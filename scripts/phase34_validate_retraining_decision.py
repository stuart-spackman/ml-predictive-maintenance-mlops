from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from predictive_maintenance.retraining.decision import (
    assess_retraining_eligibility,
    evaluate_performance_window,
)


POLICY_PATH = Path(
    "reports/phase_34_performance_retraining_policy.json"
)


REPORT_PATH = Path(
    "reports/phase_34_tg2_retraining_decision_validation.json"
)


with POLICY_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    policy = json.load(
        file
    )


minimum_events = int(
    policy[
        "performance_monitoring"
    ][
        "minimum_labeled_prediction_events"
    ]
)


relative_threshold = float(
    policy[
        "degradation_policy"
    ][
        "relative_rmse_increase_threshold"
    ]
)


# Synthetic reference used only to validate
# decision logic, not to make a claim about
# actual FD001 production performance.
reference_rmse = 10.0


# ------------------------------------------------------------
# Scenario 1 — insufficient labels
# ------------------------------------------------------------

insufficient = (
    evaluate_performance_window(
        y_true=np.arange(
            10,
            dtype=float,
        ),

        y_pred=(
            np.arange(
                10,
                dtype=float,
            )
            + 12.0
        ),

        reference_rmse=(
            reference_rmse
        ),

        minimum_labeled_events=(
            minimum_events
        ),

        relative_rmse_degradation_threshold=(
            relative_threshold
        ),

        label_quality_verified=True,
    )
)


# ------------------------------------------------------------
# Scenario 2 — stable performance
# ------------------------------------------------------------

stable_actual = np.arange(
    30,
    dtype=float,
)


stable = (
    evaluate_performance_window(
        y_true=(
            stable_actual
        ),

        y_pred=(
            stable_actual
            + 10.0
        ),

        reference_rmse=(
            reference_rmse
        ),

        minimum_labeled_events=(
            minimum_events
        ),

        relative_rmse_degradation_threshold=(
            relative_threshold
        ),

        label_quality_verified=True,
    )
)


# ------------------------------------------------------------
# Scenario 3 — degraded performance
# ------------------------------------------------------------

degraded_actual = np.arange(
    30,
    dtype=float,
)


degraded = (
    evaluate_performance_window(
        y_true=(
            degraded_actual
        ),

        y_pred=(
            degraded_actual
            + 12.0
        ),

        reference_rmse=(
            reference_rmse
        ),

        minimum_labeled_events=(
            minimum_events
        ),

        relative_rmse_degradation_threshold=(
            relative_threshold
        ),

        label_quality_verified=True,
    )
)


# ------------------------------------------------------------
# Scenario 4 — degradation but investigation incomplete
# ------------------------------------------------------------

blocked_decision = (
    assess_retraining_eligibility(
        performance_result=(
            degraded
        ),

        investigation_checks={
            "served_model_identity_verified": True,
            "feature_pipeline_verified": True,
            "input_data_quality_verified": False,
            "outcome_label_quality_verified": True,
            "sample_representative": True,
            "new_labeled_training_data_available": True,
        },
    )
)


# ------------------------------------------------------------
# Scenario 5 — degradation and investigation complete
# ------------------------------------------------------------

eligible_decision = (
    assess_retraining_eligibility(
        performance_result=(
            degraded
        ),

        investigation_checks={
            "served_model_identity_verified": True,
            "feature_pipeline_verified": True,
            "input_data_quality_verified": True,
            "outcome_label_quality_verified": True,
            "sample_representative": True,
            "new_labeled_training_data_available": True,
        },
    )
)


# ------------------------------------------------------------
# Assertions
# ------------------------------------------------------------

if (
    insufficient[
        "status"
    ]
    != "insufficient_labels"
):

    raise RuntimeError(
        "Insufficient-label scenario failed."
    )


if (
    stable[
        "status"
    ]
    != "performance_stable"
):

    raise RuntimeError(
        "Stable-performance scenario failed."
    )


if (
    degraded[
        "status"
    ]
    != "performance_degraded"
):

    raise RuntimeError(
        "Degraded-performance scenario failed."
    )


if (
    blocked_decision[
        "status"
    ]
    != "investigate_before_retraining"
):

    raise RuntimeError(
        "Investigation gate failed."
    )


if (
    eligible_decision[
        "status"
    ]
    != "eligible_to_retrain"
):

    raise RuntimeError(
        "Retraining-eligibility scenario failed."
    )


# ------------------------------------------------------------
# Evidence report
# ------------------------------------------------------------

report = {
    "phase": "3.4",
    "task_group": "TG2",

    "validation": (
        "passed"
    ),

    "important_claim": (
        "Synthetic values validate decision "
        "logic only; they do not represent "
        "actual production performance."
    ),

    "policy": {
        "minimum_labeled_events": (
            minimum_events
        ),

        "relative_rmse_degradation_threshold": (
            relative_threshold
        ),
    },

    "scenarios": {
        "insufficient_labels": (
            insufficient
        ),

        "stable_performance": (
            stable
        ),

        "degraded_performance": (
            degraded
        ),

        "degraded_but_investigation_failed": (
            blocked_decision
        ),

        "eligible_to_retrain": (
            eligible_decision
        ),
    },

    "decision_boundaries": {
        "drift_required_for_retraining": (
            False
        ),

        "labels_required_for_direct_performance_evidence": (
            True
        ),

        "performance_degradation_alone_bypasses_investigation": (
            False
        ),

        "eligible_to_retrain_means_challenger_may_be_fit": (
            True
        ),

        "eligible_to_retrain_means_deploy": (
            False
        ),
    },
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
    "\nPhase 3.4 TG2 retraining "
    "decision validation: PASSED"
)


print(
    "\nInsufficient scenario:",
    insufficient[
        "status"
    ]
)


print(
    "Stable scenario:",
    stable[
        "status"
    ]
)


print(
    "Degraded scenario:",
    degraded[
        "status"
    ]
)


print(
    "Incomplete investigation:",
    blocked_decision[
        "status"
    ]
)


print(
    "Completed investigation:",
    eligible_decision[
        "status"
    ]
)


print(
    "\nCreated:",
    REPORT_PATH
)