from __future__ import annotations

import json
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

from mlflow import MlflowClient
from mlflow.models import infer_signature

from sklearn.ensemble import (
    ExtraTreesRegressor,
    RandomForestRegressor,
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

CHAMPION_ALIAS = (
    "champion"
)


REPORTS_DIR = Path(
    "reports"
)


INCUMBENT_ARTIFACT_PATH = (
    REPORTS_DIR
    / "phase_16_final_fitted_model.joblib"
)

INCUMBENT_FIT_RECORD_PATH = (
    REPORTS_DIR
    / "phase_16_final_fit_record.json"
)

LOCKED_SPEC_PATH = (
    REPORTS_DIR
    / "phase_16_locked_model_spec.json"
)

PHASE31_HANDOFF_PATH = (
    REPORTS_DIR
    / "phase_31_handoff.json"
)

PROMOTION_CONTRACT_PATH = (
    REPORTS_DIR
    / "phase_32_promotion_contract.json"
)

TG2_RESULT_PATH = (
    REPORTS_DIR
    / "phase_32_tg2_gate_results.json"
)


# ------------------------------------------------------------
# 1. Require source artifacts
# ------------------------------------------------------------

required_paths = [
    INCUMBENT_ARTIFACT_PATH,
    INCUMBENT_FIT_RECORD_PATH,
    LOCKED_SPEC_PATH,
    PHASE31_HANDOFF_PATH,
    PROMOTION_CONTRACT_PATH,
]


for path in required_paths:

    if not path.exists():

        raise FileNotFoundError(
            f"Missing required file: {path}"
        )


# ------------------------------------------------------------
# 2. Load source-of-truth records
# ------------------------------------------------------------

with LOCKED_SPEC_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    locked_spec = json.load(
        file
    )


with PHASE31_HANDOFF_PATH.open(
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
# 3. Connect to MLflow
# ------------------------------------------------------------

mlflow.set_tracking_uri(
    TRACKING_URI
)


mlflow.set_experiment(
    EXPERIMENT_NAME
)


client = MlflowClient()


# ------------------------------------------------------------
# 4. Find exactly one pending candidate version
# ------------------------------------------------------------

versions = (
    client.search_model_versions(
        filter_string=(
            f"name='{REGISTERED_MODEL_NAME}'"
        )
    )
)


pending_candidates = []


for version in versions:

    full_version = (
        client.get_model_version(
            name=REGISTERED_MODEL_NAME,
            version=version.version,
        )
    )


    tags = (
        full_version.tags
        or {}
    )


    if (
        tags.get(
            "lifecycle_role"
        )
        == "candidate"
        and
        tags.get(
            "validation_status"
        )
        == "pending"
    ):

        pending_candidates.append(
            full_version
        )


if len(
    pending_candidates
) != 1:

    raise RuntimeError(
        "Expected exactly one pending "
        "candidate model version, "
        f"found {len(pending_candidates)}."
    )


candidate_version = (
    pending_candidates[0]
)


print(
    "Pending candidate version:",
    candidate_version.version,
)


# ------------------------------------------------------------
# 5. Candidate identity gate
# ------------------------------------------------------------

candidate_uri = (
    f"models:/"
    f"{REGISTERED_MODEL_NAME}/"
    f"{candidate_version.version}"
)


candidate_model = (
    mlflow.sklearn.load_model(
        candidate_uri
    )
)


if not isinstance(
    candidate_model,
    ExtraTreesRegressor,
):

    raise RuntimeError(
        "Candidate identity gate failed: "
        "registered model is not "
        "ExtraTreesRegressor."
    )


expected_candidate_params = {
    "n_estimators": 300,
    "max_depth": 20,
    "max_features": "sqrt",
    "min_samples_leaf": 2,
    "min_samples_split": 5,
}


candidate_params = (
    candidate_model.get_params(
        deep=False
    )
)


for (
    parameter_name,
    expected_value,
) in expected_candidate_params.items():

    actual_value = (
        candidate_params[
            parameter_name
        ]
    )


    if actual_value != expected_value:

        raise RuntimeError(
            "Candidate identity gate failed: "
            f"{parameter_name} expected "
            f"{expected_value!r}, "
            f"received {actual_value!r}."
        )


if (
    candidate_model.n_features_in_
    != 36
):

    raise RuntimeError(
        "Candidate identity gate failed: "
        "expected 36 input features."
    )


candidate_identity_passed = True


# ------------------------------------------------------------
# 6. Predictive-performance gate
# ------------------------------------------------------------

incumbent_rmse = float(
    handoff[
        "incumbent"
    ][
        "reference_pooled_oof_rmse"
    ]
)


candidate_rmse = float(
    handoff[
        "challenger"
    ][
        "reference_pooled_oof_rmse"
    ]
)


rmse_delta = (
    candidate_rmse
    - incumbent_rmse
)


performance_passed = (
    candidate_rmse
    < incumbent_rmse
)


if not performance_passed:

    raise RuntimeError(
        "Predictive-performance gate failed: "
        f"candidate RMSE {candidate_rmse} "
        "did not beat incumbent RMSE "
        f"{incumbent_rmse}."
    )


# ------------------------------------------------------------
# 7. Load historical incumbent artifact
# ------------------------------------------------------------

incumbent_model = (
    joblib.load(
        INCUMBENT_ARTIFACT_PATH
    )
)


if not isinstance(
    incumbent_model,
    RandomForestRegressor,
):

    raise RuntimeError(
        "Historical incumbent artifact is not "
        "RandomForestRegressor."
    )


if (
    incumbent_model.n_features_in_
    != 36
):

    raise RuntimeError(
        "Historical incumbent does not expect "
        "36 model features."
    )


# ------------------------------------------------------------
# 8. Build realistic input example for incumbent
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


X_dev = X_dev.loc[
    :,
    locked_features,
].copy()


input_example = (
    X_dev
    .head(5)
    .copy()
)


incumbent_example_predictions = (
    incumbent_model.predict(
        input_example
    )
)


incumbent_signature = (
    infer_signature(
        input_example,
        incumbent_example_predictions,
    )
)


# ------------------------------------------------------------
# 9. Check whether champion already exists
# ------------------------------------------------------------

incumbent_registry_version = None


try:

    existing_champion = (
        client.get_model_version_by_alias(
            name=REGISTERED_MODEL_NAME,
            alias=CHAMPION_ALIAS,
        )
    )


except Exception:

    existing_champion = None


if existing_champion is not None:

    existing_champion_model = (
        mlflow.sklearn.load_model(
            (
                f"models:/"
                f"{REGISTERED_MODEL_NAME}"
                f"@{CHAMPION_ALIAS}"
            )
        )
    )


    if not isinstance(
        existing_champion_model,
        RandomForestRegressor,
    ):

        raise RuntimeError(
            "A champion alias already exists, "
            "but it does not point to the "
            "Random Forest incumbent."
        )


    incumbent_registry_version = (
        existing_champion
    )


    print(
        "Existing Random Forest champion found. "
        "Reusing version:",
        incumbent_registry_version.version,
    )


# ------------------------------------------------------------
# 10. Bootstrap incumbent into registry if necessary
# ------------------------------------------------------------

if incumbent_registry_version is None:

    incumbent_params = (
        incumbent_model.get_params(
            deep=False
        )
    )


    with mlflow.start_run(
        run_name=(
            "random-forest-incumbent-bootstrap"
        )
    ) as run:

        incumbent_run_id = (
            run.info.run_id
        )


        mlflow.log_params(
            {
                "model_family": (
                    "RandomForestRegressor"
                ),

                "feature_count": 36,

                "lifecycle_role": (
                    "incumbent"
                ),

                "bootstrap_import": True,

                "original_training_run_recreated": (
                    False
                ),

                **{
                    f"model_{key}": value
                    for (
                        key,
                        value,
                    ) in incumbent_params.items()
                },
            }
        )


        mlflow.log_metrics(
            {
                "reference_pooled_oof_rmse": (
                    incumbent_rmse
                ),

                "reference_pooled_oof_mae": float(
                    handoff[
                        "incumbent"
                    ][
                        "reference_pooled_oof_mae"
                    ]
                ),
            }
        )


        mlflow.set_tags(
            {
                "phase": "3.2",

                "lifecycle_role": (
                    "incumbent_bootstrap"
                ),

                "bootstrap_import": (
                    "true"
                ),

                "historical_training_run": (
                    "not_recreated"
                ),

                "dataset": (
                    "NASA C-MAPSS FD001"
                ),
            }
        )


        mlflow.log_artifact(
            str(
                INCUMBENT_FIT_RECORD_PATH
            ),
            artifact_path=(
                "historical_provenance"
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
                PROMOTION_CONTRACT_PATH
            ),
            artifact_path=(
                "governance"
            ),
        )


        mlflow.sklearn.log_model(
            sk_model=incumbent_model,

            name=(
                "incumbent_model"
            ),

            signature=(
                incumbent_signature
            ),

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

                "registry_import_type": (
                    "historical_incumbent_bootstrap"
                ),

                "feature_count": 36,
            },
        )


    # --------------------------------------------------------
    # Find version created by this bootstrap run
    # --------------------------------------------------------

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
        if version.run_id
        == incumbent_run_id
    ]


    if len(
        matching_versions
    ) != 1:

        raise RuntimeError(
            "Expected exactly one incumbent "
            "model version from bootstrap run."
        )


    incumbent_registry_version = (
        matching_versions[0]
    )


    # --------------------------------------------------------
    # Tag historical incumbent version
    # --------------------------------------------------------

    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=(
            incumbent_registry_version.version
        ),
        key="validation_status",
        value="passed",
    )


    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=(
            incumbent_registry_version.version
        ),
        key="lifecycle_role",
        value="incumbent",
    )


    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=(
            incumbent_registry_version.version
        ),
        key="registry_import_type",
        value="historical_bootstrap",
    )


    # --------------------------------------------------------
    # Establish the real current champion
    # --------------------------------------------------------

    client.set_registered_model_alias(
        name=REGISTERED_MODEL_NAME,
        alias=CHAMPION_ALIAS,
        version=(
            incumbent_registry_version.version
        ),
    )


# ------------------------------------------------------------
# 11. Verify champion alias
# ------------------------------------------------------------

champion_version = (
    client.get_model_version_by_alias(
        name=REGISTERED_MODEL_NAME,
        alias=CHAMPION_ALIAS,
    )
)


if (
    champion_version.version
    != incumbent_registry_version.version
):

    raise RuntimeError(
        "Champion alias does not point to "
        "incumbent registry version."
    )


champion_model = (
    mlflow.sklearn.load_model(
        (
            f"models:/"
            f"{REGISTERED_MODEL_NAME}"
            f"@{CHAMPION_ALIAS}"
        )
    )
)


if not isinstance(
    champion_model,
    RandomForestRegressor,
):

    raise RuntimeError(
        "Champion alias did not load the "
        "Random Forest incumbent."
    )


# ------------------------------------------------------------
# 12. Record passed candidate gates
# ------------------------------------------------------------

client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=candidate_version.version,
    key="gate_candidate_identity",
    value="passed",
)


client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=candidate_version.version,
    key="gate_predictive_performance",
    value="passed",
)


# IMPORTANT:
# Overall validation remains pending.
client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=candidate_version.version,
    key="validation_status",
    value="pending",
)


# ------------------------------------------------------------
# 13. Save machine-readable TG2 gate record
# ------------------------------------------------------------

result = {
    "registered_model": (
        REGISTERED_MODEL_NAME
    ),

    "champion": {
        "version": (
            incumbent_registry_version.version
        ),

        "model_family": (
            "RandomForestRegressor"
        ),

        "alias": (
            CHAMPION_ALIAS
        ),

        "registry_import_type": (
            "historical_bootstrap"
        ),
    },

    "candidate": {
        "version": (
            candidate_version.version
        ),

        "model_family": (
            "ExtraTreesRegressor"
        ),

        "validation_status": (
            "pending"
        ),
    },

    "gates": {
        "candidate_identity": {
            "passed": (
                candidate_identity_passed
            ),
        },

        "predictive_performance": {
            "passed": (
                performance_passed
            ),

            "incumbent_reference_rmse": (
                incumbent_rmse
            ),

            "candidate_reference_rmse": (
                candidate_rmse
            ),

            "challenger_minus_incumbent_rmse": (
                rmse_delta
            ),
        },
    },

    "promotion_performed": False,
}


with TG2_RESULT_PATH.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        result,
        file,
        indent=2,
        sort_keys=True,
    )


# ------------------------------------------------------------
# 14. Human-readable output
# ------------------------------------------------------------

print(
    "\nPhase 3.2 TG2 complete."
)


print(
    "\nChampion version:",
    incumbent_registry_version.version,
)


print(
    "Champion model:",
    "RandomForestRegressor",
)


print(
    "\nCandidate version:",
    candidate_version.version,
)


print(
    "Candidate model:",
    "ExtraTreesRegressor",
)


print(
    "\nCandidate identity gate:",
    "PASSED",
)


print(
    "Predictive-performance gate:",
    "PASSED",
)


print(
    "\nIncumbent reference RMSE:",
    round(
        incumbent_rmse,
        6,
    ),
)


print(
    "Candidate reference RMSE:",
    round(
        candidate_rmse,
        6,
    ),
)


print(
    "RMSE delta:",
    round(
        rmse_delta,
        6,
    ),
)


print(
    "\nCandidate validation status:",
    "pending",
)


print(
    "Promotion performed:",
    False,
)


print(
    "\nCreated:",
    TG2_RESULT_PATH,
)