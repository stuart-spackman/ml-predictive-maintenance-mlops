# Phase 2.1 — Task Group 2
# Reusable Training-Serving Feature Pipeline
#
# Responsibility:
# Convert validated raw single-engine history into the same causal temporal
# representation used during Phase 1 model development.
#
# Important:
# This module REUSES the Phase 1 temporal-feature implementation.
# It does not independently recreate rolling/lag mathematics.

import numpy as np
import pandas as pd

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
    SIMPLE_TEMPORAL_MODEL_FEATURES,
    EXPANDED_TEMPORAL_SOURCE_FEATURES,
    EXPANDED_TEMPORAL_LAG,
    EXPANDED_TEMPORAL_WINDOW,
    EXPANDED_TEMPORAL_EXTENSION_FEATURES,
)

from predictive_maintenance.features.temporal import (
    add_simple_temporal_features,
    add_expanded_temporal_features,
)

from predictive_maintenance.inference.contract import (
    PHASE_21_INFERENCE_CONTRACT,
)

from predictive_maintenance.inference.validation import (
    validate_engine_history,
)

from predictive_maintenance.inference.errors import (
    InferenceFeatureError,
)


PHASE_21_TEMPORAL_SUPERSET = tuple(
    dict.fromkeys(
        list(
            SIMPLE_TEMPORAL_MODEL_FEATURES
        )
        + list(
            EXPANDED_TEMPORAL_EXTENSION_FEATURES
        )
    )
)


assert len(
    SIMPLE_TEMPORAL_MODEL_FEATURES
) == 36

assert len(
    EXPANDED_TEMPORAL_EXTENSION_FEATURES
) == 24

assert len(
    PHASE_21_TEMPORAL_SUPERSET
) == 60


def build_inference_temporal_table(
    history_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate raw single-engine history and construct the complete causal
    Phase 1.6 temporal representation.

    Parameters
    ----------
    history_df:
        Raw FD001-style history for exactly one engine.

    Returns
    -------
    pd.DataFrame
        Validated chronological engine history with the same temporal feature
        definitions used during Phase 1 development.
    """

    validated_df = (
        validate_engine_history(
            history_df
        )
    )


    # ------------------------------------------------------------
    # Simple Phase 1 temporal representation
    # ------------------------------------------------------------
    #
    # IMPORTANT:
    # We call the same source function used during training rather than
    # reproducing its calculations here.

    simple_temporal_df = (
        add_simple_temporal_features(
            validated_df
        )
    )


    # ------------------------------------------------------------
    # Expanded Phase 1 temporal representation
    # ------------------------------------------------------------

    expanded_temporal_df = (
        add_expanded_temporal_features(
            X=simple_temporal_df,
            groups=simple_temporal_df[
                GROUP_COLUMN
            ],
            sensor_columns=(
                EXPANDED_TEMPORAL_SOURCE_FEATURES
            ),
            lag=(
                EXPANDED_TEMPORAL_LAG
            ),
            window=(
                EXPANDED_TEMPORAL_WINDOW
            ),
        )
    )


    assert len(
        expanded_temporal_df
    ) == len(
        validated_df
    )


    missing_temporal_features = [
        feature
        for feature
        in PHASE_21_TEMPORAL_SUPERSET
        if feature
        not in expanded_temporal_df.columns
    ]


    assert not missing_temporal_features, (
        "Inference temporal construction is missing expected Phase 1 "
        f"features: {missing_temporal_features}"
    )


    return expanded_temporal_df


def build_latest_temporal_row(
    history_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construct the complete Phase 1.6 temporal feature row for the latest
    observed cycle of one valid engine history.
    """

    temporal_df = (
        build_inference_temporal_table(
            history_df
        )
    )


    minimum_cycles = (
        PHASE_21_INFERENCE_CONTRACT
        .minimum_history_cycles
    )


    # TG1 already checks this, but keeping this assertion close to the temporal
    # eligibility logic documents the assumption explicitly.
    assert len(
        temporal_df
    ) >= minimum_cycles


    latest_row = (
        temporal_df
        .iloc[
            [-1]
        ]
        .copy()
    )


    # The latest cycle should now have every Phase 1.6 temporal feature needed
    # by the canonical temporal superset.
    latest_temporal_values = (
        latest_row[
            list(
                PHASE_21_TEMPORAL_SUPERSET
            )
        ]
        .to_numpy(
            dtype=float
        )
    )


    if not np.isfinite(
        latest_temporal_values
    ).all():
        raise InferenceFeatureError(
            "Latest engine cycle does not contain a complete finite "
            "Phase 1.6 temporal representation."
        )


    return latest_row