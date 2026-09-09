"""Training sample-weight utilities."""

import pandas as pd


def make_equal_engine_sample_weights(
    groups: pd.Series,
) -> pd.Series:
    """Give each engine equal total sample-weight mass."""

    if groups.empty:
        raise ValueError(
            "groups must contain at least one observation."
        )

    if groups.isna().any():
        raise ValueError(
            "groups must not contain missing engine identifiers."
        )

    engine_row_counts = (
        groups
        .groupby(groups)
        .transform("size")
    )

    sample_weights = (
        1.0
        / engine_row_counts.astype(float)
    )

    sample_weights.name = "sample_weight"

    return sample_weights