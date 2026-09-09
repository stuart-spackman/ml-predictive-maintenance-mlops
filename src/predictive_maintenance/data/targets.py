"""Target construction utilities for C-MAPSS training data."""

import pandas as pd


def add_training_rul(df: pd.DataFrame) -> pd.DataFrame:
    """Add final-cycle and RUL columns to run-to-failure training data."""

    required_columns = {"unit_no", "cycles"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    labeled_df = df.copy()

    labeled_df["final_cycle"] = (
        labeled_df.groupby("unit_no")["cycles"]
        .transform("max")
    )

    labeled_df["rul"] = (
        labeled_df["final_cycle"]
        - labeled_df["cycles"]
    )

    return labeled_df

def cap_rul_target(
    y: pd.Series,
    cap: float,
) -> pd.Series:
    """Cap RUL values at a specified upper bound."""

    if cap <= 0:
        raise ValueError(
            "RUL cap must be greater than zero."
        )

    return (
        y
        .clip(upper=cap)
        .copy()
    )