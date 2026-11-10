from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pandas as pd


REPORTS_DIR = Path(
    "reports"
)


MONITORING_CONTRACT_PATH = (
    REPORTS_DIR
    / "phase_33_monitoring_contract.json"
)


TG1_VALIDATION_PATH = (
    REPORTS_DIR
    / "phase_33_tg1_telemetry_validation.json"
)


DRIFT_POLICY_PATH = (
    REPORTS_DIR
    / "phase_33_drift_policy.json"
)


REFERENCE_EVENTS_PATH = (
    REPORTS_DIR
    / "phase_33_reference_prediction_events.csv"
)


REFERENCE_BINS_PATH = (
    REPORTS_DIR
    / "phase_33_reference_bins.json"
)


REFERENCE_SUMMARY_PATH = (
    REPORTS_DIR
    / "phase_33_reference_baseline_summary.json"
)


TG3_REPORT_PATH = (
    REPORTS_DIR
    / "phase_33_tg3_monitoring_report.csv"
)


TG3_SUMMARY_PATH = (
    REPORTS_DIR
    / "phase_33_tg3_monitoring_summary.json"
)


HANDOFF_PATH = (
    REPORTS_DIR
    / "phase_33_handoff.json"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def load_json(
    path: Path,
) -> dict:

    if not path.exists():

        raise FileNotFoundError(
            f"Missing required Phase 3.3 artifact: {path}"
        )


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

    if not path.exists():

        raise FileNotFoundError(
            f"Cannot hash missing file: {path}"
        )


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


def require(
    condition: bool,
    message: str,
) -> None:

    if not condition:

        raise RuntimeError(
            message
        )


# ------------------------------------------------------------
# 1. Load Phase 3.3 evidence
# ------------------------------------------------------------

monitoring_contract = (
    load_json(
        MONITORING_CONTRACT_PATH
    )
)


tg1 = (
    load_json(
        TG1_VALIDATION_PATH
    )
)


drift_policy = (
    load_json(
        DRIFT_POLICY_PATH
    )
)


reference_bins = (
    load_json(
        REFERENCE_BINS_PATH
    )
)


reference_summary = (
    load_json(
        REFERENCE_SUMMARY_PATH
    )
)


tg3_summary = (
    load_json(
        TG3_SUMMARY_PATH
    )
)


if not REFERENCE_EVENTS_PATH.exists():

    raise FileNotFoundError(
        f"Missing: {REFERENCE_EVENTS_PATH}"
    )


if not TG3_REPORT_PATH.exists():

    raise FileNotFoundError(
        f"Missing: {TG3_REPORT_PATH}"
    )


reference_df = pd.read_csv(
    REFERENCE_EVENTS_PATH
)


tg3_report = pd.read_csv(
    TG3_REPORT_PATH
)


# ------------------------------------------------------------
# 2. Reconcile monitoring semantics
# ------------------------------------------------------------

require(
    monitoring_contract[
        "monitoring_unit"
    ][
        "name"
    ]
    == "prediction_event",

    "Monitoring unit is not prediction_event.",
)


require(
    monitoring_contract[
        "monitoring_unit"
    ][
        "raw_history_is_not_the_monitoring_unit"
    ]
    is True,

    "Raw history must not be treated "
    "as the monitoring observation.",
)


require(
    monitoring_contract[
        "model_identity_policy"
    ][
        "record_actual_served_model"
    ]
    is True,

    "Contract does not require actual "
    "served-model identity.",
)


require(
    monitoring_contract[
        "model_identity_policy"
    ][
        "do_not_infer_served_model_from_registry_alias"
    ]
    is True,

    "Contract incorrectly permits model "
    "identity inference from registry alias.",
)


require(
    monitoring_contract[
        "claim_boundaries"
    ][
        "unlabeled_data_drift_proves_accuracy_degradation"
    ]
    is False,

    "Monitoring contract incorrectly claims "
    "unlabeled drift proves degradation.",
)


require(
    monitoring_contract[
        "alert_policy"
    ][
        "drift_automatically_triggers_retraining"
    ]
    is False,

    "Monitoring contract incorrectly allows "
    "automatic retraining from drift alone.",
)


# ------------------------------------------------------------
# 3. Reconcile TG1 telemetry
# ------------------------------------------------------------

require(
    tg1[
        "telemetry_validation"
    ]
    == "passed",

    "TG1 telemetry validation did not pass.",
)


require(
    tg1[
        "prediction_event"
    ][
        "model_input_feature_count"
    ]
    == 36,

    "TG1 telemetry does not contain "
    "exactly 36 model inputs.",
)


tg1_model = (
    tg1[
        "prediction_event"
    ][
        "served_model"
    ]
)


# ------------------------------------------------------------
# 4. Reconcile TG2 reference baseline
# ------------------------------------------------------------

locked_features = list(
    reference_summary[
        "feature_contract"
    ][
        "feature_names"
    ]
)


require(
    len(
        locked_features
    )
    == 36,

    "TG2 reference feature contract "
    "does not contain 36 features.",
)


require(
    reference_summary[
        "feature_contract"
    ][
        "feature_count"
    ]
    == 36,

    "TG2 summary feature count is not 36.",
)


expected_reference_columns = {
    "reference_event_id",
    "engine_id",
    "current_cycle",
    "predicted_rul",
    *locked_features,
}


require(
    set(
        reference_df.columns
    )
    == expected_reference_columns,

    "Reference prediction-event columns "
    "do not match expected schema.",
)


require(
    len(
        reference_df
    )
    ==
    reference_summary[
        "reference_population"
    ][
        "event_count"
    ],

    "Reference event count disagrees "
    "with TG2 summary.",
)


require(
    reference_df[
        "engine_id"
    ]
    .nunique()
    ==
    reference_summary[
        "reference_population"
    ][
        "engine_count"
    ],

    "Reference engine count disagrees "
    "with TG2 summary.",
)


monitored_columns = (
    locked_features
    + [
        "predicted_rul"
    ]
)


require(
    len(
        monitored_columns
    )
    == 37,

    "Expected 37 monitored distributions.",
)


require(
    set(
        reference_bins[
            "columns"
        ].keys()
    )
    ==
    set(
        monitored_columns
    ),

    "Frozen-bin schema does not match "
    "36 features plus predicted_rul.",
)


require(
    reference_bins[
        "reference_only"
    ]
    is True,

    "PSI bins were not declared "
    "reference-only.",
)


# ------------------------------------------------------------
# 5. Verify TG1 and TG2 used same served artifact
# ------------------------------------------------------------

baseline_model = (
    reference_summary[
        "served_model"
    ]
)


require(
    tg1_model[
        "model_artifact_sha256"
    ]
    ==
    baseline_model[
        "model_artifact_sha256"
    ],

    "TG1 telemetry and TG2 baseline "
    "refer to different model artifacts.",
)


require(
    tg1_model[
        "locked_spec_sha256"
    ]
    ==
    baseline_model[
        "locked_spec_sha256"
    ],

    "TG1 telemetry and TG2 baseline "
    "refer to different locked specifications.",
)


# ------------------------------------------------------------
# 6. Reconcile frozen drift policy
# ------------------------------------------------------------

require(
    float(
        drift_policy[
            "thresholds"
        ][
            "stable_upper_exclusive"
        ]
    )
    == 0.10,

    "Stable PSI threshold changed.",
)


require(
    float(
        drift_policy[
            "thresholds"
        ][
            "warning_lower_inclusive"
        ]
    )
    == 0.10,

    "Warning PSI threshold changed.",
)


require(
    float(
        drift_policy[
            "thresholds"
        ][
            "alert_lower_inclusive"
        ]
    )
    == 0.25,

    "Alert PSI threshold changed.",
)


require(
    int(
        drift_policy[
            "window_policy"
        ][
            "minimum_prediction_events"
        ]
    )
    == 30,

    "Minimum monitoring-window size changed.",
)


require(
    drift_policy[
        "claim_boundaries"
    ][
        "psi_proves_accuracy_degradation"
    ]
    is False,

    "Drift policy incorrectly claims PSI "
    "proves performance degradation.",
)


require(
    drift_policy[
        "retraining_policy"
    ][
        "drift_automatically_triggers_retraining"
    ]
    is False,

    "Drift policy incorrectly triggers "
    "automatic retraining.",
)


# ------------------------------------------------------------
# 7. Reconcile TG3 detector validation
# ------------------------------------------------------------

require(
    tg3_summary[
        "validation"
    ][
        "stable_control_remained_stable"
    ]
    is True,

    "TG3 stable-control validation failed.",
)


require(
    tg3_summary[
        "validation"
    ][
        "all_injected_distributions_alerted"
    ]
    is True,

    "TG3 failed to alert on all "
    "injected distributions.",
)


require(
    tg3_summary[
        "validation"
    ][
        "drift_proves_accuracy_degradation"
    ]
    is False,

    "TG3 incorrectly claims that drift "
    "proves accuracy degradation.",
)


require(
    tg3_summary[
        "validation"
    ][
        "automatic_retraining_triggered"
    ]
    is False,

    "TG3 unexpectedly triggered retraining.",
)


stable_rows = (
    tg3_report
    .loc[
        tg3_report[
            "scenario"
        ]
        == "stable_control"
    ]
)


drift_rows = (
    tg3_report
    .loc[
        tg3_report[
            "scenario"
        ]
        == "drift_injection"
    ]
)


require(
    len(
        stable_rows
    )
    == 37,

    "TG3 stable scenario does not contain "
    "37 monitored distributions.",
)


require(
    len(
        drift_rows
    )
    == 37,

    "TG3 drift scenario does not contain "
    "37 monitored distributions.",
)


require(
    (
        stable_rows[
            "status"
        ]
        == "stable"
    ).all(),

    "TG3 stable control contains a "
    "non-stable result.",
)


# ------------------------------------------------------------
# 8. Record Git provenance
# ------------------------------------------------------------

git_commit = (
    git_output(
        "rev-parse",
        "HEAD",
    )
)


git_status = (
    git_output(
        "status",
        "--porcelain",
    )
)


git_dirty = bool(
    git_status
)


# ------------------------------------------------------------
# 9. Hash Phase 3.3 evidence
# ------------------------------------------------------------

evidence_paths = [
    MONITORING_CONTRACT_PATH,
    TG1_VALIDATION_PATH,
    DRIFT_POLICY_PATH,
    REFERENCE_EVENTS_PATH,
    REFERENCE_BINS_PATH,
    REFERENCE_SUMMARY_PATH,
    TG3_REPORT_PATH,
    TG3_SUMMARY_PATH,
]


evidence_hashes = {
    str(path): (
        sha256_file(
            path
        )
    )

    for path
    in evidence_paths
}


# ------------------------------------------------------------
# 10. Create Phase 3.3 handoff
# ------------------------------------------------------------

handoff = {
    "phase": "3.3",

    "name": (
        "Monitoring, Logging, "
        "and Drift Detection"
    ),

    "status": (
        "complete"
    ),

    "served_model_identity": {
        "source": (
            tg1_model[
                "source"
            ]
        ),

        "model_artifact_sha256": (
            tg1_model[
                "model_artifact_sha256"
            ]
        ),

        "locked_spec_sha256": (
            tg1_model[
                "locked_spec_sha256"
            ]
        ),

        "tg1_and_tg2_identity_match": (
            True
        ),
    },

    "monitoring_capability": {
        "telemetry_logging": (
            "implemented"
        ),

        "monitoring_unit": (
            "prediction_event"
        ),

        "model_input_feature_count": 36,

        "monitored_distribution_count": 37,

        "drift_metric": (
            "population_stability_index"
        ),

        "reference_bins_frozen": (
            True
        ),

        "minimum_window_events": 30,

        "states": [
            "insufficient_data",
            "stable",
            "warning",
            "alert",
        ],
    },

    "detector_validation": {
        "stable_control_passed": (
            True
        ),

        "synthetic_drift_detection_passed": (
            True
        ),
    },

    "claim_boundaries": {
        "drift_proves_accuracy_degradation": (
            False
        ),

        "outcome_labels_required_for_direct_performance_monitoring": (
            True
        ),

        "drift_automatically_triggers_retraining": (
            False
        ),
    },

    "phase_34_handoff": {
        "next_phase": (
            "3.4"
        ),

        "next_phase_name": (
            "Retraining Strategy and "
            "Production Failure Modes"
        ),

        "questions_to_answer": [
            (
                "What evidence should cause "
                "investigation rather than retraining?"
            ),

            (
                "What evidence is sufficient "
                "to justify retraining?"
            ),

            (
                "How should delayed outcome "
                "labels influence retraining decisions?"
            ),

            (
                "What production failure modes "
                "must be anticipated?"
            ),

            (
                "How does a retrained challenger "
                "return through evaluation, validation, "
                "promotion, and deployment?"
            ),
        ],
    },

    "provenance": {
        "git_commit": (
            git_commit
        ),

        "git_dirty": (
            git_dirty
        ),

        "git_dirty_is_not_an_automatic_failure": (
            True
        ),

        "evidence_sha256": (
            evidence_hashes
        ),
    },
}


with HANDOFF_PATH.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        handoff,
        file,
        indent=2,
        sort_keys=True,
    )


print(
    "\nPhase 3.3 evidence audit: PASSED"
)


print(
    "Monitoring features:",
    len(
        locked_features
    )
)


print(
    "Monitored distributions:",
    len(
        monitored_columns
    )
)


print(
    "Reference events:",
    len(
        reference_df
    )
)


print(
    "Served-model identity reconciled:",
    True
)


print(
    "Stable-control validation:",
    "PASSED"
)


print(
    "Synthetic-drift validation:",
    "PASSED"
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