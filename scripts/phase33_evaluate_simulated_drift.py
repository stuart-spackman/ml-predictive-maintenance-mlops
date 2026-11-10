from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from predictive_maintenance.monitoring.drift import (
    classify_psi,
    population_stability_index,
)


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

REPORTS_DIR = Path(
    "reports"
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


MONITORING_REPORT_PATH = (
    REPORTS_DIR
    / "phase_33_tg3_monitoring_report.csv"
)


MONITORING_SUMMARY_PATH = (
    REPORTS_DIR
    / "phase_33_tg3_monitoring_summary.json"
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

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
# 1. Load frozen monitoring state
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
        "Missing reference prediction events: "
        f"{REFERENCE_EVENTS_PATH}"
    )


reference_df = pd.read_csv(
    REFERENCE_EVENTS_PATH
)


# ------------------------------------------------------------
# 2. Recover locked monitored columns
# ------------------------------------------------------------

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
        "Expected exactly 36 locked "
        "model-input features."
    )


monitored_columns = (
    locked_features
    + [
        "predicted_rul"
    ]
)


if len(
    monitored_columns
) != 37:

    raise RuntimeError(
        "Expected exactly 37 monitored "
        "distributions."
    )


for column in monitored_columns:

    if (
        column
        not in reference_df.columns
    ):

        raise RuntimeError(
            "Reference population is missing "
            f"monitored column: {column}"
        )


reference_bins = (
    reference_bins_record[
        "columns"
    ]
)


for column in monitored_columns:

    if (
        column
        not in reference_bins
    ):

        raise RuntimeError(
            "Frozen PSI bins are missing "
            f"column: {column}"
        )


# ------------------------------------------------------------
# 3. Load frozen PSI policy
# ------------------------------------------------------------

epsilon = float(
    policy[
        "metric"
    ][
        "epsilon"
    ]
)


warning_threshold = float(
    policy[
        "thresholds"
    ][
        "warning_lower_inclusive"
    ]
)


alert_threshold = float(
    policy[
        "thresholds"
    ][
        "alert_lower_inclusive"
    ]
)


minimum_events = int(
    policy[
        "window_policy"
    ][
        "minimum_prediction_events"
    ]
)


if (
    len(
        reference_df
    )
    < minimum_events
):

    raise RuntimeError(
        "Reference population does not meet "
        "minimum monitoring-window size."
    )


# ------------------------------------------------------------
# 4. Build healthy control window
# ------------------------------------------------------------
#
# Same rows, same values, different order.
#
# Distribution should therefore remain exactly unchanged.
# ------------------------------------------------------------

stable_window = (
    reference_df
    .sample(
        frac=1.0,
        random_state=42,
    )
    .reset_index(
        drop=True
    )
)


# ------------------------------------------------------------
# 5. Select deterministic drift-injection features
# ------------------------------------------------------------
#
# Select the first three locked features whose reference
# population actually varies.
# ------------------------------------------------------------

drift_features = []


for feature_name in locked_features:

    reference_min = float(
        reference_df[
            feature_name
        ]
        .min()
    )


    reference_max = float(
        reference_df[
            feature_name
        ]
        .max()
    )


    if (
        reference_max
        > reference_min
    ):

        drift_features.append(
            feature_name
        )


    if (
        len(
            drift_features
        )
        == 3
    ):

        break


if (
    len(
        drift_features
    )
    != 3
):

    raise RuntimeError(
        "Could not find three non-constant "
        "locked features for drift injection."
    )


# ------------------------------------------------------------
# 6. Build deliberately drifted window
# ------------------------------------------------------------

drifted_window = (
    stable_window.copy()
)


drift_injections = {}


for feature_name in drift_features:

    reference_min = float(
        reference_df[
            feature_name
        ]
        .min()
    )


    reference_max = float(
        reference_df[
            feature_name
        ]
        .max()
    )


    reference_range = (
        reference_max
        - reference_min
    )


    shift = (
        2.0
        * reference_range
    )


    drifted_window[
        feature_name
    ] = (
        drifted_window[
            feature_name
        ]
        + shift
    )


    drift_injections[
        feature_name
    ] = {
        "type": (
            "additive_shift"
        ),

        "reference_min": (
            reference_min
        ),

        "reference_max": (
            reference_max
        ),

        "shift": float(
            shift
        ),
    }


# ------------------------------------------------------------
# 7. Inject prediction drift independently
# ------------------------------------------------------------

prediction_min = float(
    reference_df[
        "predicted_rul"
    ]
    .min()
)


prediction_max = float(
    reference_df[
        "predicted_rul"
    ]
    .max()
)


prediction_range = (
    prediction_max
    - prediction_min
)


if (
    prediction_range
    <= 0.0
):

    raise RuntimeError(
        "Reference prediction distribution "
        "does not vary."
    )


prediction_shift = (
    2.0
    * prediction_range
)


drifted_window[
    "predicted_rul"
] = (
    drifted_window[
        "predicted_rul"
    ]
    + prediction_shift
)


drift_injections[
    "predicted_rul"
] = {
    "type": (
        "additive_shift"
    ),

    "reference_min": (
        prediction_min
    ),

    "reference_max": (
        prediction_max
    ),

    "shift": float(
        prediction_shift
    ),

    "note": (
        "Synthetic prediction-distribution "
        "injection for detector validation; "
        "not regenerated from the estimator."
    ),
}


# ------------------------------------------------------------
# 8. Evaluate one monitoring window
# ------------------------------------------------------------

def evaluate_window(
    *,
    scenario: str,
    current_df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []


    if (
        len(
            current_df
        )
        < minimum_events
    ):

        raise RuntimeError(
            f"{scenario} does not meet minimum "
            "monitoring-window size."
        )


    for column in monitored_columns:

        psi = (
            population_stability_index(
                reference_df[
                    column
                ],

                current_df[
                    column
                ],

                cutpoints=(
                    reference_bins[
                        column
                    ]
                ),

                epsilon=(
                    epsilon
                ),
            )
        )


        status = (
            classify_psi(
                psi,

                warning_threshold=(
                    warning_threshold
                ),

                alert_threshold=(
                    alert_threshold
                ),
            )
        )


        distribution_type = (
            "prediction"
            if (
                column
                == "predicted_rul"
            )
            else
            "model_input_feature"
        )


        rows.append(
            {
                "scenario": (
                    scenario
                ),

                "distribution_type": (
                    distribution_type
                ),

                "column": (
                    column
                ),

                "psi": float(
                    psi
                ),

                "status": (
                    status
                ),

                "drift_injected": (
                    column
                    in drift_injections
                    if (
                        scenario
                        == "drift_injection"
                    )
                    else False
                ),
            }
        )


    return pd.DataFrame(
        rows
    )


# ------------------------------------------------------------
# 9. Evaluate healthy + drifted scenarios
# ------------------------------------------------------------

stable_results = (
    evaluate_window(
        scenario=(
            "stable_control"
        ),

        current_df=(
            stable_window
        ),
    )
)


drifted_results = (
    evaluate_window(
        scenario=(
            "drift_injection"
        ),

        current_df=(
            drifted_window
        ),
    )
)


monitoring_report = pd.concat(
    [
        stable_results,
        drifted_results,
    ],
    ignore_index=True,
)


# ------------------------------------------------------------
# 10. Validate expected detector behavior
# ------------------------------------------------------------

stable_max_psi = float(
    stable_results[
        "psi"
    ]
    .max()
)


if (
    stable_max_psi
    > 1e-12
):

    raise RuntimeError(
        "Stable control should have "
        "approximately zero PSI."
    )


stable_nonstable = (
    stable_results
    .loc[
        stable_results[
            "status"
        ]
        != "stable"
    ]
)


if not stable_nonstable.empty:

    raise RuntimeError(
        "Stable control unexpectedly "
        "produced drift warnings/alerts."
    )


for column in drift_injections:

    row = (
        drifted_results
        .loc[
            drifted_results[
                "column"
            ]
            == column
        ]
    )


    if (
        len(
            row
        )
        != 1
    ):

        raise RuntimeError(
            "Could not uniquely locate "
            f"drift result for {column}."
        )


    status = (
        row[
            "status"
        ]
        .iloc[0]
    )


    if (
        status
        != "alert"
    ):

        raise RuntimeError(
            "Injected drift did not produce "
            f"an alert for {column}. "
            f"Observed status: {status}"
        )


# ------------------------------------------------------------
# 11. Save flat monitoring report
# ------------------------------------------------------------

monitoring_report.to_csv(
    MONITORING_REPORT_PATH,
    index=False,
)


# ------------------------------------------------------------
# 12. Build scenario summaries
# ------------------------------------------------------------

def summarize_results(
    results: pd.DataFrame,
) -> dict:

    status_counts = (
        results[
            "status"
        ]
        .value_counts()
        .to_dict()
    )


    alert_columns = (
        results
        .loc[
            results[
                "status"
            ]
            == "alert",
            "column",
        ]
        .tolist()
    )


    warning_columns = (
        results
        .loc[
            results[
                "status"
            ]
            == "warning",
            "column",
        ]
        .tolist()
    )


    return {
        "distribution_count": int(
            len(
                results
            )
        ),

        "stable_count": int(
            status_counts.get(
                "stable",
                0,
            )
        ),

        "warning_count": int(
            status_counts.get(
                "warning",
                0,
            )
        ),

        "alert_count": int(
            status_counts.get(
                "alert",
                0,
            )
        ),

        "maximum_psi": float(
            results[
                "psi"
            ]
            .max()
        ),

        "warning_columns": (
            warning_columns
        ),

        "alert_columns": (
            alert_columns
        ),
    }


stable_summary = (
    summarize_results(
        stable_results
    )
)


drifted_summary = (
    summarize_results(
        drifted_results
    )
)


# ------------------------------------------------------------
# 13. Save monitoring decision record
# ------------------------------------------------------------

summary = {
    "phase": "3.3",
    "task_group": "TG3",

    "purpose": (
        "Validate the drift-monitoring system "
        "against known stable and deliberately "
        "drifted distributions."
    ),

    "reference": {
        "event_count": int(
            len(
                reference_df
            )
        ),

        "monitored_distribution_count": (
            len(
                monitored_columns
            )
        ),

        "served_model": (
            reference_summary[
                "served_model"
            ]
        ),
    },

    "policy": {
        "metric": (
            "population_stability_index"
        ),

        "stable_upper_exclusive": (
            policy[
                "thresholds"
            ][
                "stable_upper_exclusive"
            ]
        ),

        "warning_lower_inclusive": (
            warning_threshold
        ),

        "alert_lower_inclusive": (
            alert_threshold
        ),

        "minimum_prediction_events": (
            minimum_events
        ),
    },

    "stable_control": (
        stable_summary
    ),

    "drift_injection": {
        **drifted_summary,

        "injected_distributions": (
            drift_injections
        ),
    },

    "validation": {
        "stable_control_remained_stable": (
            True
        ),

        "all_injected_distributions_alerted": (
            True
        ),

        "drift_proves_accuracy_degradation": (
            False
        ),

        "automatic_retraining_triggered": (
            False
        ),
    },

    "artifacts": {
        "monitoring_report": (
            str(
                MONITORING_REPORT_PATH
            )
        ),

        "monitoring_summary": (
            str(
                MONITORING_SUMMARY_PATH
            )
        ),
    },
}


with MONITORING_SUMMARY_PATH.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        summary,
        file,
        indent=2,
        sort_keys=True,
    )


# ------------------------------------------------------------
# 14. Human-readable result
# ------------------------------------------------------------

print(
    "\nPhase 3.3 TG3 complete."
)


print(
    "\nStable-control distributions:",
    len(
        stable_results
    )
)


print(
    "Stable-control alerts:",
    stable_summary[
        "alert_count"
    ]
)


print(
    "Stable-control maximum PSI:",
    stable_summary[
        "maximum_psi"
    ]
)


print(
    "\nInjected distributions:"
)


for column in drift_injections:

    print(
        " -",
        column
    )


print(
    "\nDrift-window alerts:",
    drifted_summary[
        "alert_count"
    ]
)


print(
    "Alert columns:",
    drifted_summary[
        "alert_columns"
    ]
)


print(
    "\nAccuracy degradation claimed:",
    False
)


print(
    "Automatic retraining triggered:",
    False
)


print(
    "\nCreated:",
    MONITORING_REPORT_PATH
)


print(
    "Created:",
    MONITORING_SUMMARY_PATH
)