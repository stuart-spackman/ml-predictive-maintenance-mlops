from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.ensemble import (
    ExtraTreesRegressor,
    HistGradientBoostingRegressor,
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


REPORTS_DIR = Path(
    "reports"
)

LOCKED_SPEC_PATH = (
    REPORTS_DIR
    / "phase_16_locked_model_spec.json"
)

INCUMBENT_MODEL_PATH = (
    REPORTS_DIR
    / "phase_16_final_fitted_model.joblib"
)


# ------------------------------------------------------------
# 1. Load the locked incumbent feature schema
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


# ------------------------------------------------------------
# 2. Rebuild the development data
# ------------------------------------------------------------

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


if not (
    len(X)
    == len(y)
    == len(groups)
):
    raise RuntimeError(
        "Development X, y, and groups "
        "are not row-aligned."
    )


# ------------------------------------------------------------
# 3. Enforce the locked 36-feature representation
# ------------------------------------------------------------

missing_features = sorted(
    set(locked_features)
    - set(X.columns)
)


if missing_features:
    raise RuntimeError(
        "Development feature matrix is missing "
        f"locked features: {missing_features}"
    )


X = X.loc[
    :,
    locked_features,
].copy()


if X.shape[1] != 36:
    raise RuntimeError(
        "Expected exactly 36 locked model features, "
        f"received {X.shape[1]}."
    )


print(
    "Development rows:",
    len(X),
)

print(
    "Development engines:",
    groups.nunique(),
)

print(
    "Model features:",
    X.shape[1],
)


# ------------------------------------------------------------
# 4. Recover the incumbent recipe
# ------------------------------------------------------------

fitted_incumbent = (
    joblib.load(
        INCUMBENT_MODEL_PATH
    )
)


incumbent_prototype = clone(
    fitted_incumbent
)


# ------------------------------------------------------------
# 5. Define model-family candidates
# ------------------------------------------------------------

model_prototypes = {
    "incumbent_random_forest": (
        incumbent_prototype
    ),

    "extra_trees": (
        ExtraTreesRegressor(
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    ),

    "hist_gradient_boosting": (
        HistGradientBoostingRegressor(
            random_state=RANDOM_STATE,
        )
    ),
}


# ------------------------------------------------------------
# 6. Freeze one grouped CV procedure
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


# ------------------------------------------------------------
# 7. Evaluate every model on the exact same folds
# ------------------------------------------------------------

fold_records = []

oof_output = pd.DataFrame(
    {
        "row_index": np.arange(
            len(X)
        ),
        "unit_no": groups.to_numpy(),
        "rul": y.to_numpy(),
    }
)


summary_records = []


for (
    model_name,
    prototype,
) in model_prototypes.items():

    print(
        f"\nEvaluating {model_name}..."
    )

    oof_predictions = np.full(
        len(X),
        np.nan,
        dtype=float,
    )


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

        train_groups = groups.iloc[
            train_indices
        ]

        validation_groups = groups.iloc[
            validation_indices
        ]


        if not set(
            train_groups
        ).isdisjoint(
            set(
                validation_groups
            )
        ):
            raise RuntimeError(
                "Engine leakage detected "
                f"in fold {fold_number}."
            )


        model = clone(
            prototype
        )


        model.fit(
            X_train,
            y_train,
        )


        predictions = model.predict(
            X_validation
        )


        oof_predictions[
            validation_indices
        ] = predictions


        fold_rmse = float(
            np.sqrt(
                mean_squared_error(
                    y_validation,
                    predictions,
                )
            )
        )


        fold_mae = float(
            mean_absolute_error(
                y_validation,
                predictions,
            )
        )


        fold_records.append(
            {
                "model": model_name,
                "fold": fold_number,
                "train_engines": (
                    train_groups.nunique()
                ),
                "validation_engines": (
                    validation_groups.nunique()
                ),
                "rmse": fold_rmse,
                "mae": fold_mae,
            }
        )


    if not np.isfinite(
        oof_predictions
    ).all():
        raise RuntimeError(
            f"{model_name} did not produce "
            "a prediction for every OOF row."
        )


    pooled_oof_rmse = float(
        np.sqrt(
            mean_squared_error(
                y,
                oof_predictions,
            )
        )
    )


    pooled_oof_mae = float(
        mean_absolute_error(
            y,
            oof_predictions,
        )
    )


    model_fold_records = [
        record
        for record in fold_records
        if record["model"]
        == model_name
    ]


    fold_rmses = np.array(
        [
            record["rmse"]
            for record
            in model_fold_records
        ],
        dtype=float,
    )


    summary_records.append(
        {
            "model": model_name,
            "pooled_oof_rmse": (
                pooled_oof_rmse
            ),
            "pooled_oof_mae": (
                pooled_oof_mae
            ),
            "mean_fold_rmse": float(
                fold_rmses.mean()
            ),
            "std_fold_rmse": float(
                fold_rmses.std(
                    ddof=1
                )
            ),
        }
    )


    oof_output[
        f"{model_name}_prediction"
    ] = oof_predictions


# ------------------------------------------------------------
# 8. Save evidence
# ------------------------------------------------------------

fold_metrics = pd.DataFrame(
    fold_records
)


summary = (
    pd.DataFrame(
        summary_records
    )
    .sort_values(
        "pooled_oof_rmse"
    )
    .reset_index(
        drop=True
    )
)


fold_metrics.to_csv(
    REPORTS_DIR
    / "phase_31_tg1_fold_metrics.csv",
    index=False,
)


summary.to_csv(
    REPORTS_DIR
    / "phase_31_tg1_challenger_summary.csv",
    index=False,
)


oof_output.to_csv(
    REPORTS_DIR
    / "phase_31_tg1_oof_predictions.csv",
    index=False,
)


print(
    "\nModel-family screening results:"
)

print(
    summary.to_string(
        index=False
    )
)