# Phase 2.2 — Task Group 2
# FastAPI Application Startup & Persistent Inference Dependency
#
# The Phase 2.1 inference pipeline is created once during application
# startup and reused for the lifetime of this application process.

from contextlib import (
    asynccontextmanager,
)

import logging

from fastapi import FastAPI

from predictive_maintenance.inference.pipeline import (
    create_default_inference_pipeline,
)

from predictive_maintenance.api.routes import (
    router,
)

APP_TITLE = (
    "Predictive Maintenance RUL API"
)

APP_DESCRIPTION = (
    "HTTP service for generating remaining useful life predictions "
    "using the frozen NASA C-MAPSS FD001 model."
)

APP_VERSION = "0.1.0"


logger = logging.getLogger(
    __name__
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Manage application-level runtime resources.

    Startup:
        Load and verify the frozen Phase 2.1 inference pipeline once.

    Runtime:
        All endpoints reuse that same pipeline instance.

    Shutdown:
        Remove the application reference to the pipeline.
    """

    logger.info(
        "Initializing Phase 2.1 inference pipeline."
    )


    pipeline = (
        create_default_inference_pipeline()
    )


    app.state.inference_pipeline = (
        pipeline
    )


    logger.info(
        "Phase 2.1 inference pipeline initialized."
    )


    yield


    logger.info(
        "Releasing Phase 2.1 inference pipeline."
    )


    del app.state.inference_pipeline


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.include_router(
    router
)