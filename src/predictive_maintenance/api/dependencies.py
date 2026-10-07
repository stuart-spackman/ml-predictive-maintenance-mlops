# Phase 2.2 — Task Group 2
# FastAPI dependency accessors.
#
# HTTP endpoints should obtain shared application resources through
# these dependency functions rather than manually reaching into
# app.state throughout the codebase.

from typing import Annotated

from fastapi import (
    Depends,
    Request,
)

from predictive_maintenance.inference.pipeline import (
    RULInferencePipeline,
)


def get_inference_pipeline(
    request: Request,
) -> RULInferencePipeline:
    """
    Return the application-level Phase 2.1 inference pipeline.

    The pipeline should already have been created by the FastAPI
    lifespan startup logic.
    """

    pipeline = getattr(
        request.app.state,
        "inference_pipeline",
        None,
    )


    if pipeline is None:

        raise RuntimeError(
            "Inference pipeline is unavailable. "
            "Application startup may not have completed successfully."
        )


    return pipeline


InferencePipelineDependency = Annotated[
    RULInferencePipeline,
    Depends(
        get_inference_pipeline
    ),
]