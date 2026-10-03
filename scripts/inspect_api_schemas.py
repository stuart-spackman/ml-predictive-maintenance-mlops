# Phase 2.2 — Task Group 1
# Inspect Pydantic request/response schema behavior.

from copy import deepcopy

from pydantic import (
    ValidationError,
)

from predictive_maintenance.api.schemas import (
    PredictionRequest,
    PredictionResponse,
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


def raw_row_to_api_observation(
    row,
) -> dict:
    """
    Convert one canonical FD001 dataframe row into the public API
    observation representation.

    This helper exists only for this inspection script.
    """

    payload = {
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

        payload[column] = float(
            row[column]
        )


    return payload

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


    valid_payload = {
        "engine_id": 1,
        "observations": [
            raw_row_to_api_observation(
                row
            )

            for _, row
            in engine_history.iterrows()
        ],
    }


    print(
        "PHASE 2.2 API SCHEMA AUDIT"
    )

    print(
        "=" * 60
    )


    # --------------------------------------------------------
    # 1. Valid request
    # --------------------------------------------------------

    request = (
        PredictionRequest
        .model_validate(
            valid_payload
        )
    )


    assert request.engine_id == 1

    assert len(
        request.observations
    ) == 10


    print(
        "Valid PredictionRequest: PASSED"
    )


    # --------------------------------------------------------
    # 2. Missing required field
    # --------------------------------------------------------

    missing_field_payload = deepcopy(
        valid_payload
    )

    del (
        missing_field_payload[
            "observations"
        ][0][
            "sensor_measurement_12"
        ]
    )


    try:

        PredictionRequest.model_validate(
            missing_field_payload
        )

    except ValidationError:

        print(
            "Missing required sensor rejected: PASSED"
        )

    else:

        raise AssertionError(
            "Missing required sensor was unexpectedly accepted."
        )


    # --------------------------------------------------------
    # 3. Unknown field
    # --------------------------------------------------------

    extra_field_payload = deepcopy(
        valid_payload
    )

    extra_field_payload[
        "observations"
    ][0][
        "actual_rul"
    ] = 99.0


    try:

        PredictionRequest.model_validate(
            extra_field_payload
        )

    except ValidationError:

        print(
            "Unexpected field rejected: PASSED"
        )

    else:

        raise AssertionError(
            "Unexpected field was unexpectedly accepted."
        )


    # --------------------------------------------------------
    # 4. Demonstrate schema vs domain validation
    # --------------------------------------------------------
    #
    # Duplicate cycles remain structurally legal to Pydantic.
    # Phase 2.1 will reject them later.

    duplicate_cycle_payload = deepcopy(
        valid_payload
    )

    duplicate_cycle_payload[
        "observations"
    ][1][
        "cycle"
    ] = 1


    structurally_valid_request = (
        PredictionRequest
        .model_validate(
            duplicate_cycle_payload
        )
    )


    assert (
        structurally_valid_request
        .observations[0]
        .cycle
        ==
        structurally_valid_request
        .observations[1]
        .cycle
    )


    print(
        "Duplicate cycle passes Pydantic structural validation: "
        "YES — expected"
    )

    print(
        "Phase 2.1 domain validation must reject it later."
    )


    # --------------------------------------------------------
    # 5. Response serialization
    # --------------------------------------------------------

    response = PredictionResponse(
        engine_id=1,
        current_cycle=10,
        predicted_rul=87.5,
    )


    print()

    print(
        "PredictionResponse Python form:"
    )

    print(
        response.model_dump()
    )


    print()

    print(
        "PredictionResponse JSON form:"
    )

    print(
        response.model_dump_json()
    )


    print()

    print(
        "Phase 2.2 API schema audit: PASSED"
    )


if __name__ == "__main__":
    main()