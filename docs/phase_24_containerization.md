# Phase 2.4 — Containerization

## Image Objective

Package the Phase 2.2 FastAPI serving application and frozen Phase 1
inference artifacts into a reproducible Linux-based runtime image.

## Base Runtime

- Python family: 3.13
- base image: `python:3.13-slim`

## Runtime Contents

The image contains:

- installed `predictive-maintenance` application,
- declared runtime Python dependencies,
- constrained known-good dependency resolution,
- frozen fitted model,
- locked model specification,
- final-fit provenance record.

The image intentionally excludes development-only tooling and local
developer environments.

## Application Entrypoint

`predictive_maintenance.api.main:app`

The default image command starts Uvicorn on container port 8000.

## Image Build

`docker build -t predictive-maintenance-api:0.1.0 .`

## Image-Level Verification

- image build: `<PASS/FAIL>`
- package import: `<PASS/FAIL>`
- required artifacts present: `<PASS/FAIL>`
- inference pipeline initialization: `<PASS/FAIL>`