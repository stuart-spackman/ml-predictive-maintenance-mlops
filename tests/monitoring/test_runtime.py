import numpy as np
import pandas as pd

from predictive_maintenance.monitoring.drift import (
    build_reference_cutpoints,
)

from predictive_maintenance.monitoring.runtime import (
    aggregate_drift_status,
    evaluate_runtime_window,
)


LOCKED_FEATURES = [
    "feature_a",
    "feature_b",
]


MODEL_SHA = "model-abc"

SPEC_SHA = "spec-abc"


def make_reference_dataframe():

    values = np.arange(
        1,
        31,
        dtype=float,
    )


    return pd.DataFrame(
        {
            "feature_a": (
                values
            ),

            "feature_b": (
                values * 2.0
            ),

            "predicted_rul": (
                100.0 - values
            ),
        }
    )


def make_prediction_dataframe(
    reference_df,
    *,
    model_sha=MODEL_SHA,
    spec_sha=SPEC_SHA,
):

    current = (
        reference_df.copy()
    )


    current[
        "model_artifact_sha256"
    ] = model_sha


    current[
        "locked_spec_sha256"
    ] = spec_sha


    return current


def make_bins(
    reference_df,
):

    return {
        column: (
            build_reference_cutpoints(
                reference_df[
                    column
                ]
            )
        )

        for column in [
            *LOCKED_FEATURES,
            "predicted_rul",
        ]
    }


def evaluate(
    reference_df,
    current_df,
):

    return (
        evaluate_runtime_window(
            reference_df=(
                reference_df
            ),

            prediction_events_df=(
                current_df
            ),

            locked_features=(
                LOCKED_FEATURES
            ),

            reference_bins=(
                make_bins(
                    reference_df
                )
            ),

            expected_model_sha256=(
                MODEL_SHA
            ),

            expected_locked_spec_sha256=(
                SPEC_SHA
            ),

            minimum_events=30,
            window_size=30,
            epsilon=1e-6,
            warning_threshold=0.10,
            alert_threshold=0.25,
        )
    )


def test_matching_window_is_stable():

    reference = (
        make_reference_dataframe()
    )


    current = (
        make_prediction_dataframe(
            reference
        )
    )


    result = (
        evaluate(
            reference,
            current,
        )
    )


    assert (
        result[
            "status"
        ]
        == "stable"
    )


def test_small_window_is_insufficient_data():

    reference = (
        make_reference_dataframe()
    )


    current = (
        make_prediction_dataframe(
            reference
        )
        .head(10)
    )


    result = (
        evaluate(
            reference,
            current,
        )
    )


    assert (
        result[
            "status"
        ]
        == "insufficient_data"
    )


def test_model_mismatch_is_reference_incompatible():

    reference = (
        make_reference_dataframe()
    )


    current = (
        make_prediction_dataframe(
            reference.head(10),
            model_sha="different-model",
        )
    )


    result = (
        evaluate(
            reference,
            current,
        )
    )


    assert (
        result[
            "status"
        ]
        == "reference_incompatible"
    )


def test_large_feature_shift_produces_alert():

    reference = (
        make_reference_dataframe()
    )


    current = (
        make_prediction_dataframe(
            reference
        )
    )


    current[
        "feature_a"
    ] = (
        current[
            "feature_a"
        ]
        + 500.0
    )


    result = (
        evaluate(
            reference,
            current,
        )
    )


    assert (
        result[
            "status"
        ]
        == "alert"
    )


def test_alert_wins_over_warning_and_stable():

    assert (
        aggregate_drift_status(
            [
                "stable",
                "warning",
                "alert",
            ]
        )
        == "alert"
    )