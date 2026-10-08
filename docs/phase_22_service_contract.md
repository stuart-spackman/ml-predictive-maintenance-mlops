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

## POST /predict

### Purpose

Generate one latest-cycle RUL prediction using the completed Phase 2.1
inference pipeline.

### Request

The request contains:

- one `engine_id`,
- one or more raw `observations`,
- each observation contains:
  - `cycle`,
  - three operating settings,
  - 21 sensor measurements.

Pydantic validates the public network structure.

Phase 2.1 remains authoritative for inference-domain rules such as:

- exactly one engine,
- complete contiguous history,
- history beginning at cycle 1,
- minimum history length,
- finite numeric values.

### Response

A successful prediction returns:

- `engine_id`,
- `current_cycle`,
- `predicted_rul`.

### Boundary behavior

Phase 2.2 translates the public request representation into the canonical
Phase 2.1 dataframe representation.

Phase 2.2 does not duplicate temporal feature engineering, model feature
selection, artifact loading, or prediction logic.

## Prediction failure behavior

### API-schema validation failure

Examples:

- missing required field,
- invalid field type,
- unknown field.

Handled by FastAPI/Pydantic.

Expected HTTP status:

- `422 Unprocessable Entity`

### Inference-domain input failure

Examples:

- insufficient history,
- duplicate cycles,
- missing cycles,
- otherwise illegal Phase 2.1 engine history.

Handled authoritatively by Phase 2.1 and translated by Phase 2.2.

Expected HTTP status:

- `422 Unprocessable Entity`

Public error code:

- `invalid_inference_request`

### Internal inference failure

Examples:

- feature-construction failure,
- model-contract failure,
- invalid prediction output.

Expected HTTP status:

- `500 Internal Server Error`

Public error code:

- `inference_service_error`

Detailed internal exception information is logged server-side rather than
exposed to clients.

Critical artifact/model initialization failures should ordinarily prevent
application startup rather than first appearing during a prediction request.