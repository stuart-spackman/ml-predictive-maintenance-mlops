from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import mlflow
import mlflow.sklearn
import numpy as np

from mlflow import MlflowClient
from sklearn.ensemble import ExtraTreesRegressor

from predictive_maintenance.data.cmapss import (
    load_cmapss_subset,
)

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)

from predictive_maintenance.inference.artifacts import (
    LoadedModelArtifacts,
)

from predictive_maintenance.inference.pipeline import (
    RULInferencePipeline,
)

from predictive_maintenance.inference.schema import (
    REQUIRED_RAW_HISTORY_COLUMNS,
)

from predictive_maintenance.config import (
    DATASET_NAME,
)

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

TRACKING_URI = (
    "http://127.0.0.1:5000"
)

REGISTERED_MODEL_NAME = (
    "fd001-rul"
)


REPORTS_DIR = Path(
    "reports"
)


LOCKED_SPEC_PATH = (
    REPORTS_DIR
    / "phase_16_locked_model_spec.json"
)

TG2_RESULT_PATH = (
    REPORTS_DIR
    / "phase_32_tg2_gate_results.json"
)

TG3_RESULT_PATH = (
    REPORTS_DIR
    / "phase_32_tg3_compatibility_results.json"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def sha256_file(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        for chunk in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):

            digest.update(
                chunk
            )

    return digest.hexdigest()


# ------------------------------------------------------------
# 1. Require source records
# ------------------------------------------------------------

for path in [
    LOCKED_SPEC_PATH,
    TG2_RESULT_PATH,
]:

    if not path.exists():

        raise FileNotFoundError(
            f"Missing required file: {path}"
        )


# ------------------------------------------------------------
# 2. Load locked contract and TG2 state
# ------------------------------------------------------------

with LOCKED_SPEC_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    locked_spec = json.load(
        file
    )


with TG2_RESULT_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    tg2_result = json.load(
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


candidate_version = str(
    tg2_result[
        "candidate"
    ][
        "version"
    ]
)


# ------------------------------------------------------------
# 3. Connect to MLflow
# ------------------------------------------------------------

mlflow.set_tracking_uri(
    TRACKING_URI
)


client = MlflowClient()


candidate_uri = (
    f"models:/"
    f"{REGISTERED_MODEL_NAME}/"
    f"{candidate_version}"
)


# ------------------------------------------------------------
# 4. Load the ACTUAL registered candidate
# ------------------------------------------------------------

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
        "Registered candidate is not "
        "ExtraTreesRegressor."
    )


# ------------------------------------------------------------
# 5. Artifact / feature-schema gate
# ------------------------------------------------------------

if (
    candidate_model.n_features_in_
    != 36
):

    raise RuntimeError(
        "Candidate does not expect "
        "exactly 36 features."
    )


if not hasattr(
    candidate_model,
    "feature_names_in_",
):

    raise RuntimeError(
        "Candidate does not expose "
        "feature_names_in_."
    )


candidate_feature_names = list(
    candidate_model.feature_names_in_
)


if (
    candidate_feature_names
    != locked_features
):

    raise RuntimeError(
        "Candidate feature names/order "
        "do not match locked specification."
    )


artifact_feature_gate_passed = True


# ------------------------------------------------------------
# 6. Build compatibility-only artifact bundle
# ------------------------------------------------------------

candidate_artifacts = (
    LoadedModelArtifacts(
        locked_spec=locked_spec,

        final_fit_record={
            "source": (
                "mlflow_registry"
            ),

            "registered_model": (
                REGISTERED_MODEL_NAME
            ),

            "model_version": (
                candidate_version
            ),

            "purpose": (
                "phase32_compatibility_validation"
            ),
        },

        model=candidate_model,

        locked_spec_sha256=(
            sha256_file(
                LOCKED_SPEC_PATH
            )
        ),

        # This compatibility bundle does not load
        # the candidate from the historical joblib
        # artifact path, so we deliberately do not
        # pretend this value is a joblib SHA-256.
        model_sha256=(
            "mlflow-registry-managed-"
            f"version-{candidate_version}"
        ),
    )
)


candidate_pipeline = (
    RULInferencePipeline(
        artifacts=candidate_artifacts
    )
)


# ------------------------------------------------------------
# 7. Obtain realistic raw engine history
# ------------------------------------------------------------

train_df, _, _ = (
    load_cmapss_subset(
        DATASET_NAME
    )
)


engine_id = int(
    train_df[
        GROUP_COLUMN
    ].iloc[0]
)


engine_history = (
    train_df
    .loc[
        train_df[
            GROUP_COLUMN
        ]
        == engine_id,
        list(
            REQUIRED_RAW_HISTORY_COLUMNS
        ),
    ]
    .head(20)
    .copy()
)


if len(
    engine_history
) != 20:

    raise RuntimeError(
        "Could not construct expected "
        "20-cycle raw engine history."
    )


# ------------------------------------------------------------
# 8. Prove raw-history → locked model input
# ------------------------------------------------------------

model_input = (
    candidate_pipeline
    .build_model_input(
        engine_history
    )
)


if (
    model_input.shape
    != (1, 36)
):

    raise RuntimeError(
        "Candidate pipeline produced "
        "unexpected model-input shape: "
        f"{model_input.shape}"
    )


if (
    list(
        model_input.columns
    )
    != locked_features
):

    raise RuntimeError(
        "Candidate pipeline model-input "
        "feature order does not match "
        "locked specification."
    )


# ------------------------------------------------------------
# 9. End-to-end candidate inference
# ------------------------------------------------------------

first_result = (
    candidate_pipeline.predict(
        engine_history
    )
)


second_result = (
    candidate_pipeline.predict(
        engine_history
    )
)


if not math.isfinite(
    first_result.predicted_rul
):

    raise RuntimeError(
        "Candidate produced a non-finite "
        "RUL prediction."
    )


if not np.isclose(
    first_result.predicted_rul,
    second_result.predicted_rul,
):

    raise RuntimeError(
        "Candidate inference was not "
        "deterministic."
    )


# ------------------------------------------------------------
# 10. Direct model and pipeline must agree
# ------------------------------------------------------------

direct_prediction = float(
    candidate_model.predict(
        model_input
    )[0]
)


if not np.isclose(
    first_result.predicted_rul,
    direct_prediction,
):

    raise RuntimeError(
        "Pipeline prediction does not match "
        "direct candidate-model prediction."
    )


serving_inference_gate_passed = True


# ------------------------------------------------------------
# 11. Run existing software quality gate
# ------------------------------------------------------------

pytest_command = [
    sys.executable,
    "-m",
    "pytest",
    "--cov=predictive_maintenance",
    "--cov-report=term-missing",
    "-q",
]


pytest_result = (
    subprocess.run(
        pytest_command,
        check=False,
    )
)


if (
    pytest_result.returncode
    != 0
):

    raise RuntimeError(
        "Existing pytest quality gate failed. "
        "Candidate remains pending."
    )


# ------------------------------------------------------------
# 12. Verify installed dependency consistency
# ------------------------------------------------------------

pip_check_result = (
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "check",
        ],
        check=False,
    )
)


if (
    pip_check_result.returncode
    != 0
):

    raise RuntimeError(
        "pip check failed. "
        "Candidate remains pending."
    )


software_quality_gate_passed = True


# ------------------------------------------------------------
# 13. Record passed gates in MLflow
# ------------------------------------------------------------

client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=candidate_version,
    key=(
        "gate_artifact_feature_compatibility"
    ),
    value="passed",
)


client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=candidate_version,
    key=(
        "gate_serving_software_compatibility"
    ),
    value="passed",
)


# Do NOT mark overall validation passed yet.
client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=candidate_version,
    key="validation_status",
    value="pending",
)


# ------------------------------------------------------------
# 14. Save Git-trackable evidence
# ------------------------------------------------------------

result = {
    "registered_model": (
        REGISTERED_MODEL_NAME
    ),

    "candidate_version": (
        candidate_version
    ),

    "candidate_model_uri": (
        candidate_uri
    ),

    "gates": {
        "artifact_feature_compatibility": {
            "passed": (
                artifact_feature_gate_passed
            ),

            "feature_count": 36,

            "feature_names_and_order_match": (
                True
            ),
        },

        "serving_inference_compatibility": {
            "passed": (
                serving_inference_gate_passed
            ),

            "raw_history_cycles": (
                len(
                    engine_history
                )
            ),

            "model_input_shape": (
                list(
                    model_input.shape
                )
            ),

            "prediction_finite": (
                True
            ),

            "prediction_deterministic": (
                True
            ),

            "pipeline_matches_direct_model": (
                True
            ),
        },

        "software_quality": {
            "passed": (
                software_quality_gate_passed
            ),

            "pytest_return_code": (
                pytest_result.returncode
            ),

            "pip_check_return_code": (
                pip_check_result.returncode
            ),
        },
    },

    "validation_status": (
        "pending"
    ),

    "promotion_performed": (
        False
    ),
}


with TG3_RESULT_PATH.open(
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
# 15. Human-readable result
# ------------------------------------------------------------

print(
    "\nPhase 3.2 TG3 complete."
)


print(
    "\nCandidate version:",
    candidate_version,
)


print(
    "Candidate URI:",
    candidate_uri,
)


print(
    "\nArtifact / feature gate:",
    "PASSED",
)


print(
    "Serving / inference gate:",
    "PASSED",
)


print(
    "Software-quality gate:",
    "PASSED",
)


print(
    "\nModel input shape:",
    model_input.shape,
)


print(
    "Candidate prediction:",
    round(
        first_result.predicted_rul,
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
    TG3_RESULT_PATH,
)