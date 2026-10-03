# Phase 2.1 — Task Group 6
# Automated tests for inference-time temporal feature construction.

import numpy as np

from predictive_maintenance.inference.features import (
    PHASE_21_TEMPORAL_SUPERSET,
    build_inference_temporal_table,
    build_latest_temporal_row,
)


def test_temporal_superset_contains_60_features():
    assert len(
        PHASE_21_TEMPORAL_SUPERSET
    ) == 60


def test_latest_temporal_row_is_complete(
    valid_20_cycle_history,
):
    latest_row = (
        build_latest_temporal_row(
            valid_20_cycle_history
        )
    )

    assert latest_row.shape[0] == 1

    assert int(
        latest_row[
            "cycles"
        ].iloc[0]
    ) == 20

    values = (
        latest_row[
            list(
                PHASE_21_TEMPORAL_SUPERSET
            )
        ]
        .to_numpy(
            dtype=float
        )
    )

    assert np.isfinite(
        values
    ).all()


def test_temporal_feature_construction_is_deterministic(
    valid_20_cycle_history,
):
    first = (
        build_inference_temporal_table(
            valid_20_cycle_history
        )
    )

    second = (
        build_inference_temporal_table(
            valid_20_cycle_history
        )
    )

    first_values = (
        first[
            list(
                PHASE_21_TEMPORAL_SUPERSET
            )
        ]
        .to_numpy(
            dtype=float
        )
    )

    second_values = (
        second[
            list(
                PHASE_21_TEMPORAL_SUPERSET
            )
        ]
        .to_numpy(
            dtype=float
        )
    )

    assert np.allclose(
        first_values,
        second_values,
        equal_nan=True,
    )


def test_temporal_features_are_prefix_invariant(
    engine_1_df,
):
    cutoff_cycle = 20

    prefix_history = (
        engine_1_df
        .loc[
            engine_1_df[
                "cycles"
            ]
            .le(
                cutoff_cycle
            )
        ]
        .copy()
    )

    full_temporal = (
        build_inference_temporal_table(
            engine_1_df
        )
    )

    prefix_temporal = (
        build_inference_temporal_table(
            prefix_history
        )
    )

    full_cycle_values = (
        full_temporal
        .loc[
            full_temporal[
                "cycles"
            ]
            .eq(
                cutoff_cycle
            ),
            list(
                PHASE_21_TEMPORAL_SUPERSET
            ),
        ]
        .to_numpy(
            dtype=float
        )
    )

    prefix_cycle_values = (
        prefix_temporal
        .loc[
            prefix_temporal[
                "cycles"
            ]
            .eq(
                cutoff_cycle
            ),
            list(
                PHASE_21_TEMPORAL_SUPERSET
            ),
        ]
        .to_numpy(
            dtype=float
        )
    )

    assert np.allclose(
        full_cycle_values,
        prefix_cycle_values,
        equal_nan=True,
    )