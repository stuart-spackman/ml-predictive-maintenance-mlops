from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from predictive_maintenance.monitoring.runtime import (
    evaluate_runtime_window,
    prediction_events_to_frame,
)


REPORTS_DIR = Path(
    "reports"
)


TELEMETRY_PATH = Path(
    "runtime/telemetry/events.jsonl"
)


RUNTIME_STATUS_PATH = Path(
    "runtime/monitoring/current_status.json"
)


INTEGRATION_REPORT_PATH = (
    REPORTS_DIR
    / "phase_33_tg5_runtime_monitoring_integration.json"
)


POLICY_PATH = (
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


HANDOFF_PATH = (
    REPORTS_DIR
    / "phase_33_handoff.json"
)


def load_json(
    path: Path,
) -> dict:

    if not path.exists():

        raise FileNotFoundError(
            f"Missing required file: {path}"
        )


    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(
            file
        )


# ------------------------------------------------------------
# 1. Load frozen monitoring configuration
# ------------------------------------------------------------

policy = (
    load_json(
        POLICY_PATH
    )
)


reference_bins_record = (
    load_json(
        REFERENCE_BINS_PATH
    )
)


reference_summary = (
    load_json(
        REFERENCE_SUMMARY_PATH
    )
)


if not REFERENCE_EVENTS_PATH.exists():

    raise FileNotFoundError(
        f"Missing reference events: "
        f"{REFERENCE_EVENTS_PATH}"
    )


reference_df = pd.read_csv(
    REFERENCE_EVENTS_PATH
)


locked_features = list(
    reference_summary[
        "feature_contract"
    ][
        "feature_names"
    ]
)


if len(
    locked_features
) != 36:

    raise RuntimeError(
        "Expected 36 locked features."
    )


baseline_model = (
    reference_summary[
        "served_model"
    ]
)


# ------------------------------------------------------------
# 2. Load actual runtime telemetry
# ------------------------------------------------------------

events = []


if TELEMETRY_PATH.exists():

    for line in (
        TELEMETRY_PATH
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
    ):

        if not line.strip():

            continue


        events.append(
            json.loads(
                line
            )
        )


prediction_df = (
    prediction_events_to_frame(
        events,
        locked_features=(
            locked_features
        ),
    )
)


# ------------------------------------------------------------
# 3. Evaluate runtime monitoring state
# ------------------------------------------------------------

window_policy = (
    policy[
        "window_policy"
    ]
)


result = (
    evaluate_runtime_window(
        reference_df=(
            reference_df
        ),

        prediction_events_df=(
            prediction_df
        ),

        locked_features=(
            locked_features
        ),

        reference_bins=(
            reference_bins_record[
                "columns"
            ]
        ),

        expected_model_sha256=(
            baseline_model[
                "model_artifact_sha256"
            ]
        ),

        expected_locked_spec_sha256=(
            baseline_model[
                "locked_spec_sha256"
            ]
        ),

        minimum_events=int(
            window_policy[
                "minimum_prediction_events"
            ]
        ),

        window_size=int(
            window_policy[
                "evaluation_window_prediction_events"
            ]
        ),

        epsilon=float(
            policy[
                "metric"
            ][
                "epsilon"
            ]
        ),

        warning_threshold=float(
            policy[
                "thresholds"
            ][
                "warning_lower_inclusive"
            ]
        ),

        alert_threshold=float(
            policy[
                "thresholds"
            ][
                "alert_lower_inclusive"
            ]
        ),
    )
)


# ------------------------------------------------------------
# 4. Write current runtime status
# ------------------------------------------------------------

runtime_status = {
    "phase": "3.3",

    "monitoring_state": (
        result[
            "status"
        ]
    ),

    "reference_model": {
        "model_artifact_sha256": (
            baseline_model[
                "model_artifact_sha256"
            ]
        ),

        "locked_spec_sha256": (
            baseline_model[
                "locked_spec_sha256"
            ]
        ),
    },

    "window_policy": (
        window_policy
    ),

    **result,
}


RUNTIME_STATUS_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


RUNTIME_STATUS_PATH.write_text(
    json.dumps(
        runtime_status,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


# ------------------------------------------------------------
# 5. Create one tracked integration-evidence record
# ------------------------------------------------------------

integration_report = {
    "phase": "3.3",
    "task_group": "TG5",

    "runtime_monitoring_integration": (
        "implemented"
    ),

    "telemetry_source": (
        str(
            TELEMETRY_PATH
        )
    ),

    "reference_source": (
        str(
            REFERENCE_EVENTS_PATH
        )
    ),

    "window_strategy": (
        window_policy[
            "selection"
        ]
    ),

    "window_size": int(
        window_policy[
            "evaluation_window_prediction_events"
        ]
    ),

    "possible_states": [
        "reference_incompatible",
        "insufficient_data",
        "stable",
        "warning",
        "alert",
    ],

    "observed_state_at_validation": (
        result[
            "status"
        ]
    ),

    "distribution_count_when_evaluable": (
        37
    ),

    "claim_boundaries": {
        "alert_is_diagnosis": (
            False
        ),

        "alert_proves_accuracy_degradation": (
            False
        ),

        "alert_automatically_triggers_retraining": (
            False
        ),
    },

    "runtime_status_artifact": (
        str(
            RUNTIME_STATUS_PATH
        )
    ),
}


INTEGRATION_REPORT_PATH.write_text(
    json.dumps(
        integration_report,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


# ------------------------------------------------------------
# 6. Extend the single Phase 3.3 handoff
# ------------------------------------------------------------

if HANDOFF_PATH.exists():

    handoff = (
        load_json(
            HANDOFF_PATH
        )
    )


    handoff[
        "runtime_monitoring_integration"
    ] = {
        "implemented": True,

        "window_strategy": (
            window_policy[
                "selection"
            ]
        ),

        "window_size": int(
            window_policy[
                "evaluation_window_prediction_events"
            ]
        ),

        "possible_states": [
            "reference_incompatible",
            "insufficient_data",
            "stable",
            "warning",
            "alert",
        ],

        "runtime_status_artifact": (
            str(
                RUNTIME_STATUS_PATH
            )
        ),

        "tg5_evidence": (
            str(
                INTEGRATION_REPORT_PATH
            )
        ),
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


# ------------------------------------------------------------
# 7. Human-readable result
# ------------------------------------------------------------

print(
    "\nPhase 3.3 TG5 runtime monitoring."
)


print(
    "\nPrediction events available:",
    len(
        prediction_df
    )
)


print(
    "Monitoring state:",
    result[
        "status"
    ]
)


if (
    result[
        "status"
    ]
    == "insufficient_data"
):

    print(
        "Events required:",
        window_policy[
            "minimum_prediction_events"
        ]
    )


elif (
    result[
        "status"
    ]
    in {
        "stable",
        "warning",
        "alert",
    }
):

    distribution_results = (
        result[
            "distribution_results"
        ]
    )


    warning_count = sum(
        row[
            "status"
        ]
        == "warning"

        for row
        in distribution_results
    )


    alert_count = sum(
        row[
            "status"
        ]
        == "alert"

        for row
        in distribution_results
    )


    print(
        "Warnings:",
        warning_count
    )


    print(
        "Alerts:",
        alert_count
    )


elif (
    result[
        "status"
    ]
    == "reference_incompatible"
):

    print(
        "Reference baseline cannot be "
        "validly applied to the current "
        "serving identity."
    )


print(
    "\nRuntime state:",
    RUNTIME_STATUS_PATH
)


print(
    "Integration evidence:",
    INTEGRATION_REPORT_PATH
)