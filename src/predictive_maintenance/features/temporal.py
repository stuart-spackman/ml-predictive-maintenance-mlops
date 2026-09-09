"""Causal temporal feature utilities for engine-cycle data."""

import pandas as pd
import numpy as np

GROUP_COLUMN = "unit_no"
TIME_COLUMN = "cycles"


def _sorted_engine_copy(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy ordered by engine and operating cycle."""

    required_columns = {
        GROUP_COLUMN,
        TIME_COLUMN,
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Temporal features require columns: "
            f"{sorted(missing_columns)}"
        )

    return (
        df
        .sort_values(
            [GROUP_COLUMN, TIME_COLUMN]
        )
        .copy()
    )


def add_lag_features(
    df: pd.DataFrame,
    columns,
    lags,
) -> pd.DataFrame:
    """Add causal within-engine lag features."""

    result = _sorted_engine_copy(df)

    for column in columns:
        for lag in lags:
            if lag <= 0:
                raise ValueError(
                    "Lag values must be positive."
                )

            result[
                f"{column}_lag_{lag}"
            ] = (
                result
                .groupby(GROUP_COLUMN)[column]
                .shift(lag)
            )

    return result


def add_difference_features(
    df: pd.DataFrame,
    columns,
    periods=1,
) -> pd.DataFrame:
    """Add causal within-engine difference features."""

    if periods <= 0:
        raise ValueError(
            "Difference periods must be positive."
        )

    result = _sorted_engine_copy(df)

    for column in columns:
        result[
            f"{column}_diff_{periods}"
        ] = (
            result
            .groupby(GROUP_COLUMN)[column]
            .diff(periods)
        )

    return result


def add_rolling_mean_features(
    df: pd.DataFrame,
    columns,
    windows,
) -> pd.DataFrame:
    """Add causal trailing within-engine rolling means."""

    result = _sorted_engine_copy(df)

    for column in columns:
        for window in windows:
            if window <= 0:
                raise ValueError(
                    "Rolling windows must be positive."
                )

            result[
                f"{column}_rolling_mean_{window}"
            ] = (
                result
                .groupby(GROUP_COLUMN)[column]
                .transform(
                    lambda series: (
                        series
                        .rolling(
                            window=window,
                            min_periods=window,
                        )
                        .mean()
                    )
                )
            )

    return result

# --- Compose the simple temporal feature policy from the validated primitives ---
#
# What this does:
# Applies the project's initial lag, difference, and rolling-mean definitions
# through one reusable function.
#
# Why this matters:
# The same transformation must later be applied independently to training,
# validation, and test engine histories.
#
# Concept to focus on:
# The individual primitives establish HOW features are calculated.
# This wrapper establishes WHICH temporal features belong to this particular
# experiment.

from predictive_maintenance.features.feature_sets import (
    SIMPLE_TEMPORAL_LAGS,
    SIMPLE_TEMPORAL_WINDOWS,
    TEMPORAL_SOURCE_FEATURES,
)


def add_simple_temporal_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Add the initial causal temporal feature set."""

    result = add_lag_features(
        df,
        columns=TEMPORAL_SOURCE_FEATURES,
        lags=SIMPLE_TEMPORAL_LAGS,
    )

    result = add_difference_features(
        result,
        columns=TEMPORAL_SOURCE_FEATURES,
        periods=1,
    )

    result = add_rolling_mean_features(
        result,
        columns=TEMPORAL_SOURCE_FEATURES,
        windows=SIMPLE_TEMPORAL_WINDOWS,
    )

    return result

# 4D — Implement causal, engine-bounded expanded temporal features
#
# What this does:
# Adds longer-horizon lag, rolling-level, rolling-instability, and rolling-trend
# features to an existing aligned modeling matrix.
#
# Why this matters:
# Temporal features are valid only if they use information available at or
# before the prediction cycle and never cross engine boundaries.
#
# Concept to focus on:
# SORT by cycle + GROUP by engine + look backward only.

def _rolling_linear_slope(
    values: np.ndarray,
) -> float:
    """Return the least-squares slope across an equally spaced window."""

    x = np.arange(
        len(values),
        dtype=float,
    )

    x_centered = (
        x - x.mean()
    )

    y_centered = (
        values - values.mean()
    )

    denominator = np.sum(
        x_centered ** 2
    )

    if denominator == 0:
        return 0.0

    return float(
        np.sum(
            x_centered * y_centered
        )
        / denominator
    )


def add_expanded_temporal_features(
    X: pd.DataFrame,
    groups: pd.Series,
    sensor_columns: list[str],
    lag: int = 5,
    window: int = 10,
) -> pd.DataFrame:
    """Add causal temporal extensions while preserving original row indices."""

    if not X.index.equals(
        groups.index
    ):
        raise ValueError(
            "X and groups must have identical indices."
        )

    if "cycles" not in X.columns:
        raise ValueError(
            "X must contain the cycles column."
        )

    result = X.copy()

    helper_group_column = (
        "__engine_group__"
    )

    result[
        helper_group_column
    ] = groups

    original_index = (
        result.index.copy()
    )

    result = (
        result
        .sort_values(
            [
                helper_group_column,
                "cycles",
            ]
        )
    )

    for sensor in sensor_columns:
        grouped_sensor = (
            result
            .groupby(
                helper_group_column,
                sort=False,
            )[sensor]
        )

        result[
            f"{sensor}_lag_{lag}"
        ] = (
            grouped_sensor.shift(lag)
        )

        result[
            f"{sensor}_rolling_mean_{window}"
        ] = (
            grouped_sensor.transform(
                lambda values:
                values
                .rolling(
                    window=window,
                    min_periods=window,
                )
                .mean()
            )
        )

        result[
            f"{sensor}_rolling_std_{window}"
        ] = (
            grouped_sensor.transform(
                lambda values:
                values
                .rolling(
                    window=window,
                    min_periods=window,
                )
                .std(ddof=0)
            )
        )

        result[
            f"{sensor}_rolling_slope_{window}"
        ] = (
            grouped_sensor.transform(
                lambda values:
                values
                .rolling(
                    window=window,
                    min_periods=window,
                )
                .apply(
                    _rolling_linear_slope,
                    raw=True,
                )
            )
        )

    result = (
        result
        .drop(
            columns=[
                helper_group_column
            ]
        )
        .reindex(
            original_index
        )
    )

    return result