# Phase 2.2 — Task Group 4
# End-to-end HTTP prediction smoke check.
#
# IMPORTANT:
# Run the FastAPI/Uvicorn server in another terminal before running
# this script.

import json
from urllib.request import (
    Request,
    urlopen,
)

import numpy as np

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
    """
    Convert one canonical FD001 dataframe row into the public
    EngineObservation representation used by the HTTP API.
    """

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


def main() -> None:

    development_raw_df, _, _ = (
        load_cmapss_subset(
            DATASET_NAME
        )
    )


    engine_id = 1


    engine_history = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(
                engine_id
            )
        ]
        .head(20)
        .copy()
    )


    payload = {
        "engine_id": engine_id,
        "observations": [
            raw_row_to_api_observation(
                row
            )

            for _, row
            in engine_history.iterrows()
        ],
    }


    encoded_payload = (
        json.dumps(
            payload
        )
        .encode(
            "utf-8"
        )
    )


    http_request = Request(
        PREDICTION_URL,
        data=encoded_payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )


    print(
        "PHASE 2.2 /predict HTTP SMOKE CHECK"
    )

    print(
        "=" * 60
    )


    with urlopen(
        http_request,
        timeout=30,
    ) as response:

        response_body = (
            json.loads(
                response
                .read()
                .decode(
                    "utf-8"
                )
            )
        )


        assert response.status == 200

        assert (
            response_body[
                "engine_id"
            ]
            ==
            engine_id
        )

        assert (
            response_body[
                "current_cycle"
            ]
            ==
            20
        )

        assert np.isfinite(
            response_body[
                "predicted_rul"
            ]
        )


        print(
            "HTTP status:",
            response.status,
        )

        print(
            "Engine ID:",
            response_body[
                "engine_id"
            ],
        )

        print(
            "Current cycle:",
            response_body[
                "current_cycle"
            ],
        )

        print(
            "Predicted RUL:",
            response_body[
                "predicted_rul"
            ],
        )


    print()

    print(
        "Phase 2.2 /predict HTTP smoke check: PASSED"
    )


if __name__ == "__main__":
    main()