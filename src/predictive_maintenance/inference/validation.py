# Phase 2.1 — Task Group 1
# Raw Engine-History Validation
#
# Responsibility:
# Turn arbitrary dataframe input into a validated, normalized raw
# single-engine history.
#
# This module does NOT:
# - construct temporal features,
# - load the fitted model,
# - generate predictions,
# - or know anything about HTTP.

import numpy as np
import pandas as pd

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)

from predictive_maintenance.inference.contract import (
    PHASE_21_INFERENCE_CONTRACT,
)

from predictive_maintenance.inference.schema import (
    CYCLE_COLUMN,
    RAW_NUMERIC_COLUMNS,
    REQUIRED_RAW_HISTORY_COLUMNS,
)

from predictive_maintenance.inference.errors import (
    InferenceInputError,
)

class EngineHistoryValidationError(
    InferenceInputError
):
    """
    Raised when raw engine history violates the Phase 2.1
    inference contract.
    """

def validate_engine_history(
    history_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate and normalize one raw engine history.

    Returns
    -------
    pd.DataFrame
        A validated copy that is:

        - restricted to the canonical raw schema,
        - arranged in canonical column order,
        - sorted chronologically by cycle,
        - reset to a clean row index.

    Raises
    ------
    EngineHistoryValidationError
        If the input violates the Phase 2.1 inference contract.
    """

    # ------------------------------------------------------------
    # 1. Input object
    # ------------------------------------------------------------

    if not isinstance(
        history_df,
        pd.DataFrame,
    ):
        raise EngineHistoryValidationError(
            "Engine history must be provided as a pandas DataFrame."
        )


    if history_df.empty:
        raise EngineHistoryValidationError(
            "Engine history cannot be empty."
        )


    # ------------------------------------------------------------
    # 2. Column schema
    # ------------------------------------------------------------

    expected_columns = set(
        REQUIRED_RAW_HISTORY_COLUMNS
    )

    actual_columns = set(
        history_df.columns
    )


    missing_columns = sorted(
        expected_columns
        - actual_columns
    )

    unexpected_columns = sorted(
        actual_columns
        - expected_columns
    )


    if missing_columns:
        raise EngineHistoryValidationError(
            "Missing required raw columns: "
            f"{missing_columns}"
        )


    if unexpected_columns:
        raise EngineHistoryValidationError(
            "Unexpected columns are not allowed in raw engine history: "
            f"{unexpected_columns}"
        )


    # Create a copy so caller-owned data is never modified in place.
    normalized_df = (
    history_df
    .loc[
        :,
        list(
            REQUIRED_RAW_HISTORY_COLUMNS
        ),
    ]
    .copy()
    )


    # ------------------------------------------------------------
    # 3. Numeric schema
    # ------------------------------------------------------------

    non_numeric_columns = [
        column
        for column in RAW_NUMERIC_COLUMNS
        if not pd.api.types.is_numeric_dtype(
            normalized_df[column]
        )
    ]


    if non_numeric_columns:
        raise EngineHistoryValidationError(
            "The following raw columns must be numeric: "
            f"{non_numeric_columns}"
        )


    # Reject NaN, +inf, and -inf.
    numeric_values = (
    normalized_df[
        list(
            RAW_NUMERIC_COLUMNS
        )
    ]
    .to_numpy(
        dtype=float
    )
    )


    if not np.isfinite(
        numeric_values
    ).all():
        raise EngineHistoryValidationError(
            "Raw engine history contains NaN or infinite numeric values."
        )


    # ------------------------------------------------------------
    # 4. Integer-valued engine IDs and cycles
    # ------------------------------------------------------------

    engine_values = (
        normalized_df[
            GROUP_COLUMN
        ]
        .to_numpy(
            dtype=float
        )
    )

    cycle_values = (
        normalized_df[
            CYCLE_COLUMN
        ]
        .to_numpy(
            dtype=float
        )
    )


    if not np.equal(
        engine_values,
        np.floor(
            engine_values
        ),
    ).all():
        raise EngineHistoryValidationError(
            "Engine identifiers must be integer-valued."
        )


    if not np.equal(
        cycle_values,
        np.floor(
            cycle_values
        ),
    ).all():
        raise EngineHistoryValidationError(
            "Cycle numbers must be integer-valued."
        )


    normalized_df[
        GROUP_COLUMN
    ] = normalized_df[
        GROUP_COLUMN
    ].astype(int)


    normalized_df[
        CYCLE_COLUMN
    ] = normalized_df[
        CYCLE_COLUMN
    ].astype(int)


    # ------------------------------------------------------------
    # 5. Exactly one engine
    # ------------------------------------------------------------

    unique_engine_ids = (
        normalized_df[
            GROUP_COLUMN
        ]
        .unique()
    )


    if len(
        unique_engine_ids
    ) != 1:
        raise EngineHistoryValidationError(
            "Phase 2.1 accepts exactly one engine per inference request. "
            f"Received {len(unique_engine_ids)} engines."
        )


    engine_id = int(
        unique_engine_ids[0]
    )


    if engine_id <= 0:
        raise EngineHistoryValidationError(
            "Engine identifier must be a positive integer."
        )


    # ------------------------------------------------------------
    # 6. Normalize chronological order
    # ------------------------------------------------------------

    normalized_df = (
        normalized_df
        .sort_values(
            CYCLE_COLUMN
        )
        .reset_index(
            drop=True
        )
    )


    # ------------------------------------------------------------
    # 7. Duplicate cycles
    # ------------------------------------------------------------

    duplicate_cycle_mask = (
        normalized_df[
            CYCLE_COLUMN
        ]
        .duplicated()
    )


    if duplicate_cycle_mask.any():

        duplicate_cycles = (
            normalized_df
            .loc[
                duplicate_cycle_mask,
                CYCLE_COLUMN,
            ]
            .tolist()
        )

        raise EngineHistoryValidationError(
            "Duplicate cycle numbers are not allowed. "
            f"Duplicates: {duplicate_cycles}"
        )


    # ------------------------------------------------------------
    # 8. Complete lifecycle history
    # ------------------------------------------------------------
    #
    # For the initial MVP contract, the caller provides complete history
    # beginning at cycle 1.
    #
    # Example valid:
    # 1, 2, 3, ..., 57
    #
    # Example invalid:
    # 1, 2, 3, 5, 6
    #
    # We do not invent missing sensor observations.

    actual_cycles = (
        normalized_df[
            CYCLE_COLUMN
        ]
        .to_numpy()
    )


    expected_cycles = np.arange(
        1,
        len(
            normalized_df
        ) + 1,
    )


    if not np.array_equal(
        actual_cycles,
        expected_cycles,
    ):
        raise EngineHistoryValidationError(
            "Engine history must contain one contiguous observation "
            "for every cycle starting at cycle 1."
        )


    # ------------------------------------------------------------
    # 9. Minimum temporal history
    # ------------------------------------------------------------

    minimum_cycles = (
        PHASE_21_INFERENCE_CONTRACT
        .minimum_history_cycles
    )


    if len(
        normalized_df
    ) < minimum_cycles:
        raise EngineHistoryValidationError(
            "Insufficient engine history. "
            f"At least {minimum_cycles} cycles are required, "
            f"but only {len(normalized_df)} were provided."
        )


    return normalized_df