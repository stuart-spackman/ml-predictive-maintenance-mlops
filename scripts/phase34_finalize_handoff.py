from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pandas as pd


REPORTS_DIR = Path("reports")

CONTRACT_PATH = (
    REPORTS_DIR
    / "phase_34_retraining_contract.json"
)

FAILURE_MATRIX_PATH = (
    REPORTS_DIR
    / "phase_34_failure_response_matrix.csv"
)

TG1_SUMMARY_PATH = (
    REPORTS_DIR
    / "phase_34_tg1_failure_response_summary.json"
)

PERFORMANCE_POLICY_PATH = (
    REPORTS_DIR
    / "phase_34_performance_retraining_policy.json"
)

TG2_PATH = (
    REPORTS_DIR
    / "phase_34_tg2_retraining_decision_validation.json"
)

EXECUTION_POLICY_PATH = (
    REPORTS_DIR
    / "phase_34_retraining_execution_policy.json"
)

TG3_PATH = (
    REPORTS_DIR
    / "phase_34_tg3_retraining_handoff.json"
)

HANDOFF_PATH = (
    REPORTS_DIR
    / "phase_34_handoff.json"
)


def load_json(path: Path) -> dict:

    if not path.exists():

        raise FileNotFoundError(
            f"Missing required Phase 3.4 artifact: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def require(
    condition: bool,
    message: str,
) -> None:

    if not condition:

        raise RuntimeError(message)


def sha256_file(path: Path) -> str:

    digest = hashlib.sha256()

    with path.open("rb") as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):

            digest.update(chunk)

    return digest.hexdigest()


def git_output(
    *args: str,
) -> str:

    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


# ------------------------------------------------------------
# 1. Load Phase 3.4 evidence
# ------------------------------------------------------------

contract = load_json(
    CONTRACT_PATH
)

tg1 = load_json(
    TG1_SUMMARY_PATH
)

performance_policy = load_json(
    PERFORMANCE_POLICY_PATH
)

tg2 = load_json(
    TG2_PATH
)

execution_policy = load_json(
    EXECUTION_POLICY_PATH
)

tg3 = load_json(
    TG3_PATH
)


if not FAILURE_MATRIX_PATH.exists():

    raise FileNotFoundError(
        f"Missing: {FAILURE_MATRIX_PATH}"
    )


failure_matrix = pd.read_csv(
    FAILURE_MATRIX_PATH
)


# ------------------------------------------------------------
# 2. Reconcile TG0 retraining contract
# ------------------------------------------------------------

require(
    contract[
        "decision_boundaries"
    ][
        "drift_detection_is_retraining_authorization"
    ]
    is False,
    "Drift must not directly authorize retraining.",
)


require(
    contract[
        "decision_boundaries"
    ][
        "retrained_model_is_a_challenger"
    ]
    is True,
    "Retrained models must enter as challengers.",
)


require(
    contract[
        "decision_boundaries"
    ][
        "retraining_is_promotion"
    ]
    is False,
    "Retraining must remain separate from promotion.",
)


require(
    contract[
        "decision_boundaries"
    ][
        "promotion_is_deployment"
    ]
    is False,
    "Promotion must remain separate from deployment.",
)


require(
    contract[
        "scope"
    ][
        "automatic_retraining"
    ]
    is False,
    "Phase 3.4 must not enable automatic retraining.",
)


# ------------------------------------------------------------
# 3. Reconcile TG1 failure-response policy
# ------------------------------------------------------------

require(
    tg1[
        "validation"
    ]
    == "passed",
    "TG1 failure-response validation did not pass.",
)


require(
    len(
        failure_matrix
    )
    == 14,
    "Expected 14 failure-response rows.",
)


lookup = (
    failure_matrix
    .set_index("failure_id")
)


require(
    lookup.loc[
        "PERSISTENT_DRIFT",
        "retraining_relevance",
    ]
    == "conditional",
    "Persistent drift must remain conditional evidence.",
)


require(
    lookup.loc[
        "PERFORMANCE_DEGRADATION",
        "retraining_relevance",
    ]
    == "yes",
    "Validated degradation should support "
    "retraining consideration.",
)


for failure_id in [
    "SERVICE_UNAVAILABLE",
    "INPUT_CONTRACT",
    "ARTIFACT_INTEGRITY",
    "TELEMETRY_FAILURE",
    "REFERENCE_INCOMPATIBLE",
    "LABEL_PIPELINE",
]:

    require(
        lookup.loc[
            failure_id,
            "retraining_relevance",
        ]
        == "no",
        f"{failure_id} must not directly "
        "authorize retraining.",
    )


# ------------------------------------------------------------
# 4. Reconcile TG2 delayed-label policy
# ------------------------------------------------------------

require(
    performance_policy[
        "performance_monitoring"
    ][
        "minimum_labeled_prediction_events"
    ]
    == 30,
    "Minimum labeled-event requirement changed.",
)


require(
    float(
        performance_policy[
            "degradation_policy"
        ][
            "relative_rmse_increase_threshold"
        ]
    )
    == 0.10,
    "RMSE degradation threshold changed.",
)


require(
    performance_policy[
        "label_policy"
    ][
        "labels_must_be_trustworthy_before_performance_evaluation"
    ]
    is True,
    "Label quality must precede performance conclusions.",
)


require(
    performance_policy[
        "decision_boundaries"
    ][
        "performance_degraded_automatically_retrains"
    ]
    is False,
    "Performance degradation must not "
    "automatically trigger retraining.",
)


require(
    tg2[
        "validation"
    ]
    == "passed",
    "TG2 decision validation did not pass.",
)


require(
    tg2[
        "scenarios"
    ][
        "eligible_to_retrain"
    ][
        "status"
    ]
    == "eligible_to_retrain",
    "TG2 did not validate the retraining-eligible branch.",
)


require(
    tg2[
        "decision_boundaries"
    ][
        "eligible_to_retrain_means_deploy"
    ]
    is False,
    "Retraining eligibility must not imply deployment.",
)


# ------------------------------------------------------------
# 5. Reconcile TG3 execution boundary
# ------------------------------------------------------------

require(
    execution_policy[
        "execution_boundary"
    ][
        "incumbent_mutated_in_place"
    ]
    is False,
    "Incumbent must remain immutable.",
)


require(
    execution_policy[
        "promotion_boundary"
    ][
        "retraining_moves_champion_alias"
    ]
    is False,
    "Retraining must not move champion alias.",
)


require(
    execution_policy[
        "promotion_boundary"
    ][
        "retraining_changes_fastapi_serving"
    ]
    is False,
    "Retraining must not change FastAPI serving.",
)


require(
    execution_policy[
        "project_reality"
    ][
        "genuine_new_labeled_production_data_available"
    ]
    is False,
    "Portfolio reality unexpectedly changed.",
)


require(
    execution_policy[
        "project_reality"
    ][
        "real_production_retraining_claim_allowed"
    ]
    is False,
    "Project must not claim real production retraining.",
)


require(
    tg3[
        "validation"
    ]
    == "passed",
    "TG3 retraining handoff validation did not pass.",
)


require(
    tg3[
        "project_reality"
    ][
        "actual_new_challenger_fit"
    ]
    is False,
    "TG3 unexpectedly claims a real challenger fit.",
)


require(
    tg3[
        "incumbent"
    ][
        "unchanged"
    ]
    is True,
    "Incumbent changed during retraining simulation.",
)


require(
    tg3[
        "safety_boundaries"
    ][
        "registry_alias_moved"
    ]
    is False,
    "TG3 unexpectedly moved a registry alias.",
)


require(
    tg3[
        "safety_boundaries"
    ][
        "serving_cutover_performed"
    ]
    is False,
    "TG3 unexpectedly performed deployment cutover.",
)


require(
    tg3[
        "safety_boundaries"
    ][
        "real_production_retraining_claimed"
    ]
    is False,
    "TG3 incorrectly claims real production retraining.",
)


# ------------------------------------------------------------
# 6. Hash Phase 3.4 evidence
# ------------------------------------------------------------

evidence_paths = [
    CONTRACT_PATH,
    FAILURE_MATRIX_PATH,
    TG1_SUMMARY_PATH,
    PERFORMANCE_POLICY_PATH,
    TG2_PATH,
    EXECUTION_POLICY_PATH,
    TG3_PATH,
]


evidence_hashes = {
    str(path): sha256_file(path)

    for path
    in evidence_paths
}


# ------------------------------------------------------------
# 7. Git provenance
# ------------------------------------------------------------

git_commit = git_output(
    "rev-parse",
    "HEAD",
)


git_status = git_output(
    "status",
    "--porcelain",
)


git_dirty = bool(
    git_status
)


# ------------------------------------------------------------
# 8. Create final Phase 3.4 + Part 3 handoff
# ------------------------------------------------------------

handoff = {
    "phase": "3.4",

    "name": (
        "Retraining Strategy and "
        "Production Failure Modes"
    ),

    "status": "complete",

    "validated_capabilities": {
        "failure_mode_classification": True,
        "layer_specific_response_policy": True,
        "delayed_label_performance_logic": True,
        "retraining_eligibility_logic": True,
        "safe_challenger_handoff": True,
        "incumbent_preservation": True,
        "rollback_preconditions_defined": True,
    },

    "decision_chain": [
        "observe production signal",
        "identify failing layer",
        "investigate cause",
        "obtain trustworthy delayed labels when required",
        "evaluate direct performance",
        "decide whether retraining is justified",
        "fit a separate challenger when real evidence and data exist",
        "evaluate and validate challenger",
        "make promotion decision",
        "make separate deployment decision",
    ],

    "claim_boundaries": {
        "drift_proves_performance_degradation": False,
        "performance_degradation_automatically_retrains": False,
        "retraining_means_promotion": False,
        "promotion_means_deployment": False,
        "registry_champion_proves_actual_serving_identity": False,
    },

    "project_reality": {
        "genuine_new_labeled_production_data_available": False,
        "real_production_retraining_performed": False,
        "retraining_workflow_simulated_and_validated": True,
        "incumbent_preserved": True,
    },

    "part_3_handoff": {
        "part": "3",

        "name": (
            "Model Improvement and "
            "Production Thinking"
        ),

        "status": "complete",

        "lifecycle_summary": (
            "Model experimentation, governed promotion, "
            "runtime monitoring, delayed-label performance "
            "reasoning, and evidence-driven retraining are "
            "treated as separate but connected lifecycle stages."
        ),

        "next_phase": "4.1",

        "next_phase_name": (
            "Documentation & Technical Storytelling"
        ),
    },

    "provenance": {
        "git_commit": git_commit,
        "git_dirty": git_dirty,
        "evidence_sha256": evidence_hashes,
    },
}


HANDOFF_PATH.write_text(
    json.dumps(
        handoff,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print(
    "\nPhase 3.4 evidence audit: PASSED"
)


print(
    "Failure modes:",
    len(failure_matrix)
)


print(
    "Minimum labeled events:",
    30
)


print(
    "RMSE degradation threshold:",
    "10%"
)


print(
    "Incumbent preserved:",
    True
)


print(
    "Real production retraining claimed:",
    False
)


print(
    "Part 3 status:",
    "complete"
)


print(
    "Next phase:",
    "4.1 Documentation & Technical Storytelling"
)


print(
    "Git commit:",
    git_commit
)


print(
    "Git dirty:",
    git_dirty
)


print(
    "\nCreated:",
    HANDOFF_PATH
)