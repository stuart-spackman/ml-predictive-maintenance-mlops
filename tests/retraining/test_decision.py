import numpy as np

from predictive_maintenance.retraining.decision import (
    assess_retraining_eligibility,
    evaluate_performance_window,
    regression_metrics,
)


def test_regression_metrics():

    actual = np.array(
        [
            10.0,
            20.0,
            30.0,
        ]
    )


    predicted = np.array(
        [
            12.0,
            18.0,
            33.0,
        ]
    )


    result = (
        regression_metrics(
            y_true=actual,
            y_pred=predicted,
        )
    )


    assert (
        result[
            "event_count"
        ]
        == 3
    )


    assert (
        result[
            "rmse"
        ]
        > 0.0
    )


    assert (
        result[
            "mae"
        ]
        > 0.0
    )


def test_bad_label_quality_blocks_evaluation():

    result = (
        evaluate_performance_window(
            y_true=[1.0] * 30,
            y_pred=[1.0] * 30,
            reference_rmse=10.0,
            minimum_labeled_events=30,
            relative_rmse_degradation_threshold=0.10,
            label_quality_verified=False,
        )
    )


    assert (
        result[
            "status"
        ]
        == "label_quality_failure"
    )


def test_too_few_labels_is_insufficient():

    result = (
        evaluate_performance_window(
            y_true=[1.0] * 10,
            y_pred=[2.0] * 10,
            reference_rmse=10.0,
            minimum_labeled_events=30,
            relative_rmse_degradation_threshold=0.10,
            label_quality_verified=True,
        )
    )


    assert (
        result[
            "status"
        ]
        == "insufficient_labels"
    )


def test_stable_performance_window():

    actual = np.arange(
        30,
        dtype=float,
    )


    predicted = (
        actual
        + 10.0
    )


    result = (
        evaluate_performance_window(
            y_true=actual,
            y_pred=predicted,
            reference_rmse=10.0,
            minimum_labeled_events=30,
            relative_rmse_degradation_threshold=0.10,
            label_quality_verified=True,
        )
    )


    assert (
        result[
            "status"
        ]
        == "performance_stable"
    )


def test_degraded_performance_window():

    actual = np.arange(
        30,
        dtype=float,
    )


    predicted = (
        actual
        + 12.0
    )


    result = (
        evaluate_performance_window(
            y_true=actual,
            y_pred=predicted,
            reference_rmse=10.0,
            minimum_labeled_events=30,
            relative_rmse_degradation_threshold=0.10,
            label_quality_verified=True,
        )
    )


    assert (
        result[
            "status"
        ]
        == "performance_degraded"
    )


def test_degradation_plus_failed_check_requires_investigation():

    performance_result = {
        "status": (
            "performance_degraded"
        )
    }


    checks = {
        "served_model_identity_verified": True,
        "feature_pipeline_verified": True,
        "input_data_quality_verified": False,
        "outcome_label_quality_verified": True,
        "sample_representative": True,
        "new_labeled_training_data_available": True,
    }


    decision = (
        assess_retraining_eligibility(
            performance_result=(
                performance_result
            ),

            investigation_checks=(
                checks
            ),
        )
    )


    assert (
        decision[
            "status"
        ]
        == "investigate_before_retraining"
    )


def test_degradation_plus_all_checks_allows_retraining():

    performance_result = {
        "status": (
            "performance_degraded"
        )
    }


    checks = {
        "served_model_identity_verified": True,
        "feature_pipeline_verified": True,
        "input_data_quality_verified": True,
        "outcome_label_quality_verified": True,
        "sample_representative": True,
        "new_labeled_training_data_available": True,
    }


    decision = (
        assess_retraining_eligibility(
            performance_result=(
                performance_result
            ),

            investigation_checks=(
                checks
            ),
        )
    )


    assert (
        decision[
            "status"
        ]
        == "eligible_to_retrain"
    )


    assert (
        decision[
            "retraining_authorized"
        ]
        is True
    )