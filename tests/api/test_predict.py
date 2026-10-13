# Phase 2.2 — Task Group 6
# Automated successful-prediction API tests.

import math

import pytest

from predictive_maintenance.api.adapters import (
    prediction_request_to_history_dataframe,
)

from predictive_maintenance.api.main import (
    app,
)

from predictive_maintenance.api.schemas import (
    PredictionRequest,
)


def test_valid_prediction_request_returns_200(
    api_client,
    valid_prediction_payload,
):
    response = (
        api_client.post(
            "/predict",
            json=valid_prediction_payload,
        )
    )


    assert response.status_code == 200


    body = response.json()


    assert (
        body[
            "engine_id"
        ]
        ==
        1
    )

    assert (
        body[
            "current_cycle"
        ]
        ==
        20
    )

    assert math.isfinite(
        body[
            "predicted_rul"
        ]
    )

    body = response.json()

    assert set(
        body
    ) == {
        "engine_id",
        "current_cycle",
        "predicted_rul",
    }

def test_http_prediction_matches_phase_21_pipeline(
    api_client,
    valid_prediction_payload,
):
    """
    Verify that the HTTP layer preserves the prediction produced by
    the authoritative Phase 2.1 pipeline.
    """

    response = (
        api_client.post(
            "/predict",
            json=valid_prediction_payload,
        )
    )


    assert response.status_code == 200


    # Reconstruct the same Phase 2.1 input through our public adapter.

    request_model = (
        PredictionRequest
        .model_validate(
            valid_prediction_payload
        )
    )


    history_df = (
        prediction_request_to_history_dataframe(
            request_model
        )
    )


    expected_result = (
        app.state
        .inference_pipeline
        .predict(
            history_df
        )
    )


    assert (
        response.json()[
            "predicted_rul"
        ]
        ==
        pytest.approx(
            expected_result.predicted_rul
        )
    )

from copy import (
    deepcopy,
)

def test_prediction_is_invariant_to_observation_order(
    api_client,
    valid_prediction_payload,
):
    ordered_response = (
        api_client.post(
            "/predict",
            json=valid_prediction_payload,
        )
    )


    assert (
        ordered_response.status_code
        ==
        200
    )


    reversed_payload = deepcopy(
        valid_prediction_payload
    )


    reversed_payload[
        "observations"
    ].reverse()


    reversed_response = (
        api_client.post(
            "/predict",
            json=reversed_payload,
        )
    )


    assert (
        reversed_response.status_code
        ==
        200
    )


    ordered_body = (
        ordered_response.json()
    )

    reversed_body = (
        reversed_response.json()
    )


    assert (
        reversed_body[
            "engine_id"
        ]
        ==
        ordered_body[
            "engine_id"
        ]
    )


    assert (
        reversed_body[
            "current_cycle"
        ]
        ==
        ordered_body[
            "current_cycle"
        ]
    )


    assert (
        reversed_body[
            "predicted_rul"
        ]
        ==
        pytest.approx(
            ordered_body[
                "predicted_rul"
            ]
        )
    )