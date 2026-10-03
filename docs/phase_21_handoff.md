# Phase 2.1 — Production-Style Inference Pipeline Handoff

## Status

Phase 2.1 is complete.

The inference subsystem accepts one raw FD001-style engine history and
produces one RUL prediction for the latest eligible cycle using the frozen
Phase 1 model.

## Public Python interface

Primary construction:

```python
from predictive_maintenance.inference.pipeline import (
    create_default_inference_pipeline,
)

pipeline = create_default_inference_pipeline()