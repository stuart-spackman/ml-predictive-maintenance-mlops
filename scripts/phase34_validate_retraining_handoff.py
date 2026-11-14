from __future__ import annotations

import hashlib
import json
from pathlib import Path

from predictive_maintenance.retraining.handoff import (
    build_retraining_handoff,
)


MODEL_PATH = Path(
    "reports/phase_16_final_fitted_model.joblib"
)


SPEC_PATH = Path(
    "reports/phase_16_locked_model_spec.json"
)


TG2_PATH = Path(
    "reports/phase_34_tg2_retraining_decision_validation.json"
)


POLICY_PATH = Path(
    "reports/phase_34_retraining_execution_policy.json"
)


REPORT_PATH = Path(
    "reports/phase_34_tg3_retraining_handoff.json"
)


EXPECTED_MODEL_SHA256 = (
    "bb5825d198d6eda27d1e720e67837a469ac7d126dfdd2e832bd9b5374514596b"
)


EXPECTED_SPEC_SHA256 = (
    "34cdf9c7b844f71dba555b0bdc6206ee849eee7e5634e2ee4a8d6d4ed99f4c8e"
)


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


def load_json(
    path: Path,
) -> dict:

    if not path.exists():

        raise FileNotFoundError(
            f"Missing required artifact: {path}"
        )


    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


# ------------------------------------------------------------
# 1. Verify incumbent identity before handoff
# ------------------------------------------------------------

model_sha_before = (
    sha256_file(
        MODEL_PATH
    )
)


spec_sha_before = (
    sha256_file(
        SPEC_PATH
    )
)


if (
    model_sha_before
    != EXPECTED_MODEL_SHA256
):

    raise RuntimeError(
        "Incumbent fitted-model artifact "
        "does not match expected identity."
    )


if (
    spec_sha_before
    != EXPECTED_SPEC_SHA256
):

    raise RuntimeError(
        "Incumbent locked specification "
        "does not match expected identity."
    )


# ------------------------------------------------------------
# 2. Load TG2 synthetic workflow validation
# ------------------------------------------------------------

tg2 = (
    load_json(
        TG2_PATH
    )
)


policy = (
    load_json(
        POLICY_PATH
    )
)


eligible_scenario = (
    tg2[
        "scenarios"
    ][
        "eligible_to_retrain"
    ]
)


if (
    eligible_scenario[
        "status"
    ]
    != "eligible_to_retrain"
):

    raise RuntimeError(
        "TG2 did not validate the "
        "eligible-to-retrain branch."
    )


# ------------------------------------------------------------
# 3. Apply project-reality boundary
# ------------------------------------------------------------

real_data_available = bool(
    policy[
        "project_reality"
    ][
        "genuine_new_labeled_production_data_available"
    ]
)


handoff = (
    build_retraining_handoff(
        performance_decision=(
            eligible_scenario
        ),

        incumbent_model_sha256=(
            model_sha_before
        ),

        incumbent_spec_sha256=(
            spec_sha_before
        ),

        real_new_labeled_data_available=(
            real_data_available
        ),
    )
)


# ------------------------------------------------------------
# 4. Verify incumbent is unchanged after workflow
# ------------------------------------------------------------

model_sha_after = (
    sha256_file(
        MODEL_PATH
    )
)


spec_sha_after = (
    sha256_file(
        SPEC_PATH
    )
)


incumbent_unchanged = (
    model_sha_before
    == model_sha_after
    and
    spec_sha_before
    == spec_sha_after
)


if not incumbent_unchanged:

    raise RuntimeError(
        "Incumbent identity changed during "
        "the retraining-handoff simulation."
    )


# ------------------------------------------------------------
# 5. Validate safe project result
# ------------------------------------------------------------

expected_status = (
    "workflow_validated_but_real_fit_blocked"
)


if (
    handoff[
        "status"
    ]
    != expected_status
):

    raise RuntimeError(
        "Portfolio project should block "
        "a real production retraining claim "
        "because genuine newly labeled "
        "production data is unavailable."
    )


if (
    handoff[
        "registry_action"
    ]
    != "none"
):

    raise RuntimeError(
        "Retraining handoff unexpectedly "
        "changed registry state."
    )


if (
    handoff[
        "deployment_action"
    ]
    != "none"
):

    raise RuntimeError(
        "Retraining handoff unexpectedly "
        "changed deployment state."
    )


# ------------------------------------------------------------
# 6. Evidence report
# ------------------------------------------------------------

report = {
    "phase": "3.4",
    "task_group": "TG3",

    "validation": (
        "passed"
    ),

    "workflow_type": (
        "retraining_lifecycle_simulation"
    ),

    "project_reality": {
        "genuine_new_labeled_production_data_available": (
            real_data_available
        ),

        "actual_new_challenger_fit": (
            False
        ),

        "reason": (
            "The project does not possess genuine "
            "newly labeled production observations."
        ),
    },

    "incumbent": {
        "model_path": (
            str(
                MODEL_PATH
            )
        ),

        "model_sha256_before": (
            model_sha_before
        ),

        "model_sha256_after": (
            model_sha_after
        ),

        "locked_spec_path": (
            str(
                SPEC_PATH
            )
        ),

        "locked_spec_sha256_before": (
            spec_sha_before
        ),

        "locked_spec_sha256_after": (
            spec_sha_after
        ),

        "unchanged": (
            incumbent_unchanged
        ),
    },

    "synthetic_decision_branch": (
        eligible_scenario
    ),

    "retraining_handoff": (
        handoff
    ),

    "safety_boundaries": {
        "incumbent_mutated": (
            False
        ),

        "registry_alias_moved": (
            False
        ),

        "serving_cutover_performed": (
            False
        ),

        "real_production_retraining_claimed": (
            False
        ),

        "promotion_still_required_after_future_real_fit": (
            True
        ),
    },

    "future_real_retraining_sequence": [
        "obtain representative trustworthy labeled production data",
        "construct leakage-safe grouped training population",
        "fit a separate challenger artifact",
        "estimate challenger performance using grouped evaluation",
        "validate feature and serving compatibility",
        "record provenance",
        "run promotion gates",
        "make a separate deployment decision"
    ]
}


REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print(
    "\nPhase 3.4 TG3 retraining handoff "
    "validation: PASSED"
)


print(
    "\nTG2 eligible branch:",
    eligible_scenario[
        "status"
    ]
)


print(
    "Real newly labeled production data:",
    real_data_available
)


print(
    "Actual challenger fit:",
    False
)


print(
    "Handoff status:",
    handoff[
        "status"
    ]
)


print(
    "Incumbent unchanged:",
    incumbent_unchanged
)


print(
    "Registry action:",
    handoff[
        "registry_action"
    ]
)


print(
    "Deployment action:",
    handoff[
        "deployment_action"
    ]
)


print(
    "\nCreated:",
    REPORT_PATH
)