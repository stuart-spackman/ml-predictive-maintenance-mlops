# Phase 2.1 — Task Group 1
# Manually exercise the inference validation layer.

import pandas as pd

from predictive_maintenance.config import (
    DATASET_NAME,
)

from predictive_maintenance.data.cmapss import (
    load_cmapss_subset,
)

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)

from predictive_maintenance.inference.validation import (
    EngineHistoryValidationError,
    validate_engine_history,
)


def show_case(
    name,
    history_df,
) -> None:
    """Run one validation example and print the result."""

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    try:
        validated_df = (
            validate_engine_history(
                history_df
            )
        )

        print("VALID")

        print(
            "Engine:",
            validated_df[
                GROUP_COLUMN
            ].iloc[0],
        )

        print(
            "Cycles:",
            len(
                validated_df
            ),
        )

    except EngineHistoryValidationError as error:

        print("INVALID")

        print(
            "Reason:",
            error,
        )


def main() -> None:

    development_raw_df, _, _ = (
        load_cmapss_subset(
            DATASET_NAME
        )
    )


    engine_1_df = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(1)
        ]
        .copy()
    )


    # --------------------------------------------------------
    # Case 1 — Valid 12-cycle history
    # --------------------------------------------------------

    valid_history = (
        engine_1_df
        .head(12)
        .copy()
    )


    show_case(
        "CASE 1 — Valid history",
        valid_history,
    )


    # --------------------------------------------------------
    # Case 2 — Same valid rows, deliberately shuffled
    #
    # This should PASS because cycle order is unambiguous
    # and validation safely sorts it.
    # --------------------------------------------------------

    shuffled_history = (
        valid_history
        .sample(
            frac=1,
            random_state=42,
        )
        .reset_index(
            drop=True
        )
    )


    show_case(
        "CASE 2 — Unsorted but recoverable",
        shuffled_history,
    )


    # --------------------------------------------------------
    # Case 3 — Too little history
    # --------------------------------------------------------

    too_short_history = (
        engine_1_df
        .head(8)
        .copy()
    )


    show_case(
        "CASE 3 — Only 8 cycles",
        too_short_history,
    )


    # --------------------------------------------------------
    # Case 4 — Missing a cycle
    # --------------------------------------------------------

    missing_cycle_history = (
        valid_history
        .loc[
            valid_history[
                "cycles"
            ]
            .ne(6)
        ]
        .copy()
    )


    show_case(
        "CASE 4 — Missing cycle 6",
        missing_cycle_history,
    )


    # --------------------------------------------------------
    # Case 5 — Two engines mixed together
    # --------------------------------------------------------

    second_engine_row = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(2)
        ]
        .head(1)
    )


    mixed_engine_history = (
        valid_history
        .iloc[:-1]
        .copy()
    )


    mixed_engine_history = pd.concat(
    [
        mixed_engine_history,
        second_engine_row,
    ],
    ignore_index=True,
    )


    show_case(
        "CASE 5 — Multiple engines",
        mixed_engine_history,
    )


if __name__ == "__main__":
    main()