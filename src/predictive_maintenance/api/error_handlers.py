# Phase 2.2 — Task Group 5
# HTTP Error Translation
#
# Phase 2.1 owns inference error meaning.
# Phase 2.2 owns translation of known inference failures into HTTP responses.

import logging

from fastapi import (
    FastAPI,
    Request,
    status,
)

from fastapi.responses import (
    JSONResponse,
)

from predictive_maintenance.api.schemas import (
    ErrorResponse,
)

from predictive_maintenance.inference.errors import (
    InferenceError,
    InferenceInputError,
)


logger = logging.getLogger(
    __name__
)

# ------------------------------------------------------------
# 5G — Caller-correctable inference failures
# ------------------------------------------------------------

async def handle_inference_input_error(
    request: Request,
    exc: InferenceInputError,
) -> JSONResponse:
    """
    Translate a known Phase 2.1 caller-input failure into HTTP 422.

    The underlying error message is safe to expose because this
    exception category describes what the caller must correct.
    """

    logger.warning(
        "Rejected inference request at %s: %s",
        request.url.path,
        exc,
    )


    response = ErrorResponse(
        error_code=(
            "invalid_inference_request"
        ),
        message=str(
            exc
        ),
    )


    return JSONResponse(
        status_code=(
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ),
        content=response.model_dump(),
    )

# ------------------------------------------------------------
# 5H — Server-side inference failures
# ------------------------------------------------------------

async def handle_inference_error(
    request: Request,
    exc: InferenceError,
) -> JSONResponse:
    """
    Translate a known non-input Phase 2.1 inference failure into HTTP 500.

    Detailed internal exception information is logged server-side,
    while the public response remains intentionally generic.
    """

    logger.error(
        "Internal inference failure at %s: %s",
        request.url.path,
        exc,
        exc_info=(
            type(exc),
            exc,
            exc.__traceback__,
        ),
    )


    response = ErrorResponse(
        error_code=(
            "inference_service_error"
        ),
        message=(
            "The inference service could not complete the prediction."
        ),
    )


    return JSONResponse(
        status_code=(
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        content=response.model_dump(),
    )

# ------------------------------------------------------------
# 5J — Application registration
# ------------------------------------------------------------

def register_exception_handlers(
    app: FastAPI,
) -> None:
    """
    Register Phase 2.2 translations for known Phase 2.1 errors.
    """

    app.add_exception_handler(
        InferenceInputError,
        handle_inference_input_error,
    )

    app.add_exception_handler(
        InferenceError,
        handle_inference_error,
    )