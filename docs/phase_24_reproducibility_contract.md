# Phase 2.4 — Reproducibility Contract

## Objective

Phase 2.4 makes the predictive-maintenance serving application
reconstructable and verifiable outside the original developer environment.

A successful clean environment must be able to:

1. install the declared project dependencies,
2. access the required frozen model artifacts,
3. import the predictive-maintenance package,
4. run the Phase 2.3 automated quality gate,
5. start the FastAPI application,
6. serve the intended health, metadata, and prediction behavior.

The environment must not depend on undocumented machine-specific state.

## Current Environment Audit

### Repository

- project root: `<ACTUAL REPOSITORY ROOT>`
- project configuration: `pyproject.toml`
- source layout: `src/predictive_maintenance`

### Python

- Python version: `<ACTUAL>`
- Python executable: `<ACTUAL>`
- virtual environment active: `<YES/NO>`

### Package Management

- pip version: `<ACTUAL>`
- `python -m pip check`: `<RESULT>`
- declared dependencies audited: `<YES/NO>`
- installed dependency inventory captured: `<YES/NO>`

### Application

- FastAPI application entrypoint:
  `predictive_maintenance.api.main:app`

### Runtime Artifacts

Required frozen artifacts include:

- `reports/phase_16_locked_model_spec.json`
- `reports/phase_16_final_fitted_model.joblib`
- `reports/phase_16_final_fit_record.json`

Artifact paths should remain portable and repository-relative or otherwise
explicitly configured.

### Verification

Phase 2.3 quality gate:

`<ACTUAL QUALITY-GATE COMMAND>`

## Reproducibility Risks / Open Questions

The following areas require resolution or verification during Phase 2.4:

- Are all direct runtime dependencies declared explicitly?
- Are development/test dependencies separated appropriately?
- Are dependency version constraints sufficient for reconstruction?
- Is the supported Python version declared?
- Are all runtime artifact paths portable?
- Does the application rely on undocumented environment variables?
- Can a clean environment pass the Phase 2.3 quality gate?
- Can the application be packaged into a Docker image without depending on
  the developer machine?
- Can CI reconstruct the environment from repository-controlled inputs?

## Reproducibility Sources of Truth

The intended hierarchy is:

1. repository source code and project configuration,
2. declared Python/environment requirements,
3. frozen runtime artifacts,
4. documented runtime configuration,
5. automated quality gate.

The developer's existing `.venv` is evidence about the current working
environment but is not itself a reproducibility specification.