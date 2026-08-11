# Predictive Maintenance + MLOps

An end-to-end predictive maintenance project using the NASA C-MAPSS
turbofan engine degradation dataset.

The initial modeling task predicts remaining useful life (RUL) for
engines in the FD001 dataset.

## Project Status

Currently developing:

- Data understanding and exploratory analysis
- Leakage-safe feature engineering
- Baseline RUL modeling

Planned later stages include:

- Experiment tracking
- Model serving with FastAPI
- Containerization
- Automated testing and CI
- Monitoring
- Model versioning and promotion

## Repository Structure

```text
data/           Dataset storage and derived datasets
notebooks/      Exploratory and experimental notebooks
reports/        Saved figures and analysis outputs
src/            Reusable project Python package
tests/          Automated tests