FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PREDICTIVE_MAINTENANCE_PROJECT_ROOT=/app

WORKDIR /app

COPY pyproject.toml README.md ./
COPY requirements/constraints.txt requirements/constraints.txt
COPY src/ src/

COPY reports/phase_16_locked_model_spec.json reports/phase_16_locked_model_spec.json
COPY reports/phase_16_final_fitted_model.joblib reports/phase_16_final_fitted_model.joblib
COPY reports/phase_16_final_fit_record.json reports/phase_16_final_fit_record.json

RUN python -m pip install \
    --no-cache-dir \
    -c requirements/constraints.txt \
    .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "predictive_maintenance.api.main:app", "--host", "0.0.0.0", "--port", "8000"]