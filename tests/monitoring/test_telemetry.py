import json

import numpy as np

from predictive_maintenance.monitoring.telemetry import (
    JsonlTelemetryStore,
    build_prediction_event,
    build_service_event,
)


def test_jsonl_store_writes_one_valid_event_per_line(
    tmp_path,
):

    telemetry_path = (
        tmp_path
        / "events.jsonl"
    )


    store = (
        JsonlTelemetryStore(
            path=telemetry_path
        )
    )


    first_event = (
        build_service_event(
            request_id="request-1",
            method="POST",
            path="/predict",
            status_code=200,
            latency_ms=12.5,
        )
    )


    second_event = (
        build_prediction_event(
            request_id="request-1",

            model_identity={
                "source": "test",
                "model_artifact_sha256": "abc",
            },

            engine_id=1,
            current_cycle=20,
            predicted_rul=50.0,
            inference_latency_ms=8.0,

            model_input={
                "feature_a": np.float64(
                    1.25
                ),

                "feature_b": np.int64(
                    2
                ),
            },
        )
    )


    store.append(
        first_event
    )

    store.append(
        second_event
    )


    lines = (
        telemetry_path
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
    )


    assert len(
        lines
    ) == 2


    parsed = [
        json.loads(
            line
        )
        for line in lines
    ]


    assert (
        parsed[0][
            "event_type"
        ]
        == "service_request"
    )


    assert (
        parsed[1][
            "event_type"
        ]
        == "prediction"
    )


    assert (
        parsed[0][
            "request_id"
        ]
        ==
        parsed[1][
            "request_id"
        ]
    )


    assert (
        parsed[1][
            "model_input"
        ][
            "feature_a"
        ]
        == 1.25
    )


def test_service_event_marks_non_2xx_as_failure():

    event = (
        build_service_event(
            request_id="failed-request",
            method="POST",
            path="/predict",
            status_code=422,
            latency_ms=2.0,
        )
    )


    assert (
        event[
            "success"
        ]
        is False
    )


def test_try_append_does_not_raise_on_write_failure(
    tmp_path,
):

    # A directory used as the file path forces
    # the append attempt to fail.
    invalid_path = (
        tmp_path
        / "not_a_file"
    )


    invalid_path.mkdir()


    store = (
        JsonlTelemetryStore(
            path=invalid_path
        )
    )


    success = (
        store.try_append(
            {
                "event_type": "test"
            }
        )
    )


    assert (
        success
        is False
    )