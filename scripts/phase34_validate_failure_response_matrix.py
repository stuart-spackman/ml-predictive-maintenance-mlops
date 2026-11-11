from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


REPORTS_DIR = Path(
    "reports"
)


MATRIX_PATH = (
    REPORTS_DIR
    / "phase_34_failure_response_matrix.csv"
)


CONTRACT_PATH = (
    REPORTS_DIR
    / "phase_34_retraining_contract.json"
)


SUMMARY_PATH = (
    REPORTS_DIR
    / "phase_34_tg1_failure_response_summary.json"
)


EXPECTED_COLUMNS = [
    "failure_id",
    "failure_family",
    "example_signal",
    "primary_diagnosis_question",
    "first_response",
    "serving_behavior",
    "retraining_relevance",
]


ALLOWED_RETRAINING_RELEVANCE = {
    "no",
    "conditional",
    "yes",
}


REQUIRED_FAILURE_IDS = {
    "SERVICE_UNAVAILABLE",
    "SERVICE_LATENCY",
    "INPUT_CONTRACT",
    "SENSOR_SOURCE",
    "ARTIFACT_INTEGRITY",
    "SERVING_IDENTITY",
    "TELEMETRY_FAILURE",
    "INSUFFICIENT_MONITORING_DATA",
    "REFERENCE_INCOMPATIBLE",
    "LABEL_PIPELINE",
    "PERSISTENT_DRIFT",
    "PERFORMANCE_DEGRADATION",
    "RETRAINING_LEAKAGE",
    "CANDIDATE_REGRESSION",
}


def require(
    condition: bool,
    message: str,
) -> None:

    if not condition:

        raise RuntimeError(
            message
        )


if not MATRIX_PATH.exists():

    raise FileNotFoundError(
        f"Missing failure matrix: {MATRIX_PATH}"
    )


if not CONTRACT_PATH.exists():

    raise FileNotFoundError(
        f"Missing retraining contract: {CONTRACT_PATH}"
    )


matrix = pd.read_csv(
    MATRIX_PATH
)


with CONTRACT_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    contract = json.load(
        file
    )


# ------------------------------------------------------------
# Schema checks
# ------------------------------------------------------------

require(
    list(
        matrix.columns
    )
    == EXPECTED_COLUMNS,

    "Failure-response matrix columns "
    "do not match expected schema.",
)


require(
    matrix[
        "failure_id"
    ]
    .is_unique,

    "failure_id values must be unique.",
)


require(
    set(
        matrix[
            "failure_id"
        ]
    )
    ==
    REQUIRED_FAILURE_IDS,

    "Failure-response matrix does not "
    "contain the required failure set.",
)


require(
    set(
        matrix[
            "retraining_relevance"
        ]
    )
    <=
    ALLOWED_RETRAINING_RELEVANCE,

    "Unexpected retraining_relevance value.",
)


# ------------------------------------------------------------
# Policy checks
# ------------------------------------------------------------

lookup = (
    matrix
    .set_index(
        "failure_id"
    )
)


for failure_id in [
    "SERVICE_UNAVAILABLE",
    "INPUT_CONTRACT",
    "ARTIFACT_INTEGRITY",
    "SERVING_IDENTITY",
    "TELEMETRY_FAILURE",
    "INSUFFICIENT_MONITORING_DATA",
    "REFERENCE_INCOMPATIBLE",
    "LABEL_PIPELINE",
    "RETRAINING_LEAKAGE",
    "CANDIDATE_REGRESSION",
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


require(
    lookup.loc[
        "PERSISTENT_DRIFT",
        "retraining_relevance",
    ]
    == "conditional",

    "Persistent drift should remain "
    "conditional evidence.",
)


require(
    lookup.loc[
        "PERFORMANCE_DEGRADATION",
        "retraining_relevance",
    ]
    == "yes",

    "Validated predictive degradation "
    "should support retraining consideration.",
)


require(
    contract[
        "decision_boundaries"
    ][
        "drift_detection_is_retraining_authorization"
    ]
    is False,

    "Retraining contract incorrectly "
    "allows drift to authorize retraining.",
)


require(
    contract[
        "decision_boundaries"
    ][
        "retrained_model_is_a_challenger"
    ]
    is True,

    "Retrained model must remain a challenger.",
)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

relevance_counts = (
    matrix[
        "retraining_relevance"
    ]
    .value_counts()
    .to_dict()
)


summary = {
    "phase": "3.4",
    "task_group": "TG1",

    "validation": (
        "passed"
    ),

    "failure_mode_count": int(
        len(
            matrix
        )
    ),

    "failure_family_count": int(
        matrix[
            "failure_family"
        ]
        .nunique()
    ),

    "retraining_relevance_counts": {
        key: int(
            value
        )

        for key, value
        in relevance_counts.items()
    },

    "policy_checks": {
        "non_model_failures_do_not_authorize_retraining": (
            True
        ),

        "persistent_drift_is_conditional": (
            True
        ),

        "validated_performance_degradation_can_support_retraining": (
            True
        ),

        "retrained_model_remains_challenger": (
            True
        ),
    },

    "artifacts": {
        "failure_response_matrix": (
            str(
                MATRIX_PATH
            )
        ),

        "retraining_contract": (
            str(
                CONTRACT_PATH
            )
        ),
    },
}


SUMMARY_PATH.write_text(
    json.dumps(
        summary,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print(
    "\nPhase 3.4 TG1 failure-response "
    "matrix validation: PASSED"
)


print(
    "Failure modes:",
    len(
        matrix
    )
)


print(
    "Failure families:",
    matrix[
        "failure_family"
    ]
    .nunique()
)


print(
    "Retraining relevance:",
    relevance_counts
)


print(
    "\nCreated:",
    SUMMARY_PATH
)