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
)

from predictive_maintenance.config import (
    DATASET_NAME,
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