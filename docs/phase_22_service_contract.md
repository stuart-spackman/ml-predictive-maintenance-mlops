# Phase 2.2 — Model Serving Service Contract

## Purpose

Expose the completed Phase 2.1 RUL inference capability through an HTTP API.

## Architectural boundary

Phase 2.2 owns:

- HTTP request handling,
- API request/response schemas,
- application startup and shutdown,
- HTTP endpoint routing,
- HTTP error translation,
- response serialization.

Phase 2.1 continues to own:

- engine-history domain validation,
- temporal feature engineering,
- locked feature selection,
- model-artifact verification,
- model loading,
- RUL prediction,
- inference-specific error classification.

## Dependency direction

Phase 2.2 depends on Phase 2.1.

Phase 2.1 must remain independent of FastAPI and HTTP.

## Planned endpoints

### GET /health

Reports whether the API service is operational.

### GET /metadata

Reports safe information about the deployed model/service configuration.

### POST /predict

Accepts one raw FD001-style engine history and returns the latest-cycle
predicted RUL.

## Prediction behavior

The API will not implement separate prediction logic.

It will delegate prediction to the Phase 2.1 inference pipeline.

## Non-goals

Phase 2.2 will not:

- train or refit models,
- tune hyperparameters,
- select a different model,
- recreate temporal feature engineering,
- silently modify model predictions,
- implement the Streamlit interface,
- containerize the application.