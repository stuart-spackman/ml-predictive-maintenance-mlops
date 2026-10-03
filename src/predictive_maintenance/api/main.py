# Phase 2.2 — Task Group 0
# FastAPI Application Setup
#
# This module defines the HTTP-facing application.
#
# Phase 2.2 will depend on the finished Phase 2.1 inference subsystem.
# The inference subsystem must NOT depend on FastAPI.

from fastapi import FastAPI


APP_TITLE = (
    "Predictive Maintenance RUL API"
)

APP_DESCRIPTION = (
    "HTTP service for generating remaining useful life predictions "
    "using the frozen NASA C-MAPSS FD001 model."
)

APP_VERSION = "0.1.0"


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)