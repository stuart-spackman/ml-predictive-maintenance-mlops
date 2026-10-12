# Phase 2.1 — Task Group 6
# Automated tests for the end-to-end inference pipeline.

import numpy as np
import pytest

from predictive_maintenance.inference.artifacts import (
    LoadedModelArtifacts,
)

from predictive_maintenance.inference.errors import (
    InferenceInputError,
    InferenceModelContractError,
)

from predictive_maintenance.inference.pipeline import (
    RULInferencePipeline,
)

import math

from predictive_maintenance.inference.contract import (
    PHASE_21_INFERENCE_CONTRACT,
)

def test_model_input_matches_locked_feature_schema(
    inference_pipeline,
    verified_artifacts,
    valid_20_cycle_history,
):
    X = (
        inference_pipeline
        .build_model_input(
            valid_20_cycle_history
        )
    )

    expected_features = tuple(
        verified_artifacts
        .locked_spec[
            "feature_names"
        ]
    )

    assert X.shape == (
        1,
        len(
            expected_features
        ),
    )

    assert tuple(
        X.columns
    ) == expected_features


def test_valid_history_produces_finite_prediction(
    inference_pipeline,
    valid_20_cycle_history,
):
    result = (
        inference_pipeline
        .predict(
            valid_20_cycle_history
        )
    )

    assert result.engine_id == 1

    assert result.current_cycle == 20

    assert np.isfinite(
        result.predicted_rul
    )


def test_repeated_inference_is_deterministic(
    inference_pipeline,
    valid_20_cycle_history,
):
    first = (
        inference_pipeline
        .predict(
            valid_20_cycle_history
        )
    )

    second = (
        inference_pipeline
        .predict(
            valid_20_cycle_history
        )
    )

    assert np.isclose(
        first.predicted_rul,
        second.predicted_rul,
    )


def test_pipeline_rejects_invalid_history_as_input_error(
    inference_pipeline,
    engine_1_df,
):
    too_short = (
        engine_1_df
        .head(7)
        .copy()
    )

    with pytest.raises(
        InferenceInputError
    ):
        inference_pipeline.predict(
            too_short
        )

class MismatchedFeatureCountModel:
    """
    Minimal fake estimator whose feature expectation intentionally
    conflicts with the locked specification.
    """

    n_features_in_ = 2

    def predict(
        self,
        X,
    ):
        return np.array(
            [1.0]
        )


def test_pipeline_rejects_model_feature_count_mismatch():

    fake_artifacts = (
        LoadedModelArtifacts(
            locked_spec={
                "feature_names": [
                    "only_one_feature"
                ],
                "n_features": 1,
            },
            final_fit_record={},
            model=(
                MismatchedFeatureCountModel()
            ),
            locked_spec_sha256="fake",
            model_sha256="fake",
        )
    )


    with pytest.raises(
        InferenceModelContractError,
        match="feature count",
    ):
        RULInferencePipeline(
            artifacts=fake_artifacts
        )

def test_minimum_history_boundary(
    inference_pipeline,
    valid_20_cycle_history,
):
    minimum_cycles = (
        PHASE_21_INFERENCE_CONTRACT
        .minimum_history_cycles
    )


    too_short_history = (
        valid_20_cycle_history
        .head(
            minimum_cycles - 1
        )
        .copy()
    )


    with pytest.raises(
        InferenceInputError
    ):
        inference_pipeline.predict(
            too_short_history
        )


    minimum_valid_history = (
        valid_20_cycle_history
        .head(
            minimum_cycles
        )
        .copy()
    )


    result = (
        inference_pipeline.predict(
            minimum_valid_history
        )
    )


    assert (
        result.current_cycle
        ==
        minimum_cycles
    )

    assert math.isfinite(
        result.predicted_rul
    )