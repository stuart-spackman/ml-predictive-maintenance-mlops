# Phase 2.1 — Task Group 6
# Shared pytest fixtures for inference tests.

import pytest

from predictive_maintenance.config import (
    DATASET_NAME,
)

from predictive_maintenance.data.cmapss import (
    load_cmapss_subset,
)

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)

from predictive_maintenance.inference.artifacts import (
    load_locked_model_artifacts,
)

from predictive_maintenance.inference.pipeline import (
    RULInferencePipeline,
)


@pytest.fixture(
    scope="session"
)
def development_raw_df():
    """
    Load the FD001 development dataframe once for the test session.
    """

    development_df, _, _ = (
        load_cmapss_subset(
            DATASET_NAME
        )
    )

    return development_df


@pytest.fixture
def engine_1_df(
    development_raw_df,
):
    """
    Return a fresh copy of Engine 1's complete raw history.
    """

    return (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(1)
        ]
        .copy()
    )


@pytest.fixture
def valid_20_cycle_history(
    engine_1_df,
):
    """
    Standard valid inference request used by multiple tests.
    """

    return (
        engine_1_df
        .head(20)
        .copy()
    )


@pytest.fixture(
    scope="session"
)
def verified_artifacts():
    """
    Load and verify the real frozen Phase 1 artifacts once.
    """

    return (
        load_locked_model_artifacts()
    )


@pytest.fixture(
    scope="session"
)
def inference_pipeline(
    verified_artifacts,
):
    """
    Create one persistent verified inference pipeline for the test session.
    """

    return RULInferencePipeline(
        artifacts=verified_artifacts
    )