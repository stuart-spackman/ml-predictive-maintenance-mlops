# Phase 2.2 — Model Serving with FastAPI Handoff

## Status

Phase 2.2 is complete.

The completed Phase 2.1 inference subsystem is now exposed through a
FastAPI HTTP service.

## Public HTTP interface

### GET /health

Reports operational service readiness.

Successful response:

- HTTP 200
- `status = "ok"`

### GET /metadata

Reports intentional public information about the running service and
verified inference pipeline.

Successful response includes:

- service version,
- dataset identifier,
- runtime model family,
- runtime model feature count.

### POST /predict

Accepts one raw FD001-style engine history and returns one latest-cycle
RUL prediction.

Successful response includes:

- engine ID,
- current cycle,
- predicted RUL.

## Request boundary

Pydantic owns the public HTTP request structure.

Phase 2.1 remains authoritative for inference-domain validity.

## Runtime lifecycle

The verified Phase 2.1 inference pipeline is loaded once during FastAPI
application startup and reused across requests handled by that application
process.

Prediction requests do not reload or refit the model.

## Representation boundary

Phase 2.2 adapters translate between:

- public Pydantic/JSON representations,
- Phase 2.1 dataframe/result representations.

Adapters do not duplicate inference-domain behavior.

## Error behavior

API/schema-invalid requests:

- HTTP 422

Inference-domain input failures:

- HTTP 422
- `error_code = "invalid_inference_request"`

Known internal inference failures:

- HTTP 500
- `error_code = "inference_service_error"`

Internal diagnostic details are retained in server logs and are not
unnecessarily exposed to clients.

## Dependency direction

Phase 2.2 depends on Phase 2.1.

Phase 2.1 remains independent of FastAPI and HTTP.

## Verification

Phase 2.2 includes automated API tests for:

- health,
- metadata,
- declared OpenAPI surface,
- successful prediction,
- HTTP/inference prediction parity,
- schema failures,
- domain-error translation,
- internal-error sanitization.

Real Uvicorn-backed smoke checks remain available for network-level
integration verification.