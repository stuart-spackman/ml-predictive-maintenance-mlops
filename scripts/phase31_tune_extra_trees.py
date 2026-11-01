from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.ensemble import (
    ExtraTreesRegressor,
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)
from sklearn.model_selection import (
    GroupKFold,
    RandomizedSearchCV,
)

from predictive_maintenance.config import (
    RANDOM_STATE,
)
from predictive_maintenance.data.modeling import (
    build_fd001_modeling_data,
)


REPORTS_DIR = Path("reports")

LOCKED_SPEC_PATH = (
    REPORTS_DIR
    / "phase_16_locked_model_spec.json"
)

INCUMBENT_MODEL_PATH = (
    REPORTS_DIR
    / "phase_16_final_fitted_model.joblib"
)


# ------------------------------------------------------------
# 1. Rebuild the same development population
# ------------------------------------------------------------

with LOCKED_SPEC_PATH.open(
    "r",
    encoding="utf-8",
) as file:
    locked_spec = json.load(file)


locked_features = locked_spec[
    "feature_names"
]


modeling_data = (
    build_fd001_modeling_data()
)


X = pd.concat(
    [
        modeling_data.X_train_temporal,
        modeling_data.X_validation_temporal,
    ],
    ignore_index=True,
)


y = pd.concat(
    [
        modeling_data.y_train,
        modeling_data.y_validation,
    ],
    ignore_index=True,
)


groups = pd.concat(
    [
        modeling_data.groups_train,
        modeling_data.groups_validation,
    ],
    ignore_index=True,
)


X = X.loc[
    :,
    locked_features,
].copy()


if not (
    len(X)
    == len(y)
    == len(groups)
):
    raise RuntimeError(
        "X, y, and groups are not aligned."
    )


if X.shape[1] != 36:
    raise RuntimeError(
        "Expected 36 locked model features."
    )


# ------------------------------------------------------------
# 2. Recover incumbent recipe
# ------------------------------------------------------------

fitted_incumbent = joblib.load(
    INCUMBENT_MODEL_PATH
)

incumbent_prototype = clone(
    fitted_incumbent
)


# ------------------------------------------------------------
# 3. Define a deliberately small search space
# ------------------------------------------------------------

extra_trees_prototype = (
    ExtraTreesRegressor(
        n_estimators=300,
        random_state=RANDOM_STATE,

        # Avoid nested parallelism.
        n_jobs=1,
    )
)


parameter_space = {
    "max_features": [
        0.5,
        0.75,
        1.0,
        "sqrt",
    ],

    "min_samples_leaf": [
        1,
        2,
        4,
        8,
    ],

    "min_samples_split": [
        2,
        5,
        10,
    ],

    "max_depth": [
        None,
        12,
        20,
        30,
    ],
}


# ------------------------------------------------------------
# 4. Create the outer grouped folds
# ------------------------------------------------------------

outer_cv = GroupKFold(
    n_splits=5
)


outer_splits = list(
    outer_cv.split(
        X,
        y,
        groups=groups,
    )
)


incumbent_oof = np.full(
    len(X),
    np.nan,
)

challenger_oof = np.full(
    len(X),
    np.nan,
)


fold_records = []


# ------------------------------------------------------------
# 5. Nested grouped tuning
# ------------------------------------------------------------

for (
    fold_number,
    (
        train_indices,
        validation_indices,
    ),
) in enumerate(
    outer_splits,
    start=1,
):

    print(
        f"\nOuter fold {fold_number}"
    )


    X_train = X.iloc[
        train_indices
    ]

    X_validation = X.iloc[
        validation_indices
    ]


    y_train = y.iloc[
        train_indices
    ]

    y_validation = y.iloc[
        validation_indices
    ]


    groups_train = groups.iloc[
        train_indices
    ]

    groups_validation = groups.iloc[
        validation_indices
    ]


    # --------------------------------------------------------
    # Safety check: outer engine isolation
    # --------------------------------------------------------

    if not set(
        groups_train
    ).isdisjoint(
        set(
            groups_validation
        )
    ):
        raise RuntimeError(
            "Outer-fold engine leakage detected."
        )


    # --------------------------------------------------------
    # Incumbent: fit only on outer training data
    # --------------------------------------------------------

    incumbent = clone(
        incumbent_prototype
    )


    incumbent.fit(
        X_train,
        y_train,
    )


    incumbent_predictions = (
        incumbent.predict(
            X_validation
        )
    )


    incumbent_oof[
        validation_indices
    ] = incumbent_predictions


    # --------------------------------------------------------
    # Challenger: inner grouped tuning
    # --------------------------------------------------------

    inner_cv = GroupKFold(
        n_splits=3
    )


    search = RandomizedSearchCV(
        estimator=clone(
            extra_trees_prototype
        ),

        param_distributions=(
            parameter_space
        ),

        n_iter=6,

        scoring=(
            "neg_root_mean_squared_error"
        ),

        cv=inner_cv,

        random_state=RANDOM_STATE,

        # Parallelize search here rather than
        # inside every Extra Trees estimator.
        n_jobs=-1,

        refit=True,

        error_score="raise",
    )


    search.fit(
        X_train,
        y_train,
        groups=groups_train,
    )


    challenger_predictions = (
        search.predict(
            X_validation
        )
    )


    challenger_oof[
        validation_indices
    ] = challenger_predictions


    # --------------------------------------------------------
    # Outer-fold metrics
    # --------------------------------------------------------

    incumbent_rmse = float(
        np.sqrt(
            mean_squared_error(
                y_validation,
                incumbent_predictions,
            )
        )
    )


    challenger_rmse = float(
        np.sqrt(
            mean_squared_error(
                y_validation,
                challenger_predictions,
            )
        )
    )


    fold_records.append(
        {
            "fold": fold_number,

            "train_engines": (
                groups_train.nunique()
            ),

            "validation_engines": (
                groups_validation.nunique()
            ),

            "incumbent_rmse": (
                incumbent_rmse
            ),

            "challenger_rmse": (
                challenger_rmse
            ),

            "rmse_delta_challenger_minus_incumbent": (
                challenger_rmse
                - incumbent_rmse
            ),

            "inner_best_rmse": (
                -float(
                    search.best_score_
                )
            ),

            "best_params": json.dumps(
                search.best_params_,
                sort_keys=True,
            ),
        }
    )


    print(
        "Incumbent outer RMSE:",
        round(
            incumbent_rmse,
            4,
        ),
    )

    print(
        "Tuned Extra Trees outer RMSE:",
        round(
            challenger_rmse,
            4,
        ),
    )

    print(
        "Inner best params:",
        search.best_params_,
    )


# ------------------------------------------------------------
# 6. Verify complete OOF coverage
# ------------------------------------------------------------

if not np.isfinite(
    incumbent_oof
).all():
    raise RuntimeError(
        "Incomplete incumbent OOF predictions."
    )


if not np.isfinite(
    challenger_oof
).all():
    raise RuntimeError(
        "Incomplete challenger OOF predictions."
    )


# ------------------------------------------------------------
# 7. Final pooled comparison
# ------------------------------------------------------------

incumbent_pooled_rmse = float(
    np.sqrt(
        mean_squared_error(
            y,
            incumbent_oof,
        )
    )
)


challenger_pooled_rmse = float(
    np.sqrt(
        mean_squared_error(
            y,
            challenger_oof,
        )
    )
)


incumbent_pooled_mae = float(
    mean_absolute_error(
        y,
        incumbent_oof,
    )
)


challenger_pooled_mae = float(
    mean_absolute_error(
        y,
        challenger_oof,
    )
)


summary = pd.DataFrame(
    [
        {
            "model": (
                "incumbent_random_forest"
            ),
            "pooled_oof_rmse": (
                incumbent_pooled_rmse
            ),
            "pooled_oof_mae": (
                incumbent_pooled_mae
            ),
        },
        {
            "model": (
                "tuned_extra_trees"
            ),
            "pooled_oof_rmse": (
                challenger_pooled_rmse
            ),
            "pooled_oof_mae": (
                challenger_pooled_mae
            ),
        },
    ]
)


summary[
    "rmse_vs_incumbent"
] = (
    summary[
        "pooled_oof_rmse"
    ]
    - incumbent_pooled_rmse
)


fold_results = pd.DataFrame(
    fold_records
)


oof_predictions = pd.DataFrame(
    {
        "unit_no": groups.to_numpy(),
        "rul": y.to_numpy(),

        "incumbent_prediction": (
            incumbent_oof
        ),

        "tuned_extra_trees_prediction": (
            challenger_oof
        ),
    }
)


# ------------------------------------------------------------
# 8. Save evidence
# ------------------------------------------------------------

summary.to_csv(
    REPORTS_DIR
    / "phase_31_tg2_tuning_summary.csv",
    index=False,
)


fold_results.to_csv(
    REPORTS_DIR
    / "phase_31_tg2_nested_fold_results.csv",
    index=False,
)


oof_predictions.to_csv(
    REPORTS_DIR
    / "phase_31_tg2_oof_predictions.csv",
    index=False,
)


print(
    "\nFinal nested-CV comparison:"
)

print(
    summary.to_string(
        index=False
    )
)