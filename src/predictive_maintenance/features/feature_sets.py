"""Feature-set definitions for the FD001 predictive-maintenance pipeline."""

from predictive_maintenance.data.cmapss import (
    OPERATING_SETTING_COLUMNS,
    SENSOR_COLUMNS,
)


# Exactly constant measurement features identified during FD001 EDA.
#
# These features contain no training variation, so they cannot distinguish
# one training observation from another.
CONSTANT_MEASUREMENT_FEATURES = [
    "op_setting_3",
    "sensor_measurement_1",
    "sensor_measurement_5",
    "sensor_measurement_10",
    "sensor_measurement_16",
    "sensor_measurement_18",
    "sensor_measurement_19",
]


# All measurement columns that remain after removing exact constants.
#
# This includes:
# - Operating Settings 1 and 2
# - 15 nonconstant sensor measurements
MEASUREMENT_COLUMNS = (
    OPERATING_SETTING_COLUMNS
    + SENSOR_COLUMNS
)

BASELINE_MEASUREMENT_FEATURES = [
    column
    for column in MEASUREMENT_COLUMNS
    if column not in CONSTANT_MEASUREMENT_FEATURES
]


# Raw features available to the first baseline model.
#
# `cycles` is included because current engine age is observable at inference
# time. No temporal history has been engineered yet.
BASELINE_RAW_FEATURES = [
    "cycles",
    *BASELINE_MEASUREMENT_FEATURES,
]


# Column roles that must remain separate from predictive inputs.
GROUP_COLUMN = "unit_no"
TARGET_COLUMN = "rul"

FUTURE_INFORMATION_COLUMNS = [
    "final_cycle",
]

EDA_ONLY_COLUMNS = [
    "lifecycle_fraction",
    "lifecycle_stage",
    "rul_band",
]

NON_PREDICTIVE_COLUMNS = [
    GROUP_COLUMN,
    TARGET_COLUMN,
    *FUTURE_INFORMATION_COLUMNS,
    *EDA_ONLY_COLUMNS,
]

# Sensors prioritized for the first temporal-feature experiment.
#
# These were selected from EDA because they showed comparatively strong
# within-engine lifecycle-associated behavior.
#
# Important:
# This is an EDA-motivated candidate set, NOT a claim that these are the
# optimal predictive sensors.
TEMPORAL_SOURCE_FEATURES = [
    "sensor_measurement_4",
    "sensor_measurement_7",
    "sensor_measurement_9",
    "sensor_measurement_11",
    "sensor_measurement_12",
    "sensor_measurement_14",
]


# Deliberately simple temporal settings for the first temporal representation.
#
# We are not optimizing lag lengths or rolling-window sizes yet.
SIMPLE_TEMPORAL_LAGS = [
    1,
]

SIMPLE_TEMPORAL_WINDOWS = [
    5,
]


# Names of the engineered features created by the simple temporal policy.
SIMPLE_TEMPORAL_FEATURES = (
    [
        f"{column}_lag_1"
        for column in TEMPORAL_SOURCE_FEATURES
    ]
    + [
        f"{column}_diff_1"
        for column in TEMPORAL_SOURCE_FEATURES
    ]
    + [
        f"{column}_rolling_mean_5"
        for column in TEMPORAL_SOURCE_FEATURES
    ]
)


# Complete feature set for the first temporal modeling experiment.
#
# 18 raw predictors
# +
# 18 engineered temporal predictors
# =
# 36 total predictors
SIMPLE_TEMPORAL_MODEL_FEATURES = (
    BASELINE_RAW_FEATURES
    + SIMPLE_TEMPORAL_FEATURES
)

# Simplest benchmark representation.
#
# This asks how much RUL can be predicted from current engine cycle alone.
# More complex feature sets should demonstrate improvement beyond this
# extremely simple age-based reference.
CYCLE_ONLY_FEATURES = [
    "cycles",
]

SENSOR_6_FEATURE = "sensor_measurement_6"

SENSOR_6_ABLATION_FEATURES = [
    feature
    for feature in SIMPLE_TEMPORAL_MODEL_FEATURES
    if feature != SENSOR_6_FEATURE
]

# 4C — Define the Phase 1.5 expanded temporal feature configuration
#
# What this does:
# Predeclares the sensors, lag horizon, rolling horizon, and feature names used
# by the controlled temporal-expansion experiments.
#
# Why this matters:
# The feature search space should be explicit before validation results are
# observed rather than being adjusted repeatedly to fit one validation split.

EXPANDED_TEMPORAL_SOURCE_FEATURES = [
    "sensor_measurement_4",
    "sensor_measurement_7",
    "sensor_measurement_9",
    "sensor_measurement_11",
    "sensor_measurement_12",
    "sensor_measurement_14",
]

EXPANDED_TEMPORAL_LAG = 5
EXPANDED_TEMPORAL_WINDOW = 10

EXPANDED_LAG_5_FEATURES = [
    f"{feature}_lag_5"
    for feature in EXPANDED_TEMPORAL_SOURCE_FEATURES
]

EXPANDED_ROLLING_MEAN_10_FEATURES = [
    f"{feature}_rolling_mean_10"
    for feature in EXPANDED_TEMPORAL_SOURCE_FEATURES
]

EXPANDED_ROLLING_STD_10_FEATURES = [
    f"{feature}_rolling_std_10"
    for feature in EXPANDED_TEMPORAL_SOURCE_FEATURES
]

EXPANDED_ROLLING_SLOPE_10_FEATURES = [
    f"{feature}_rolling_slope_10"
    for feature in EXPANDED_TEMPORAL_SOURCE_FEATURES
]

EXPANDED_TEMPORAL_EXTENSION_FEATURES = (
    EXPANDED_LAG_5_FEATURES
    + EXPANDED_ROLLING_MEAN_10_FEATURES
    + EXPANDED_ROLLING_STD_10_FEATURES
    + EXPANDED_ROLLING_SLOPE_10_FEATURES
)