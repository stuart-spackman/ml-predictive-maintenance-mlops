# Phase 2.2 — Task Group 5
# HTTP failure-behavior smoke checks.
#
# Run the FastAPI/Uvicorn server in another terminal first.

import json

from urllib.error import (
    HTTPError,
)

from urllib.request import (
    Request,
    urlopen,
)

from predictive_maintenance.config import (
    DATASET_NAME,
)

from predictive_maintenance.data.cmapss import (
    load_cmapss_subset,
)

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)


PREDICTION_URL = (
    "http://127.0.0.1:8000/predict"
)

def raw_row_to_api_observation(
    row,
) -> dict:

    observation = {
        "cycle": int(
            row["cycles"]
        ),
        "op_setting_1": float(
            row["op_setting_1"]
        ),
        "op_setting_2": float(
            row["op_setting_2"]
        ),
        "op_setting_3": float(
            row["op_setting_3"]
        ),
    }


    for sensor_number in range(
        1,
        22,
    ):

        column = (
            f"sensor_measurement_{sensor_number}"
        )


        observation[column] = float(
            row[column]
        )


    return observation

def send_prediction_request(
    payload: dict,
) -> tuple[
    int,
    dict,
]:
    """
    Send POST /predict and return status/body even when the server
    responds with a non-2xx HTTP status.
    """

    encoded_payload = (
        json.dumps(
            payload
        )
        .encode(
            "utf-8"
        )
    )


    request = Request(
        PREDICTION_URL,
        data=encoded_payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )


    try:

        with urlopen(
            request,
            timeout=30,
        ) as response:

            body = json.loads(
                response
                .read()
                .decode(
                    "utf-8"
                )
            )


            return (
                response.status,
                body,
            )


    except HTTPError as error:

        raw_body = (
            error
            .read()
            .decode(
                "utf-8",
                errors="replace",
            )
        )


        try:

            body = json.loads(
                raw_body
            )

        except json.JSONDecodeError:

            body = {
                "raw_body": raw_body
            }


        print()
        print(
            "DEBUG HTTP error status:",
            error.code,
        )

        print(
            "DEBUG raw response body:",
            repr(
                raw_body
            ),
        )


        return (
            error.code,
            body,
        )

def main() -> None:

    development_raw_df, _, _ = (
        load_cmapss_subset(
            DATASET_NAME
        )
    )


    engine_history = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(1)
        ]
        .head(10)
        .copy()
    )


    observations = [
        raw_row_to_api_observation(
            row
        )

        for _, row
        in engine_history.iterrows()
    ]


    print(
        "PHASE 2.2 HTTP FAILURE AUDIT"
    )

    print(
        "=" * 60
    )


    # --------------------------------------------------------
    # 1. Structurally valid, domain-invalid request
    # --------------------------------------------------------

    seven_cycle_payload = {
        "engine_id": 1,
        "observations": (
            observations[:7]
        ),
    }


    status_code, body = (
        send_prediction_request(
            seven_cycle_payload
        )
    )


    assert status_code == 422

    assert (
        body[
            "error_code"
        ]
        ==
        "invalid_inference_request"
    )


    print(
        "Seven-cycle domain failure: PASSED"
    )

    print(
        "HTTP status:",
        status_code,
    )

    print(
        "Response:",
        body,
    )

    # --------------------------------------------------------
    # 2. API-schema failure
    # --------------------------------------------------------

    missing_sensor_payload = {
        "engine_id": 1,
        "observations": [
            dict(
                observation
            )

            for observation
            in observations
        ],
    }


    del (
        missing_sensor_payload[
            "observations"
        ][0][
            "sensor_measurement_12"
        ]
    )


    status_code, body = (
        send_prediction_request(
            missing_sensor_payload
        )
    )


    assert status_code == 422


    print()

    print(
        "Missing-sensor schema failure: PASSED"
    )

    print(
        "HTTP status:",
        status_code,
    )

    print(
        "Response:",
        body,
    )


    print()

    print(
        "Phase 2.2 HTTP failure audit: PASSED"
    )

if __name__ == "__main__": 
    main()