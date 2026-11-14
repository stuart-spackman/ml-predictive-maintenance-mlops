from __future__ import annotations

from collections.abc import (
    Iterable,
    Mapping,
)

import math

import numpy as np


REQUIRED_RETRAINING_CHECKS = (
    "served_model_identity_verified",
    "feature_pipeline_verified",
    "input_data_quality_verified",
    "outcome_label_quality_verified",
    "sample_representative",
    "new_labeled_training_data_available",
)


def _finite_array(
    values: Iterable[float],
) -> np.ndarray:

    array = np.asarray(
        list(values),
        dtype=float,
    )


    if not np.isfinite(
        array
    ).all():

        raise ValueError(
            "Performance values must "
            "all be finite."
        )


    return array


def regression_metrics(
    *,
    y_true: Iterable[float],
    y_pred: Iterable[float],
) -> dict:

    actual = (
        _finite_array(
            y_true
        )
    )


    predicted = (
        _finite_array(
            y_pred
        )
    )


    if (
        actual.size
        != predicted.size
    ):

        raise ValueError(
            "y_true and y_pred must "
            "have the same length."
        )


    if (
        actual.size
        == 0
    ):

        raise ValueError(
            "Cannot calculate regression "
            "metrics from zero observations."
        )


    errors = (
        predicted
        - actual
    )


    mae = float(
        np.mean(
            np.abs(
                errors
            )
        )
    )


    rmse = float(
        np.sqrt(
            np.mean(
                np.square(
                    errors
                )
            )
        )
    )


    return {
        "event_count": int(
            actual.size
        ),

        "rmse": (
            rmse
        ),

        "mae": (
            mae
        ),
    }


def evaluate_performance_window(
    *,
    y_true: Iterable[float],
    y_pred: Iterable[float],
    reference_rmse: float,
    minimum_labeled_events: int,
    relative_rmse_degradation_threshold: float,
    label_quality_verified: bool,
) -> dict:
    """
    Classify one labeled production-performance window.

    This determines performance evidence only.
    It does not independently authorize retraining.
    """

    if not (
        math.isfinite(
            reference_rmse
        )
        and reference_rmse > 0.0
    ):

        raise ValueError(
            "reference_rmse must be "
            "finite and positive."
        )


    if (
        minimum_labeled_events
        < 1
    ):

        raise ValueError(
            "minimum_labeled_events "
            "must be positive."
        )


    if (
        relative_rmse_degradation_threshold
        < 0.0
    ):

        raise ValueError(
            "Relative RMSE degradation "
            "threshold cannot be negative."
        )


    if not label_quality_verified:

        return {
            "status": (
                "label_quality_failure"
            ),

            "performance_evaluated": (
                False
            ),
        }


    actual = (
        _finite_array(
            y_true
        )
    )


    predicted = (
        _finite_array(
            y_pred
        )
    )


    if (
        actual.size
        != predicted.size
    ):

        raise ValueError(
            "y_true and y_pred must "
            "have the same length."
        )


    event_count = int(
        actual.size
    )


    if (
        event_count
        < minimum_labeled_events
    ):

        return {
            "status": (
                "insufficient_labels"
            ),

            "performance_evaluated": (
                False
            ),

            "labeled_events_available": (
                event_count
            ),

            "labeled_events_required": (
                minimum_labeled_events
            ),
        }


    metrics = (
        regression_metrics(
            y_true=actual,
            y_pred=predicted,
        )
    )


    degradation_threshold_rmse = (
        reference_rmse
        *
        (
            1.0
            +
            relative_rmse_degradation_threshold
        )
    )


    degraded = (
        metrics[
            "rmse"
        ]
        >=
        degradation_threshold_rmse
    )


    return {
        "status": (
            "performance_degraded"
            if degraded
            else
            "performance_stable"
        ),

        "performance_evaluated": (
            True
        ),

        "event_count": (
            event_count
        ),

        "reference_rmse": float(
            reference_rmse
        ),

        "degradation_threshold_rmse": float(
            degradation_threshold_rmse
        ),

        "relative_rmse_degradation_threshold": float(
            relative_rmse_degradation_threshold
        ),

        "current_rmse": (
            metrics[
                "rmse"
            ]
        ),

        "current_mae": (
            metrics[
                "mae"
            ]
        ),
    }


def assess_retraining_eligibility(
    *,
    performance_result: Mapping,
    investigation_checks: Mapping[
        str,
        bool,
    ],
) -> dict:
    """
    Convert performance evidence plus investigation results
    into a retraining-eligibility decision.

    Eligibility permits fitting a challenger only.
    """

    performance_status = (
        performance_result.get(
            "status"
        )
    )


    if (
        performance_status
        != "performance_degraded"
    ):

        return {
            "status": (
                "not_eligible_to_retrain"
            ),

            "reason": (
                "Validated performance degradation "
                "has not been established."
            ),
        }


    missing_checks = [
        check_name

        for check_name
        in REQUIRED_RETRAINING_CHECKS

        if check_name
        not in investigation_checks
    ]


    if missing_checks:

        raise ValueError(
            "Missing retraining investigation "
            f"checks: {missing_checks}"
        )


    failed_checks = [
        check_name

        for check_name
        in REQUIRED_RETRAINING_CHECKS

        if not bool(
            investigation_checks[
                check_name
            ]
        )
    ]


    if failed_checks:

        return {
            "status": (
                "investigate_before_retraining"
            ),

            "failed_checks": (
                failed_checks
            ),

            "retraining_authorized": (
                False
            ),
        }


    return {
        "status": (
            "eligible_to_retrain"
        ),

        "retraining_authorized": (
            True
        ),

        "meaning": (
            "Fit a new challenger; "
            "promotion and deployment remain "
            "separate decisions."
        ),
    }