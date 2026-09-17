# Phase 2.1 — Task Group 0
# Inference Contract
#
# This module defines WHAT the inference system promises to accept and produce.
#
# It does not yet:
# - validate actual requests,
# - construct temporal features,
# - load a model,
# - or generate predictions.
#
# Those capabilities will be added in later task groups.

from dataclasses import dataclass

from predictive_maintenance.features.feature_sets import (
    EXPANDED_TEMPORAL_WINDOW,
)


@dataclass(frozen=True)
class InferenceContract:
    """
    High-level behavioral contract for the Phase 2.1 inference pipeline.

    `frozen=True` means these values cannot be accidentally modified after
    the object is created.
    """

    # One request contains observations from one engine only.
    input_scope: str

    # The caller sends raw operating/sensor history, not engineered features.
    input_representation: str

    # One prediction is produced for the most recent eligible cycle.
    prediction_scope: str

    # The Phase 1 evaluation contract required a 10-cycle history before a
    # row became prediction-eligible.
    minimum_history_cycles: int

    # The target belongs to evaluation/training, not to inference requests.
    caller_supplies_target: bool

    # Model-specific temporal features remain an internal responsibility.
    caller_supplies_engineered_features: bool

    # The first MVP deliberately accepts one engine per inference request.
    multiple_engines_per_request: bool


PHASE_21_INFERENCE_CONTRACT = InferenceContract(
    input_scope="single_engine_history",
    input_representation="raw_engine_observations",
    prediction_scope="latest_eligible_cycle",
    minimum_history_cycles=EXPANDED_TEMPORAL_WINDOW,
    caller_supplies_target=False,
    caller_supplies_engineered_features=False,
    multiple_engines_per_request=False,
)