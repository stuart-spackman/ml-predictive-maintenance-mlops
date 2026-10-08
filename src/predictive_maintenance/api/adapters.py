# Phase 2.2 — Task Group 4
# API ↔ Inference Boundary Adapters
#
# These functions translate between the public HTTP/Pydantic
# representation and the Phase 2.1 Python inference representation.
#
# They do NOT implement inference-domain validation, feature engineering,
# artifact loading, or model prediction.

import pandas as pd

from predictive_maintenance.api.schemas import (
    PredictionRequest,
    PredictionResponse,
)

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)

from predictive_maintenance.inference.pipeline import (
    PredictionResult,
)

from predictive_maintenance.inference.schema import (
    CYCLE_COLUMN,
    REQUIRED_RAW_HISTORY_COLUMNS,
)

# ------------------------------------------------------------
# 4E — PredictionRequest → canonical raw-history DataFrame
# ------------------------------------------------------------

def prediction_request_to_history_dataframe(
    request: PredictionRequest,
) -> pd.DataFrame:
    """
    Convert the public API prediction request into the canonical
    raw engine-history dataframe expected by Phase 2.1.

    API representation:
        engine_id
        observations[*].cycle
        observations[*].op_setting_*
        observations[*].sensor_measurement_*

    Phase 2.1 representation:
        unit_no
        cycles
        op_setting_*
        sensor_measurement_*

    This function only translates representation.
    Phase 2.1 remains responsible for domain validation.
    """

    records: list[dict] = []


    for observation in request.observations:

        observation_data = (
            observation.model_dump()
        )


        # The API deliberately calls this field `cycle`.
        # Phase 2.1's canonical FD001 representation calls it `cycles`.
        cycle = observation_data.pop(
            "cycle"
        )


        record = {
            GROUP_COLUMN: request.engine_id,
            CYCLE_COLUMN: cycle,
            **observation_data,
        }


        records.append(
            record
        )


    history_df = pd.DataFrame(
        records,
        columns=list(
            REQUIRED_RAW_HISTORY_COLUMNS
        ),
    )


    return history_df

# ------------------------------------------------------------
# 4I — PredictionResult → PredictionResponse
# ------------------------------------------------------------

def prediction_result_to_response(
    result: PredictionResult,
) -> PredictionResponse:
    """
    Convert the Phase 2.1 inference result into the public API
    response representation.
    """

    return PredictionResponse(
        engine_id=result.engine_id,
        current_cycle=result.current_cycle,
        predicted_rul=result.predicted_rul,
    )