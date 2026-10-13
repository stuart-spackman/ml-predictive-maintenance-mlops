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
    """
    Regression protection:

    A structurally valid but domain-invalid short history must be
    translated from Phase 2.1 InferenceInputError to HTTP 422 rather
    than escaping as a generic HTTP 500.
    """
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

import logging

def test_internal_inference_failure_returns_sanitized_500(
    api_client,
    valid_prediction_payload,
    override_inference_pipeline,
    caplog,
):

    caplog.set_level(
        logging.ERROR, 
        logger=(
            "predictive_maintenance.api.error_handlers"
        ),
    )

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

    assert (
        "Sensitive internal diagnostic detail."
        in caplog.text
    )

def test_unknown_request_field_returns_422(
    api_client,
    valid_prediction_payload,
):
    valid_prediction_payload[
        "actual_rul"
    ] = 123


    response = (
        api_client.post(
            "/predict",
            json=valid_prediction_payload,
        )
    )


    assert (
        response.status_code
        ==
        422
    )


    body = response.json()


    assert "detail" in body

class PredictionMustNotRunPipeline:
    """
    Test double used to prove that schema-invalid requests never reach
    the inference prediction call.
    """

    def predict(
        self,
        history_df,
    ):
        raise AssertionError(
            "Prediction should not run for a schema-invalid request."
        )

def test_schema_invalid_request_does_not_execute_prediction(
    api_client,
    valid_prediction_payload,
    override_inference_pipeline,
):
    override_inference_pipeline(
        PredictionMustNotRunPipeline()
    )


    del (
        valid_prediction_payload[
            "observations"
        ][0][
            "sensor_measurement_12"
        ]
    )


    response = (
        api_client.post(
            "/predict",
            json=valid_prediction_payload,
        )
    )


    assert (
        response.status_code
        ==
        422
    )