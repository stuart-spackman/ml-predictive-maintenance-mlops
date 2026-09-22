# Phase 2.1 — Task Group 5
# Exercise known inference failure paths.

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

from predictive_maintenance.inference.errors import (
    InferenceError,
    InferenceInputError,
)

from predictive_maintenance.inference.pipeline import (
    create_default_inference_pipeline,
)


def run_failure_case(
    name: str,
    pipeline,
    history_df: pd.DataFrame,
) -> None:
    """
    Run one deliberately invalid inference request.
    """

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    try:

        pipeline.predict(
            history_df
        )

    except InferenceInputError as error:

        print(
            "EXPECTED INPUT FAILURE"
        )

        print(
            "Exception type:",
            type(
                error
            ).__name__,
        )

        print(
            "Reason:",
            error,
        )

    except InferenceError as error:

        print(
            "KNOWN NON-INPUT INFERENCE FAILURE"
        )

        print(
            "Exception type:",
            type(
                error
            ).__name__,
        )

        print(
            "Reason:",
            error,
        )

    else:

        raise AssertionError(
            "Deliberately invalid history unexpectedly produced "
            "a prediction."
        )


def main() -> None:

    development_raw_df, _, _ = (
        load_cmapss_subset(
            DATASET_NAME
        )
    )


    pipeline = (
        create_default_inference_pipeline()
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
    # Case 1 — Insufficient history
    # --------------------------------------------------------

    too_short = (
        engine_1_df
        .head(7)
        .copy()
    )


    run_failure_case(
        "CASE 1 — Insufficient history",
        pipeline,
        too_short,
    )


    # --------------------------------------------------------
    # Case 2 — Missing cycle
    # --------------------------------------------------------

    missing_cycle = (
        engine_1_df
        .head(12)
        .loc[
            lambda df:
            df["cycles"].ne(6)
        ]
        .copy()
    )


    run_failure_case(
        "CASE 2 — Missing cycle",
        pipeline,
        missing_cycle,
    )


    # --------------------------------------------------------
    # Case 3 — Duplicate cycle
    # --------------------------------------------------------

    duplicate_cycle = pd.concat(
        [
            engine_1_df.head(12),
            engine_1_df.iloc[[5]],
        ],
        ignore_index=True,
    )


    run_failure_case(
        "CASE 3 — Duplicate cycle",
        pipeline,
        duplicate_cycle,
    )


    # --------------------------------------------------------
    # Case 4 — Missing required column
    # --------------------------------------------------------

    missing_sensor = (
        engine_1_df
        .head(12)
        .drop(
            columns=[
                "sensor_measurement_12"
            ]
        )
        .copy()
    )


    run_failure_case(
        "CASE 4 — Missing required sensor column",
        pipeline,
        missing_sensor,
    )


    # --------------------------------------------------------
    # Case 5 — Multiple engines
    # --------------------------------------------------------

    engine_2_row = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(2)
        ]
        .head(1)
    )


    multiple_engines = pd.concat(
        [
            engine_1_df.head(11),
            engine_2_row,
        ],
        ignore_index=True,
    )


    run_failure_case(
        "CASE 5 — Multiple engines",
        pipeline,
        multiple_engines,
    )


    print()
    print("=" * 60)

    print(
        "Known failure-path audit: PASSED"
    )


if __name__ == "__main__":
    main()