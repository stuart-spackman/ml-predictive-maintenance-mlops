# Predictive Maintenance MLOps — Project Story Map

## 1. One-Sentence Project Description

Built an end-to-end predictive-maintenance ML system using NASA C-MAPSS FD001 to predict turbofan-engine Remaining Useful Life, with leakage-aware model development, API serving, automated testing, containerization, model lifecycle governance, drift monitoring, and evidence-driven retraining logic.

---

## 2. Reader Takeaway

This project demonstrates the transition from an ML experiment to a production-oriented ML software system.

The central engineering themes are:

- causal and group-aware evaluation
- reproducible inference
- explicit model identity
- separation of experimentation, promotion, and deployment
- structured telemetry and drift monitoring
- delayed-label performance monitoring
- evidence-driven retraining

---

## 3. Problem

Input:

Complete engine history available through the current cycle.

Output:

Predicted Remaining Useful Life for the engine at its latest observed cycle.

Key causal constraint:

> At cycle t, pretend the universe ends at t.

---

## 4. Data and Evaluation

Dataset:

NASA C-MAPSS FD001.

Important methodology:

- engines are the grouping unit
- random row splitting is invalid
- temporal features use history only through the prediction cycle
- learned preprocessing remains inside the training boundary

---

## 5. Modeling Story

Explain:

1. baseline development
2. locked evaluation methodology
3. candidate screening
4. controlled tuning
5. challenger comparison
6. why improved experimental performance does not automatically change production serving

Only include exact metrics that are verified from retained project artifacts.

---

## 6. Production Inference

Raw complete engine history
→ validation
→ feature engineering
→ locked feature selection
→ fitted model
→ latest-cycle RUL prediction

Important property:

The same feature logic is reused rather than recreated independently for production serving.

---

## 7. API and Software Architecture

FastAPI endpoints:

- GET /health
- GET /metadata
- POST /predict

Discuss:

- artifact loaded once at startup
- explicit inference contract
- domain validation
- structured errors
- deterministic inference
- tests
- Docker
- CI

---

## 8. Model Lifecycle

Explain the distinctions:

candidate ≠ incumbent

registration ≠ validation

promotion ≠ deployment

registry champion ≠ necessarily actually served artifact

---

## 9. Monitoring

Prediction telemetry records:

- request identity
- actual served-model identity
- current engine/cycle context
- 36 model-input features
- predicted RUL
- latency

Monitoring evaluates:

- service health
- feature drift P(X)
- prediction drift P(ŷ)

PSI alerts are investigation signals, not automatic retraining triggers.

---

## 10. Delayed Labels and Performance

When ground-truth outcomes eventually become available:

historical prediction + true RUL
→ prediction error
→ RMSE / MAE

This separates distribution drift from direct predictive-performance degradation.

---

## 11. Retraining

Production anomaly
→ diagnose failing layer
→ determine whether problem is actually model-learning related
→ obtain trustworthy labeled evidence
→ authorize challenger fit if justified
→ evaluate
→ validate
→ promote
→ separately deploy

The incumbent remains immutable during challenger development.

---

## 12. Limitations

Be explicit:

- NASA C-MAPSS is a benchmark/simulated degradation dataset
- this system was not operated against a live industrial fleet
- no genuine production degradation event occurred
- no genuine production retraining event occurred
- drift and retraining workflows were validated through controlled scenarios
- the official test set was historically revealed and was not treated as a fresh repeated optimization mechanism later

---

## 13. Evidence and Reproducibility

Link readers to:

- important reports
- tests
- API implementation
- Dockerfile
- CI configuration
- model lifecycle artifacts
- monitoring artifacts
- retraining artifacts

Keep the main README concise; deeper evidence can live in dedicated documentation.