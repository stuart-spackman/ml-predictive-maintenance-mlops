# Phase 2.2 — Task Group 3
# Health & Model-Metadata Routes
#
# These routes expose safe service-level information over HTTP.
#
# They do not implement model training, feature engineering,
# artifact loading, or prediction logic.

from fastapi import (
    APIRouter,
    Request,
)

from predictive_maintenance.api.dependencies import (
    InferencePipelineDependency,
)

from predictive_maintenance.api.schemas import (
    HealthResponse,
    ModelMetadataResponse,
    PredictionRequest,
    PredictionResponse,
)

from predictive_maintenance.config import (
    DATASET_NAME,
)

from predictive_maintenance.api.adapters import (
    prediction_request_to_history_dataframe,
    prediction_result_to_response,
)

router = APIRouter()

# ------------------------------------------------------------
# 3E — Service health
# ------------------------------------------------------------

@router.get(
    "/health",
    response_model=HealthResponse,
)
def get_health(
    _pipeline: InferencePipelineDependency,
) -> HealthResponse:
    """
    Report that the prediction service is operational.

    Resolving the inference-pipeline dependency confirms that the
    application-level serving resource is available.
    """

    return HealthResponse(
        status="ok"
    )

# ------------------------------------------------------------
# 3N — Safe public model metadata
# ------------------------------------------------------------

@router.get(
    "/metadata",
    response_model=ModelMetadataResponse,
)
def get_model_metadata(
    request: Request,
    pipeline: InferencePipelineDependency,
) -> ModelMetadataResponse:
    """
    Return safe metadata describing the running prediction service
    and its verified frozen model.
    """

    return ModelMetadataResponse(
        service_version=(
            request.app.version
        ),
        dataset=DATASET_NAME,
        model_family=(
            pipeline.model_family
        ),
        feature_count=(
            pipeline.feature_count
        ),
    )

# ------------------------------------------------------------
# 4L — RUL prediction
# ------------------------------------------------------------

@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict_rul(
    prediction_request: PredictionRequest,
    pipeline: InferencePipelineDependency,
) -> PredictionResponse:
    """
    Generate one latest-cycle RUL prediction from one raw engine history.

    HTTP/Pydantic concerns are handled here and in the API adapter.

    Domain validation, temporal feature engineering, locked feature
    selection, artifact usage, and model prediction remain Phase 2.1
    responsibilities.
    """

    history_df = (
        prediction_request_to_history_dataframe(
            prediction_request
        )
    )


    result = pipeline.predict(
        history_df
    )


    return (
        prediction_result_to_response(
            result
        )
    )