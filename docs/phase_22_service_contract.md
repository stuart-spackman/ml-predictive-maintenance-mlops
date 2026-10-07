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

## Model runtime lifecycle

The Phase 2.1 inference pipeline is an application-level dependency.

At application startup:

1. the frozen Phase 1 artifacts are loaded,
2. artifact integrity is verified,
3. model/spec compatibility is verified,
4. one `RULInferencePipeline` is created,
5. the pipeline is stored in application state.

During normal request handling, endpoints reuse the existing pipeline.

Prediction requests must not reload or refit the model.

If the required frozen inference artifacts cannot be loaded or verified,
application startup should fail rather than expose an untrusted prediction
service.