# Phase 2.2 — Task Group 2
# FastAPI Application Startup & Persistent Inference Dependency
#
# The Phase 2.1 inference pipeline is created once during application
# startup and reused for the lifetime of this application process.

from contextlib import (
    asynccontextmanager,
)

import logging

from time import (
    perf_counter,
)

from uuid import (
    uuid4,
)

from fastapi import (
    FastAPI,
    Request,
)

from predictive_maintenance.monitoring.telemetry import (
    JsonlTelemetryStore,
    build_served_model_identity,
    build_service_event,
)

from predictive_maintenance.inference.pipeline import (
    create_default_inference_pipeline,
)

from predictive_maintenance.api.routes import (
    router,
)

from predictive_maintenance.api.error_handlers import (
    register_exception_handlers,
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

    telemetry_store = (
        JsonlTelemetryStore()
    )
    
    
    served_model_identity = (
        build_served_model_identity()
    )
    
    app.state.inference_pipeline = (
        pipeline
    )

    app.state.telemetry_store = (
        telemetry_store
    )


    app.state.served_model_identity = (
        served_model_identity
    )


    logger.info(
        "Phase 2.1 inference pipeline initialized."
    )


    yield


    logger.info(
        "Releasing Phase 2.1 inference pipeline."
    )


    del app.state.inference_pipeline

    del app.state.telemetry_store

    del app.state.served_model_identity

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

register_exception_handlers(
    app
)

app.include_router(
    router
)

@app.middleware(
    "http"
)
async def record_predict_request_telemetry(
    request: Request,
    call_next,
):
    """
    Record one service-health event for every /predict request.

    This captures successful predictions, inference failures,
    and FastAPI/Pydantic request rejections that reach the
    application.
    """

    if (
        request.url.path
        != "/predict"
    ):

        return await call_next(
            request
        )


    request_id = str(
        uuid4()
    )


    request.state.request_id = (
        request_id
    )


    started = (
        perf_counter()
    )


    status_code = 500


    try:

        response = await call_next(
            request
        )


        status_code = (
            response.status_code
        )


        response.headers[
            "X-Request-ID"
        ] = request_id


        return response


    finally:

        latency_ms = (
            (
                perf_counter()
                - started
            )
            * 1000.0
        )


        telemetry_store = getattr(
            request.app.state,
            "telemetry_store",
            None,
        )


        if (
            telemetry_store
            is not None
        ):

            telemetry_store.try_append(
                build_service_event(
                    request_id=(
                        request_id
                    ),

                    method=(
                        request.method
                    ),

                    path=(
                        request.url.path
                    ),

                    status_code=(
                        status_code
                    ),

                    latency_ms=(
                        latency_ms
                    ),
                )
            )