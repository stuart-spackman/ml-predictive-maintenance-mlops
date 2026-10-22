## Phase 2.4 Handoff

Phase 2.4 established a reproducible serving and verification environment
for the predictive-maintenance application.

### Dependency environment

- Python support is declared in `pyproject.toml`.
- Direct dependencies are declared in `pyproject.toml`.
- A tested exact dependency resolution is retained in
  `requirements/constraints.txt`.
- A fresh development environment can be reconstructed using the
  `[dev]` extra and constraints file.

### Automated quality gate

The authoritative local and CI quality gate is:

`python -m pytest --cov=predictive_maintenance --cov-report=term-missing -q`

Branch coverage is enabled and the coverage floor is 60%.

### Container runtime

The FastAPI serving system is packaged in a Linux Docker image containing:

- the installed application package,
- runtime dependencies,
- the locked model specification,
- the fitted model artifact,
- the final-fit provenance record.

The image successfully initializes the real Phase 2.1 inference pipeline.

### Runtime verification

A fresh container successfully serves:

- `GET /health`
- `GET /metadata`
- `POST /predict`

through a published host/container port mapping.

### Continuous integration

GitHub Actions verifies the project on a clean Linux runner by:

- reconstructing the Python environment,
- checking dependency consistency,
- executing the Phase 2.3 quality gate,
- building the Docker image,
- smoke-testing the containerized inference runtime.

### Scope limits

Phase 2.4 does not claim:

- automatic production deployment,
- public cloud hosting,
- full training-environment containerization,
- monitoring or drift detection,
- scalability or high availability.