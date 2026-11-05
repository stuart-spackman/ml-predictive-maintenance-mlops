from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import mlflow
import mlflow.sklearn

from mlflow import MlflowClient

from sklearn.ensemble import (
    ExtraTreesRegressor,
    RandomForestRegressor,
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

CHAMPION_ALIAS = (
    "champion"
)


REPORTS_DIR = Path(
    "reports"
)


PROMOTION_CONTRACT_PATH = (
    REPORTS_DIR
    / "phase_32_promotion_contract.json"
)

PHASE31_HANDOFF_PATH = (
    REPORTS_DIR
    / "phase_31_handoff.json"
)

PHASE31_MANIFEST_PATH = (
    REPORTS_DIR
    / "phase_31_experiment_manifest.json"
)

PHASE31_LEDGER_PATH = (
    REPORTS_DIR
    / "phase_31_experiment_ledger.csv"
)

TG2_RESULT_PATH = (
    REPORTS_DIR
    / "phase_32_tg2_gate_results.json"
)

TG3_RESULT_PATH = (
    REPORTS_DIR
    / "phase_32_tg3_compatibility_results.json"
)

DECISION_PATH = (
    REPORTS_DIR
    / "phase_32_promotion_decision.json"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def load_json(
    path: Path,
) -> dict:

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
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


def git_output(
    *args: str,
) -> str:

    result = subprocess.run(
        [
            "git",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


# ------------------------------------------------------------
# 1. Require complete evidence package
# ------------------------------------------------------------

required_paths = [
    PROMOTION_CONTRACT_PATH,
    PHASE31_HANDOFF_PATH,
    PHASE31_MANIFEST_PATH,
    PHASE31_LEDGER_PATH,
    TG2_RESULT_PATH,
    TG3_RESULT_PATH,
]


for path in required_paths:

    if not path.exists():

        raise FileNotFoundError(
            f"Missing required promotion "
            f"evidence: {path}"
        )


# ------------------------------------------------------------
# 2. Load governance and gate evidence
# ------------------------------------------------------------

promotion_contract = (
    load_json(
        PROMOTION_CONTRACT_PATH
    )
)


tg2 = (
    load_json(
        TG2_RESULT_PATH
    )
)


tg3 = (
    load_json(
        TG3_RESULT_PATH
    )
)


candidate_version = str(
    tg2[
        "candidate"
    ][
        "version"
    ]
)


incumbent_version = str(
    tg2[
        "champion"
    ][
        "version"
    ]
)


if (
    str(
        tg3[
            "candidate_version"
        ]
    )
    != candidate_version
):

    raise RuntimeError(
        "TG2 and TG3 refer to different "
        "candidate model versions."
    )


# ------------------------------------------------------------
# 3. Verify promotion-contract policy
# ------------------------------------------------------------

if not (
    promotion_contract[
        "promotion_rule"
    ][
        "all_required_gates_must_pass"
    ]
):

    raise RuntimeError(
        "Promotion contract does not require "
        "all gates to pass."
    )


if not (
    promotion_contract[
        "promotion_rule"
    ][
        "promotion_changes_champion_reference"
    ]
):

    raise RuntimeError(
        "Promotion contract does not authorize "
        "champion-reference movement."
    )


if not (
    promotion_contract[
        "scope"
    ][
        "promotion_allowed_only_after_gate_evaluation"
    ]
):

    raise RuntimeError(
        "Promotion contract scope is inconsistent "
        "with Phase 3.2 governance."
    )


contract_alias = (
    promotion_contract[
        "registry_policy"
    ][
        "champion_alias"
    ]
)


if (
    contract_alias
    != CHAMPION_ALIAS
):

    raise RuntimeError(
        "Promotion contract champion alias "
        "does not match TG4 configuration."
    )


# ------------------------------------------------------------
# 4. Reconcile TG2 + TG3 gate evidence
# ------------------------------------------------------------

gate_results = {
    "candidate_identity": bool(
        tg2[
            "gates"
        ][
            "candidate_identity"
        ][
            "passed"
        ]
    ),

    "predictive_performance": bool(
        tg2[
            "gates"
        ][
            "predictive_performance"
        ][
            "passed"
        ]
    ),

    "artifact_feature_compatibility": bool(
        tg3[
            "gates"
        ][
            "artifact_feature_compatibility"
        ][
            "passed"
        ]
    ),

    "serving_inference_compatibility": bool(
        tg3[
            "gates"
        ][
            "serving_inference_compatibility"
        ][
            "passed"
        ]
    ),

    "software_quality": bool(
        tg3[
            "gates"
        ][
            "software_quality"
        ][
            "passed"
        ]
    ),
}


all_prior_gates_passed = all(
    gate_results.values()
)


# ------------------------------------------------------------
# 5. Connect to MLflow
# ------------------------------------------------------------

mlflow.set_tracking_uri(
    TRACKING_URI
)


client = MlflowClient()


candidate_version_info = (
    client.get_model_version(
        name=REGISTERED_MODEL_NAME,
        version=candidate_version,
    )
)


incumbent_version_info = (
    client.get_model_version(
        name=REGISTERED_MODEL_NAME,
        version=incumbent_version,
    )
)


# ------------------------------------------------------------
# 6. Verify candidate registry state
# ------------------------------------------------------------

candidate_tags = (
    candidate_version_info.tags
    or {}
)


expected_candidate_tags = {
    "gate_candidate_identity": (
        "passed"
    ),

    "gate_predictive_performance": (
        "passed"
    ),

    "gate_artifact_feature_compatibility": (
        "passed"
    ),

    "gate_serving_software_compatibility": (
        "passed"
    ),
}


for (
    key,
    expected_value,
) in expected_candidate_tags.items():

    actual_value = (
        candidate_tags.get(
            key
        )
    )


    if (
        actual_value
        != expected_value
    ):

        raise RuntimeError(
            "Candidate registry gate state "
            f"is incomplete: {key}="
            f"{actual_value!r}"
        )


if (
    candidate_tags.get(
        "validation_status"
    )
    != "pending"
):

    raise RuntimeError(
        "Candidate must still be pending "
        "before final promotion."
    )


if (
    candidate_tags.get(
        "lifecycle_role"
    )
    != "candidate"
):

    raise RuntimeError(
        "Candidate lifecycle role is not "
        "'candidate' before promotion."
    )


# ------------------------------------------------------------
# 7. Verify candidate producing-run lineage
# ------------------------------------------------------------

candidate_run_id = (
    candidate_version_info.run_id
)


if not candidate_run_id:

    raise RuntimeError(
        "Candidate model version has no "
        "source run ID."
    )


candidate_run = (
    client.get_run(
        candidate_run_id
    )
)


if (
    candidate_run.info.status
    != "FINISHED"
):

    raise RuntimeError(
        "Candidate source MLflow run "
        "did not finish successfully."
    )


if not candidate_version_info.source:

    raise RuntimeError(
        "Candidate model version has no "
        "artifact source recorded."
    )


# ------------------------------------------------------------
# 8. Verify governance artifacts exist in source run
# ------------------------------------------------------------

source_artifacts = (
    client.list_artifacts(
        candidate_run_id
    )
)


source_artifact_names = {
    artifact.path.split(
        "/"
    )[0]
    for artifact in source_artifacts
}


required_source_artifacts = {
    "governance",
    "contracts",
}


missing_source_artifacts = (
    required_source_artifacts
    - source_artifact_names
)


if missing_source_artifacts:

    raise RuntimeError(
        "Candidate source run is missing "
        "required governance artifacts: "
        f"{sorted(missing_source_artifacts)}"
    )


provenance_versioning_passed = True


# ------------------------------------------------------------
# 9. Verify current champion is still the incumbent
# ------------------------------------------------------------

current_champion = (
    client.get_model_version_by_alias(
        name=REGISTERED_MODEL_NAME,
        alias=CHAMPION_ALIAS,
    )
)


if (
    str(
        current_champion.version
    )
    != incumbent_version
):

    raise RuntimeError(
        "Champion changed since TG2. "
        "Promotion aborted."
    )


current_champion_model = (
    mlflow.sklearn.load_model(
        (
            f"models:/"
            f"{REGISTERED_MODEL_NAME}"
            f"@{CHAMPION_ALIAS}"
        )
    )
)


if not isinstance(
    current_champion_model,
    RandomForestRegressor,
):

    raise RuntimeError(
        "Current champion is not the "
        "expected Random Forest incumbent."
    )


if (
    candidate_version
    == incumbent_version
):

    raise RuntimeError(
        "Candidate and incumbent versions "
        "must be different."
    )


# ------------------------------------------------------------
# 10. Last-minute software quality gate
# ------------------------------------------------------------

pytest_result = subprocess.run(
    [
        sys.executable,
        "-m",
        "pytest",
        "--cov=predictive_maintenance",
        "--cov-report=term-missing",
        "-q",
    ],
    check=False,
)


if (
    pytest_result.returncode
    != 0
):

    raise RuntimeError(
        "Final pytest gate failed. "
        "Promotion aborted."
    )


pip_check_result = subprocess.run(
    [
        sys.executable,
        "-m",
        "pip",
        "check",
    ],
    check=False,
)


if (
    pip_check_result.returncode
    != 0
):

    raise RuntimeError(
        "Final pip check failed. "
        "Promotion aborted."
    )


# ------------------------------------------------------------
# 11. Record current Git state
# ------------------------------------------------------------

git_commit = (
    git_output(
        "rev-parse",
        "HEAD",
    )
)


git_dirty = bool(
    git_output(
        "status",
        "--porcelain",
    )
)


# ------------------------------------------------------------
# 12. Resolve final promotion decision
# ------------------------------------------------------------

all_required_gates_passed = all(
    [
        all_prior_gates_passed,
        provenance_versioning_passed,
        (
            pytest_result.returncode
            == 0
        ),
        (
            pip_check_result.returncode
            == 0
        ),
    ]
)


if not all_required_gates_passed:

    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=candidate_version,
        key="validation_status",
        value="rejected",
    )


    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=candidate_version,
        key="promotion_decision",
        value="rejected",
    )


    decision = (
        "rejected"
    )


    promotion_performed = (
        False
    )


else:

    # --------------------------------------------------------
    # 13. Perform registry promotion with rollback protection
    # --------------------------------------------------------

    try:

        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=candidate_version,
            key="validation_status",
            value="passed",
        )


        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=candidate_version,
            key="promotion_decision",
            value="approved",
        )


        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=candidate_version,
            key="lifecycle_role",
            value="champion",
        )


        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=candidate_version,
            key="promoted_from_version",
            value=incumbent_version,
        )


        # Move the logical champion role.
        client.set_registered_model_alias(
            name=REGISTERED_MODEL_NAME,
            alias=CHAMPION_ALIAS,
            version=candidate_version,
        )


        # Historical incumbent remains registered.
        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=incumbent_version,
            key="lifecycle_role",
            value="previous_incumbent",
        )


        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=incumbent_version,
            key="replaced_by_version",
            value=candidate_version,
        )


        # ----------------------------------------------------
        # Verify registry transition
        # ----------------------------------------------------

        promoted_champion = (
            client.get_model_version_by_alias(
                name=REGISTERED_MODEL_NAME,
                alias=CHAMPION_ALIAS,
            )
        )


        if (
            str(
                promoted_champion.version
            )
            != candidate_version
        ):

            raise RuntimeError(
                "Champion alias verification failed "
                "after promotion."
            )


        promoted_model = (
            mlflow.sklearn.load_model(
                (
                    f"models:/"
                    f"{REGISTERED_MODEL_NAME}"
                    f"@{CHAMPION_ALIAS}"
                )
            )
        )


        if not isinstance(
            promoted_model,
            ExtraTreesRegressor,
        ):

            raise RuntimeError(
                "Promoted champion alias does not "
                "load ExtraTreesRegressor."
            )


        decision = (
            "approved"
        )


        promotion_performed = (
            True
        )


    except Exception:

        # ----------------------------------------------------
        # Roll back registry role if promotion mutation fails
        # ----------------------------------------------------

        client.set_registered_model_alias(
            name=REGISTERED_MODEL_NAME,
            alias=CHAMPION_ALIAS,
            version=incumbent_version,
        )


        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=candidate_version,
            key="validation_status",
            value="pending",
        )


        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=candidate_version,
            key="lifecycle_role",
            value="candidate",
        )


        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=candidate_version,
            key="promotion_decision",
            value="rollback_after_error",
        )


        client.set_model_version_tag(
            name=REGISTERED_MODEL_NAME,
            version=incumbent_version,
            key="lifecycle_role",
            value="incumbent",
        )


        raise


# ------------------------------------------------------------
# 14. Build evidence-file hashes
# ------------------------------------------------------------

evidence_hashes = {
    str(path): (
        sha256_file(
            path
        )
    )

    for path in required_paths
}


# ------------------------------------------------------------
# 15. Save final Git-trackable decision record
# ------------------------------------------------------------

decision_record = {
    "phase": (
        "3.2"
    ),

    "registered_model": (
        REGISTERED_MODEL_NAME
    ),

    "decision": (
        decision
    ),

    "candidate": {
        "version": (
            candidate_version
        ),

        "model_family": (
            "ExtraTreesRegressor"
        ),

        "source_run_id": (
            candidate_run_id
        ),

        "source_run_status": (
            candidate_run.info.status
        ),

        "source_artifact": (
            candidate_version_info.source
        ),
    },

    "previous_incumbent": {
        "version": (
            incumbent_version
        ),

        "model_family": (
            "RandomForestRegressor"
        ),
    },

    "gate_results": {
        **gate_results,

        "provenance_versioning": (
            provenance_versioning_passed
        ),

        "final_pytest": (
            pytest_result.returncode
            == 0
        ),

        "final_pip_check": (
            pip_check_result.returncode
            == 0
        ),
    },

    "all_required_gates_passed": (
        all_required_gates_passed
    ),

    "promotion_performed": (
        promotion_performed
    ),

    "champion_alias_after_decision": (
        candidate_version
        if promotion_performed
        else incumbent_version
    ),

    "deployment_cutover_performed": (
        False
    ),

    "git": {
        "commit": (
            git_commit
        ),

        "dirty": (
            git_dirty
        ),
    },

    "evidence_sha256": (
        evidence_hashes
    ),
}


with DECISION_PATH.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        decision_record,
        file,
        indent=2,
        sort_keys=True,
    )


# ------------------------------------------------------------
# 16. Human-readable result
# ------------------------------------------------------------

print(
    "\nPhase 3.2 TG4 complete."
)


print(
    "\nDecision:",
    decision.upper(),
)


print(
    "Candidate version:",
    candidate_version,
)


print(
    "Previous incumbent version:",
    incumbent_version,
)


print(
    "\nAll required gates passed:",
    all_required_gates_passed,
)


print(
    "Registry promotion performed:",
    promotion_performed,
)


print(
    "Champion version after decision:",
    (
        candidate_version
        if promotion_performed
        else incumbent_version
    ),
)


print(
    "\nGit commit:",
    git_commit,
)


print(
    "Git dirty:",
    git_dirty,
)


print(
    "\nDeployment cutover performed:",
    False,
)


print(
    "\nCreated:",
    DECISION_PATH,
)