# Phase 2.1 — Task Group 2
# Inspect inference-time temporal feature construction.

import numpy as np

from predictive_maintenance.config import (
    DATASET_NAME,
)

from predictive_maintenance.data.cmapss import (
    load_cmapss_subset,
)

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)

from predictive_maintenance.inference.features import (
    PHASE_21_TEMPORAL_SUPERSET,
    build_inference_temporal_table,
    build_latest_temporal_row,
)


def main() -> None:

    development_raw_df, _, _ = (
        load_cmapss_subset(
            DATASET_NAME
        )
    )


    engine_id = 1

    engine_history = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(
                engine_id
            )
        ]
        .head(20)
        .copy()
    )


    temporal_df = (
        build_inference_temporal_table(
            engine_history
        )
    )


    latest_row = (
        build_latest_temporal_row(
            engine_history
        )
    )


    print(
        "INFERENCE TEMPORAL FEATURE AUDIT"
    )

    print(
        "=" * 50
    )

    print(
        "Engine:",
        engine_id,
    )

    print(
        "Raw history rows:",
        len(
            engine_history
        ),
    )

    print(
        "Temporal table rows:",
        len(
            temporal_df
        ),
    )

    print(
        "Temporal feature count:",
        len(
            PHASE_21_TEMPORAL_SUPERSET
        ),
    )

    print(
        "Latest cycle:",
        int(
            latest_row[
                "cycles"
            ].iloc[0]
        ),
    )


    assert (
        len(
            temporal_df
        )
        == len(
            engine_history
        )
    )


    assert (
        len(
            PHASE_21_TEMPORAL_SUPERSET
        )
        == 60
    )


    latest_values = (
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
        latest_values
    ).all()


    print()

    print(
        "Latest temporal row complete: YES"
    )

    print(
        "Training-serving feature construction audit: PASSED"
    )

    # Build the same inference representation twice.
    temporal_df_again = (
        build_inference_temporal_table(
            engine_history
        )
    )


    first_values = (
        temporal_df[
            list(
                PHASE_21_TEMPORAL_SUPERSET
            )
        ]
        .to_numpy(
            dtype=float
        )
    )


    second_values = (
        temporal_df_again[
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


    print(
        "Deterministic feature reconstruction: PASSED"
    )

    # ------------------------------------------------------------
    # Prefix-invariance causality check
    # ------------------------------------------------------------

    engine_full_history = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(
                engine_id
            )
        ]
        .copy()
    )


    cutoff_cycle = 20


    prefix_history = (
        engine_full_history
        .loc[
            engine_full_history[
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
            engine_full_history
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


    print(
        "Prefix-invariance causality audit: PASSED"
    )


if __name__ == "__main__":
    main()