from __future__ import annotations

import json
from pathlib import Path

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

TG2_FOLD_RESULTS_PATH = (
    REPORTS_DIR
    / "phase_31_tg2_nested_fold_results.csv"
)


# ------------------------------------------------------------
# 1. Recover one fixed challenger recipe from TG2
# ------------------------------------------------------------

tg2_results = pd.read_csv(
    TG2_FOLD_RESULTS_PATH
)


parameter_counts = (
    tg2_results[
        "best_params"
    ]
    .value_counts()
)


top_count = int(
    parameter_counts.iloc[0]
)


top_configs = (
    parameter_counts[
        parameter_counts.eq(
            top_count
        )
    ]
    .index
    .tolist()
)


if len(top_configs) != 1:
    raise RuntimeError(
        "TG2 did not produce one unique modal "
        "hyperparameter configuration."
    )


fixed_params = json.loads(
    top_configs[0]
)


print(
    "Fixed Extra Trees parameters:"
)

print(
    json.dumps(
        fixed_params,
        indent=2,
        sort_keys=True,
    )
)


# ------------------------------------------------------------
# 2. Rebuild the same Phase 3.1 development data
# ------------------------------------------------------------

with LOCKED_SPEC_PATH.open(
    "r",
    encoding="utf-8",
) as file:
    locked_spec = json.load(
        file
    )


locked_features = (
    locked_spec[
        "feature_names"
    ]
)


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
        "X, y, and groups are not row-aligned."
    )


if X.shape[1] != 36:
    raise RuntimeError(
        "Expected 36 locked model features."
    )


# ------------------------------------------------------------
# 3. Fixed Extra Trees recipe
# ------------------------------------------------------------

prototype = ExtraTreesRegressor(
    n_estimators=300,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    **fixed_params,
)


# ------------------------------------------------------------
# 4. Helper: engine-balanced training weights
# ------------------------------------------------------------

def build_engine_balanced_weights(
    training_groups: pd.Series,
) -> np.ndarray:

    engine_row_counts = (
        training_groups
        .value_counts()
    )


    weights = (
        training_groups
        .map(
            lambda engine_id:
                1.0
                / engine_row_counts.loc[
                    engine_id
                ]
        )
        .astype(float)
    )


    # Normalize so the average row has weight 1.
    weights = (
        weights
        / weights.mean()
    )


    # Verify that every engine has approximately
    # the same total training weight.
    weight_check = pd.DataFrame(
        {
            "unit_no": (
                training_groups
                .to_numpy()
            ),

            "weight": (
                weights
                .to_numpy()
            ),
        }
    )


    engine_total_weights = (
        weight_check
        .groupby(
            "unit_no"
        )[
            "weight"
        ]
        .sum()
    )


    if not np.allclose(
        engine_total_weights.to_numpy(),
        engine_total_weights.iloc[0],
    ):
        raise RuntimeError(
            "Engine-balanced weighting failed."
        )


    return weights.to_numpy()


# ------------------------------------------------------------
# 5. Helper: equal-engine diagnostic
# ------------------------------------------------------------

def mean_engine_rmse(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    engine_ids: np.ndarray,
) -> float:

    diagnostic = pd.DataFrame(
        {
            "unit_no": engine_ids,
            "squared_error": (
                y_true
                - y_pred
            )
            ** 2,
        }
    )


    engine_mse = (
        diagnostic
        .groupby(
            "unit_no"
        )[
            "squared_error"
        ]
        .mean()
    )


    engine_rmse = np.sqrt(
        engine_mse
    )


    return float(
        engine_rmse.mean()
    )


# ------------------------------------------------------------
# 6. Same grouped CV for both training objectives
# ------------------------------------------------------------

grouped_cv = GroupKFold(
    n_splits=5
)


splits = list(
    grouped_cv.split(
        X,
        y,
        groups=groups,
    )
)


unweighted_oof = np.full(
    len(X),
    np.nan,
)

weighted_oof = np.full(
    len(X),
    np.nan,
)


fold_records = []


for (
    fold_number,
    (
        train_indices,
        validation_indices,
    ),
) in enumerate(
    splits,
    start=1,
):

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


    if not set(
        groups_train
    ).isdisjoint(
        set(
            groups_validation
        )
    ):
        raise RuntimeError(
            "Engine leakage detected."
        )


    # --------------------------------------------------------
    # Unweighted model
    # --------------------------------------------------------

    unweighted_model = clone(
        prototype
    )


    unweighted_model.fit(
        X_train,
        y_train,
    )


    unweighted_predictions = (
        unweighted_model.predict(
            X_validation
        )
    )


    unweighted_oof[
        validation_indices
    ] = unweighted_predictions


    # --------------------------------------------------------
    # Engine-balanced model
    # --------------------------------------------------------

    training_weights = (
        build_engine_balanced_weights(
            groups_train
        )
    )


    weighted_model = clone(
        prototype
    )


    weighted_model.fit(
        X_train,
        y_train,
        sample_weight=training_weights,
    )


    weighted_predictions = (
        weighted_model.predict(
            X_validation
        )
    )


    weighted_oof[
        validation_indices
    ] = weighted_predictions


    # --------------------------------------------------------
    # Fold metrics
    # --------------------------------------------------------

    unweighted_rmse = float(
        np.sqrt(
            mean_squared_error(
                y_validation,
                unweighted_predictions,
            )
        )
    )


    weighted_rmse = float(
        np.sqrt(
            mean_squared_error(
                y_validation,
                weighted_predictions,
            )
        )
    )


    fold_records.append(
        {
            "fold": fold_number,

            "unweighted_rmse": (
                unweighted_rmse
            ),

            "engine_balanced_rmse": (
                weighted_rmse
            ),

            "rmse_delta_weighted_minus_unweighted": (
                weighted_rmse
                - unweighted_rmse
            ),
        }
    )


# ------------------------------------------------------------
# 7. Verify complete OOF coverage
# ------------------------------------------------------------

if not np.isfinite(
    unweighted_oof
).all():
    raise RuntimeError(
        "Incomplete unweighted OOF predictions."
    )


if not np.isfinite(
    weighted_oof
).all():
    raise RuntimeError(
        "Incomplete weighted OOF predictions."
    )


# ------------------------------------------------------------
# 8. Final comparison
# ------------------------------------------------------------

def pooled_rmse(
    predictions: np.ndarray,
) -> float:

    return float(
        np.sqrt(
            mean_squared_error(
                y,
                predictions,
            )
        )
    )


def pooled_mae(
    predictions: np.ndarray,
) -> float:

    return float(
        mean_absolute_error(
            y,
            predictions,
        )
    )


unweighted_rmse = pooled_rmse(
    unweighted_oof
)

weighted_rmse = pooled_rmse(
    weighted_oof
)


unweighted_mae = pooled_mae(
    unweighted_oof
)

weighted_mae = pooled_mae(
    weighted_oof
)


unweighted_engine_rmse = (
    mean_engine_rmse(
        y.to_numpy(),
        unweighted_oof,
        groups.to_numpy(),
    )
)


weighted_engine_rmse = (
    mean_engine_rmse(
        y.to_numpy(),
        weighted_oof,
        groups.to_numpy(),
    )
)


fold_results = pd.DataFrame(
    fold_records
)


summary = pd.DataFrame(
    [
        {
            "training_objective": (
                "unweighted_rows"
            ),

            "pooled_oof_rmse": (
                unweighted_rmse
            ),

            "pooled_oof_mae": (
                unweighted_mae
            ),

            "mean_engine_rmse": (
                unweighted_engine_rmse
            ),

            "mean_fold_rmse": (
                fold_results[
                    "unweighted_rmse"
                ].mean()
            ),

            "std_fold_rmse": (
                fold_results[
                    "unweighted_rmse"
                ].std(
                    ddof=1
                )
            ),
        },

        {
            "training_objective": (
                "engine_balanced"
            ),

            "pooled_oof_rmse": (
                weighted_rmse
            ),

            "pooled_oof_mae": (
                weighted_mae
            ),

            "mean_engine_rmse": (
                weighted_engine_rmse
            ),

            "mean_fold_rmse": (
                fold_results[
                    "engine_balanced_rmse"
                ].mean()
            ),

            "std_fold_rmse": (
                fold_results[
                    "engine_balanced_rmse"
                ].std(
                    ddof=1
                )
            ),
        },
    ]
)


summary[
    "rmse_vs_unweighted"
] = (
    summary[
        "pooled_oof_rmse"
    ]
    - unweighted_rmse
)


# ------------------------------------------------------------
# 9. Save evidence
# ------------------------------------------------------------

summary.to_csv(
    REPORTS_DIR
    / "phase_31_tg3_weighting_summary.csv",
    index=False,
)


fold_results.to_csv(
    REPORTS_DIR
    / "phase_31_tg3_weighting_fold_results.csv",
    index=False,
)


pd.DataFrame(
    {
        "unit_no": groups.to_numpy(),
        "rul": y.to_numpy(),

        "unweighted_prediction": (
            unweighted_oof
        ),

        "engine_balanced_prediction": (
            weighted_oof
        ),
    }
).to_csv(
    REPORTS_DIR
    / "phase_31_tg3_weighting_oof_predictions.csv",
    index=False,
)


with (
    REPORTS_DIR
    / "phase_31_tg3_fixed_challenger_recipe.json"
).open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        {
            "model_family": (
                "ExtraTreesRegressor"
            ),

            "n_estimators": 300,

            "random_state": (
                RANDOM_STATE
            ),

            "source": (
                "Modal best parameter configuration "
                "from Phase 3.1 TG2 nested CV."
            ),

            "hyperparameters": (
                fixed_params
            ),
        },
        file,
        indent=2,
        sort_keys=True,
    )


print(
    "\nWeighting experiment:"
)

print(
    summary.to_string(
        index=False
    )
)