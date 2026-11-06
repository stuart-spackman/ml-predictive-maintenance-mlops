from __future__ import annotations

import json
import math
from pathlib import Path


TELEMETRY_PATH = Path(
    "runtime/telemetry/events.jsonl"
)


REPORT_PATH = Path(
    "reports/phase_33_tg1_telemetry_validation.json"
)


if not TELEMETRY_PATH.exists():

    raise FileNotFoundError(
        "No telemetry file exists yet. "
        "Send at least one successful "
        "/predict request first."
    )


events = [
    json.loads(
        line
    )
    for line
    in TELEMETRY_PATH
    .read_text(
        encoding="utf-8"
    )
    .splitlines()
    if line.strip()
]


prediction_events = [
    event
    for event in events
    if (
        event.get(
            "event_type"
        )
        == "prediction"
    )
]


service_events = [
    event
    for event in events
    if (
        event.get(
            "event_type"
        )
        == "service_request"
    )
]


if not prediction_events:

    raise RuntimeError(
        "No successful prediction "
        "telemetry event was found."
    )


prediction = (
    prediction_events[-1]
)


matching_service_events = [
    event
    for event in service_events
    if (
        event.get(
            "request_id"
        )
        ==
        prediction.get(
            "request_id"
        )
    )
]


if len(
    matching_service_events
) != 1:

    raise RuntimeError(
        "Expected exactly one matching "
        "service event for latest prediction."
    )


service = (
    matching_service_events[0]
)


model_input = (
    prediction[
        "model_input"
    ]
)


if len(
    model_input
) != 36:

    raise RuntimeError(
        "Prediction telemetry does not "
        "contain exactly 36 model inputs."
    )


if not math.isfinite(
    float(
        prediction[
            "predicted_rul"
        ]
    )
):

    raise RuntimeError(
        "Telemetry contains a non-finite "
        "RUL prediction."
    )


if not service[
    "success"
]:

    raise RuntimeError(
        "Matching service event was "
        "not successful."
    )


if (
    service[
        "status_code"
    ]
    != 200
):

    raise RuntimeError(
        "Expected HTTP 200 for matching "
        "successful prediction event."
    )


if (
    float(
        service[
            "latency_ms"
        ]
    )
    < 0
):

    raise RuntimeError(
        "Service latency cannot be negative."
    )


if (
    float(
        prediction[
            "inference_latency_ms"
        ]
    )
    < 0
):

    raise RuntimeError(
        "Inference latency cannot be negative."
    )


served_model = (
    prediction[
        "served_model"
    ]
)


for hash_key in [
    "model_artifact_sha256",
    "locked_spec_sha256",
]:

    value = (
        served_model[
            hash_key
        ]
    )


    if len(
        value
    ) != 64:

        raise RuntimeError(
            f"{hash_key} does not look "
            "like SHA-256."
        )


result = {
    "phase": "3.3",
    "task_group": "TG1",

    "telemetry_validation": (
        "passed"
    ),

    "latest_request_id": (
        prediction[
            "request_id"
        ]
    ),

    "service_event": {
        "status_code": (
            service[
                "status_code"
            ]
        ),

        "success": (
            service[
                "success"
            ]
        ),

        "latency_ms": (
            service[
                "latency_ms"
            ]
        ),
    },

    "prediction_event": {
        "engine_id": (
            prediction[
                "engine_id"
            ]
        ),

        "current_cycle": (
            prediction[
                "current_cycle"
            ]
        ),

        "predicted_rul_finite": (
            True
        ),

        "inference_latency_ms": (
            prediction[
                "inference_latency_ms"
            ]
        ),

        "model_input_feature_count": (
            len(
                model_input
            )
        ),

        "served_model": (
            served_model
        ),
    },
}


REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


REPORT_PATH.write_text(
    json.dumps(
        result,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print(
    "Phase 3.3 TG1 telemetry validation: PASSED"
)


print(
    "Request ID:",
    prediction[
        "request_id"
    ]
)


print(
    "Feature count:",
    len(
        model_input
    )
)


print(
    "Created:",
    REPORT_PATH
)