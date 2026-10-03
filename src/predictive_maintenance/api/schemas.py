# Phase 2.2 — Task Group 1
# Request & Response Schemas
#
# These models define the public HTTP data contract.
#
# They describe network-facing structure.
# They do NOT perform Phase 2.1 domain/model validation.

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

# ------------------------------------------------------------
# 1E — Shared API schema behavior
# ------------------------------------------------------------

class APIModel(BaseModel):
    """
    Base class for Phase 2.2 API schemas.

    Unknown fields are rejected so clients cannot silently send
    fields outside the documented API contract.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

# ------------------------------------------------------------
# 1F — One raw FD001 observation
# ------------------------------------------------------------

class EngineObservation(APIModel):
    """
    One raw observed operating cycle for one engine.

    The engine identifier lives at the PredictionRequest level,
    so it is not repeated inside every observation.
    """

    cycle: int = Field(
        description=(
            "Sequential operating-cycle index for the engine."
        )
    )

    op_setting_1: float
    op_setting_2: float
    op_setting_3: float

    sensor_measurement_1: float
    sensor_measurement_2: float
    sensor_measurement_3: float
    sensor_measurement_4: float
    sensor_measurement_5: float
    sensor_measurement_6: float
    sensor_measurement_7: float
    sensor_measurement_8: float
    sensor_measurement_9: float
    sensor_measurement_10: float
    sensor_measurement_11: float
    sensor_measurement_12: float
    sensor_measurement_13: float
    sensor_measurement_14: float
    sensor_measurement_15: float
    sensor_measurement_16: float
    sensor_measurement_17: float
    sensor_measurement_18: float
    sensor_measurement_19: float
    sensor_measurement_20: float
    sensor_measurement_21: float

# ------------------------------------------------------------
# 1G — Prediction request
# ------------------------------------------------------------

class PredictionRequest(APIModel):
    """
    Public HTTP representation of one engine-history prediction request.
    """

    engine_id: int = Field(
        description=(
            "Identifier of the engine represented by this request."
        )
    )

    observations: list[
        EngineObservation
    ] = Field(
        min_length=1,
        description=(
            "Raw engine observations through the current cycle."
        ),
    )

# ------------------------------------------------------------
# 1H — Prediction response
# ------------------------------------------------------------

class PredictionResponse(APIModel):
    """
    Successful HTTP prediction response.
    """

    engine_id: int

    current_cycle: int

    predicted_rul: float

# ------------------------------------------------------------
# 1I — Health response
# ------------------------------------------------------------

class HealthResponse(APIModel):
    """
    Basic service-health response.
    """

    status: Literal[
        "ok"
    ] = "ok"

# ------------------------------------------------------------
# 1I — Model metadata response
# ------------------------------------------------------------

class ModelMetadataResponse(APIModel):
    """
    Safe public metadata describing the running inference service.
    """

    service_version: str

    dataset: str

    model_family: str

    feature_count: int