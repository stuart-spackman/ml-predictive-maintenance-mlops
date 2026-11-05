from __future__ import annotations

import json
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd

from mlflow import MlflowClient
from mlflow.models import infer_signature

from sklearn.ensemble import (
    ExtraTreesRegressor,
)

from predictive_maintenance.config import (
    RANDOM_STATE,
)

from predictive_maintenance.data.modeling import (
    build_fd001_modeling_data,
)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

TRACKING_URI = (
    "http://127.0.0.1:5000"
)

EXPERIMENT_NAME = (
    "phase-32-model-promotion"
)

REGISTERED_MODEL_NAME = (
    "fd001-rul"
)


REPORTS_DIR = Path(
    "reports"
)


HANDOFF_PATH = (
    REPORTS_DIR
    / "phase_31_handoff.json"
)

PROMOTION_CONTRACT_PATH = (
    REPORTS_DIR
    / "phase_32_promotion_contract.json"
)

LOCKED_SPEC_PATH = (
    REPORTS_DIR
    / "phase_16_locked_model_spec.json"
)

CHALLENGER_RECIPE_PATH = (
    REPORTS_DIR
    / "phase_31_tg3_fixed_challenger_recipe.json"
)


# ------------------------------------------------------------
# 1. Require source-of-truth handoff files
# ------------------------------------------------------------

required_paths = [
    HANDOFF_PATH,
    PROMOTION_CONTRACT_PATH,
    LOCKED_SPEC_PATH,
    CHALLENGER_RECIPE_PATH,
]


for path in required_paths:

    if not path.exists():

        raise FileNotFoundError(
            f"Missing required file: {path}"
        )


# ------------------------------------------------------------
# 2. Load Phase 3.1 / Phase 3.2 contracts
# ------------------------------------------------------------

with HANDOFF_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    handoff = json.load(
        file
    )


with PROMOTION_CONTRACT_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    promotion_contract = json.load(
        file
    )


with LOCKED_SPEC_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    locked_spec = json.load(
        file
    )


with CHALLENGER_RECIPE_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    challenger_recipe = json.load(
        file
    )


# ------------------------------------------------------------
# 3. Validate frozen candidate identity
# ------------------------------------------------------------

expected_params = {
    "max_depth": 20,
    "max_features": "sqrt",
    "min_samples_leaf": 2,
    "min_samples_split": 5,
}


if (
    challenger_recipe[
        "model_family"
    ]
    != "ExtraTreesRegressor"
):

    raise RuntimeError(
        "Unexpected challenger model family."
    )


if (
    challenger_recipe[
        "n_estimators"
    ]
    != 300
):

    raise RuntimeError(
        "Unexpected challenger n_estimators."
    )


if (
    challenger_recipe[
        "hyperparameters"
    ]
    != expected_params
):

    raise RuntimeError(
        "Frozen challenger hyperparameters "
        "do not match Phase 3.1 handoff."
    )


locked_features = list(
    locked_spec[
        "feature_names"
    ]
)


if len(
    locked_features
) != 36:

    raise RuntimeError(
        "Expected exactly 36 locked features."
    )


# ------------------------------------------------------------
# 4. Rebuild full development population
# ------------------------------------------------------------

modeling_data = (
    build_fd001_modeling_data()
)


X_dev = pd.concat(
    [
        modeling_data.X_train_temporal,
        modeling_data.X_validation_temporal,
    ],
    ignore_index=True,
)


y_dev = pd.concat(
    [
        modeling_data.y_train,
        modeling_data.y_validation,
    ],
    ignore_index=True,
)


groups_dev = pd.concat(
    [
        modeling_data.groups_train,
        modeling_data.groups_validation,
    ],
    ignore_index=True,
)


X_dev = X_dev.loc[
    :,
    locked_features,
].copy()


if not (
    len(X_dev)
    == len(y_dev)
    == len(groups_dev)
):

    raise RuntimeError(
        "Development X, y, and groups "
        "are not row-aligned."
    )


if (
    groups_dev.nunique()
    != 100
):

    raise RuntimeError(
        "Expected 100 development engines."
    )


# ------------------------------------------------------------
# 5. Construct exact frozen candidate
# ------------------------------------------------------------

candidate = ExtraTreesRegressor(
    n_estimators=300,
    max_depth=20,
    max_features="sqrt",
    min_samples_leaf=2,
    min_samples_split=5,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)


# ------------------------------------------------------------
# 6. Fit on all development engines
# ------------------------------------------------------------

candidate.fit(
    X_dev,
    y_dev,
)


if (
    candidate.n_features_in_
    != 36
):

    raise RuntimeError(
        "Candidate fitted with unexpected "
        "feature count."
    )


# ------------------------------------------------------------
# 7. Infer MLflow model signature
# ------------------------------------------------------------

input_example = (
    X_dev
    .head(5)
    .copy()
)


example_predictions = (
    candidate.predict(
        input_example
    )
)


signature = infer_signature(
    input_example,
    example_predictions,
)


# ------------------------------------------------------------
# 8. Recover Phase 3.1 reference evidence
# ------------------------------------------------------------

challenger_metrics = handoff[
    "challenger"
]


incumbent_metrics = handoff[
    "incumbent"
]


comparison = handoff[
    "comparison"
]


reference_metrics = {
    "reference_pooled_oof_rmse": float(
        challenger_metrics[
            "reference_pooled_oof_rmse"
        ]
    ),

    "reference_pooled_oof_mae": float(
        challenger_metrics[
            "reference_pooled_oof_mae"
        ]
    ),

    "incumbent_reference_pooled_oof_rmse": float(
        incumbent_metrics[
            "reference_pooled_oof_rmse"
        ]
    ),

    "reference_rmse_improvement_percent": float(
        comparison[
            "challenger_rmse_improvement_percent"
        ]
    ),
}


# ------------------------------------------------------------
# 9. Connect to MLflow
# ------------------------------------------------------------

mlflow.set_tracking_uri(
    TRACKING_URI
)


mlflow.set_experiment(
    EXPERIMENT_NAME
)


# ------------------------------------------------------------
# 10. Create run and log evidence
# ------------------------------------------------------------

with mlflow.start_run(
    run_name=(
        "extra-trees-phase32-candidate"
    )
) as run:

    run_id = (
        run.info.run_id
    )


    mlflow.log_params(
        {
            "model_family": (
                "ExtraTreesRegressor"
            ),

            "n_estimators": 300,

            "max_depth": 20,

            "max_features": (
                "sqrt"
            ),

            "min_samples_leaf": 2,

            "min_samples_split": 5,

            "random_state": (
                RANDOM_STATE
            ),

            "feature_count": 36,

            "training_objective": (
                "unweighted_rows"
            ),

            "development_engines": int(
                groups_dev.nunique()
            ),

            "development_rows": int(
                len(X_dev)
            ),
        }
    )


    mlflow.log_metrics(
        reference_metrics
    )


    mlflow.set_tags(
        {
            "phase": "3.2",

            "lifecycle_role": (
                "candidate"
            ),

            "source_phase": (
                "3.1"
            ),

            "dataset": (
                "NASA C-MAPSS FD001"
            ),
        }
    )


    mlflow.log_artifact(
        str(
            HANDOFF_PATH
        ),
        artifact_path=(
            "governance"
        ),
    )


    mlflow.log_artifact(
        str(
            PROMOTION_CONTRACT_PATH
        ),
        artifact_path=(
            "governance"
        ),
    )


    mlflow.log_artifact(
        str(
            LOCKED_SPEC_PATH
        ),
        artifact_path=(
            "contracts"
        ),
    )


    mlflow.log_artifact(
        str(
            CHALLENGER_RECIPE_PATH
        ),
        artifact_path=(
            "contracts"
        ),
    )


    model_info = (
        mlflow.sklearn.log_model(
            sk_model=candidate,

            name=(
                "candidate_model"
            ),

            signature=signature,

            input_example=(
                input_example
            ),

            registered_model_name=(
                REGISTERED_MODEL_NAME
            ),

            serialization_format=(
                "skops"
            ),

            skops_trusted_types=[
                "sklearn.tree._tree.Tree"
            ],

            metadata={
                "phase": "3.2",

                "candidate_status": (
                    "pending_validation"
                ),

                "feature_count": 36,
            },
        )
    )   


# ------------------------------------------------------------
# 11. Identify newly registered version
# ------------------------------------------------------------

client = MlflowClient()


versions = (
    client.search_model_versions(
        filter_string=(
            f"name='{REGISTERED_MODEL_NAME}'"
        )
    )
)


matching_versions = [
    version
    for version in versions
    if version.run_id == run_id
]


if len(
    matching_versions
) != 1:

    raise RuntimeError(
        "Expected exactly one registered "
        "model version for this MLflow run."
    )


model_version = (
    matching_versions[0]
)


# ------------------------------------------------------------
# 12. Mark candidate validation as pending
# ------------------------------------------------------------

client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=model_version.version,
    key="validation_status",
    value="pending",
)


client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=model_version.version,
    key="lifecycle_role",
    value="candidate",
)


# ------------------------------------------------------------
# 13. Human-readable result
# ------------------------------------------------------------

print(
    "\nMLflow candidate registered."
)


print(
    "Tracking URI:",
    TRACKING_URI,
)


print(
    "Experiment:",
    EXPERIMENT_NAME,
)


print(
    "Run ID:",
    run_id,
)


print(
    "Registered model:",
    REGISTERED_MODEL_NAME,
)


print(
    "Model version:",
    model_version.version,
)


print(
    "Validation status:",
    "pending",
)


print(
    "Model URI:",
    (
        f"models:/"
        f"{REGISTERED_MODEL_NAME}/"
        f"{model_version.version}"
    ),
)