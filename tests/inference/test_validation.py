# Phase 2.1 — Task Group 6
# Automated tests for raw engine-history validation.

import numpy as np
import pandas as pd
import pytest

from predictive_maintenance.inference.errors import (
    InferenceInputError,
)

from predictive_maintenance.inference.validation import (
    EngineHistoryValidationError,
    validate_engine_history,
)


def test_valid_history_is_accepted(
    valid_20_cycle_history,
):
    validated = (
        validate_engine_history(
            valid_20_cycle_history
        )
    )

    assert len(
        validated
    ) == 20

    assert validated[
        "cycles"
    ].tolist() == list(
        range(
            1,
            21,
        )
    )


def test_unsorted_history_is_normalized(
    valid_20_cycle_history,
):
    shuffled = (
        valid_20_cycle_history
        .sample(
            frac=1,
            random_state=42,
        )
        .reset_index(
            drop=True
        )
    )

    validated = (
        validate_engine_history(
            shuffled
        )
    )

    assert validated[
        "cycles"
    ].tolist() == list(
        range(
            1,
            21,
        )
    )


def test_insufficient_history_is_rejected(
    engine_1_df,
):
    too_short = (
        engine_1_df
        .head(7)
        .copy()
    )

    with pytest.raises(
        EngineHistoryValidationError,
        match="At least 10 cycles",
    ):
        validate_engine_history(
            too_short
        )


def test_missing_cycle_is_rejected(
    engine_1_df,
):
    history = (
        engine_1_df
        .head(12)
        .loc[
            lambda df:
            df["cycles"].ne(6)
        ]
        .copy()
    )

    with pytest.raises(
        EngineHistoryValidationError,
        match="contiguous",
    ):
        validate_engine_history(
            history
        )


def test_duplicate_cycle_is_rejected(
    engine_1_df,
):
    history = pd.concat(
        [
            engine_1_df.head(12),
            engine_1_df.iloc[[5]],
        ],
        ignore_index=True,
    )

    with pytest.raises(
        EngineHistoryValidationError,
        match="Duplicate cycle",
    ):
        validate_engine_history(
            history
        )


def test_missing_required_column_is_rejected(
    valid_20_cycle_history,
):
    history = (
        valid_20_cycle_history
        .drop(
            columns=[
                "sensor_measurement_12"
            ]
        )
    )

    with pytest.raises(
        EngineHistoryValidationError,
        match="Missing required raw columns",
    ):
        validate_engine_history(
            history
        )


def test_nan_is_rejected(
    valid_20_cycle_history,
):
    history = (
        valid_20_cycle_history
        .copy()
    )

    history.loc[
        history.index[0],
        "sensor_measurement_7",
    ] = np.nan

    with pytest.raises(
        EngineHistoryValidationError,
        match="NaN or infinite",
    ):
        validate_engine_history(
            history
        )


def test_multiple_engines_are_rejected(
    development_raw_df,
    engine_1_df,
):
    engine_2_row = (
        development_raw_df
        .loc[
            development_raw_df[
                "unit_no"
            ]
            .eq(2)
        ]
        .head(1)
    )

    history = pd.concat(
        [
            engine_1_df.head(11),
            engine_2_row,
        ],
        ignore_index=True,
    )

    with pytest.raises(
        EngineHistoryValidationError,
        match="exactly one engine",
    ):
        validate_engine_history(
            history
        )


def test_validation_error_is_an_inference_input_error(
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
        validate_engine_history(
            too_short
        )