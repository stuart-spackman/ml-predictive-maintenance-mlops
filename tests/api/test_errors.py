# Phase 2.2 — Task Group 6
# Automated HTTP failure-behavior tests.

from copy import (
    deepcopy,
)

from predictive_maintenance.api.dependencies import (
    get_inference_pipeline,
)

from predictive_maintenance.api.main import (
    app,
)

from predictive_maintenance.inference.errors import (
    InferencePredictionError,
)


def test_missing_sensor_returns_422(
    api_client,
    valid_prediction_payload,
):
    payload = deepcopy(
        valid_prediction_payload
    )


    del (
        payload[
            "observations"
        ][0][
            "sensor_measurement_12"
        ]
    )


    response = (
        api_client.post(
            "/predict",
            json=payload,
        )
    )


    assert response.status_code == 422


    body = response.json()


    assert "detail" in body


    assert any(
        error[
            "loc"
        ][-1]
        ==
        "sensor_measurement_12"

        for error
        in body[
            "detail"
        ]
    )

def test_short_history_returns_domain_422(
    api_client,
    valid_prediction_payload,
):
    payload = deepcopy(
        valid_prediction_payload
    )


    payload[
        "observations"
    ] = (
        payload[
            "observations"
        ][:7]
    )


    response = (
        api_client.post(
            "/predict",
            json=payload,
        )
    )


    assert response.status_code == 422


    assert response.json()[
        "error_code"
    ] == (
        "invalid_inference_request"
    )


    assert (
        "10 cycles"
        in response.json()[
            "message"
        ]
    )

class FailingPredictionPipeline:
    """
    Test double that deliberately simulates a known internal
    inference failure.
    """

    def predict(
        self,
        history_df,
    ):
        raise InferencePredictionError(
            "Sensitive internal diagnostic detail."
        )

def test_internal_inference_failure_returns_sanitized_500(
    api_client,
    valid_prediction_payload,
    override_inference_pipeline,
):

    override_inference_pipeline(
        FailingPredictionPipeline()
    )


    response = (
        api_client.post(
            "/predict",
            json=valid_prediction_payload,
        )
    )


    assert response.status_code == 500


    assert response.json() == {
        "error_code": (
            "inference_service_error"
        ),
        "message": (
            "The inference service could not complete the prediction."
        ),
    }


    assert (
        "Sensitive internal diagnostic detail."
        not in response.text
    )