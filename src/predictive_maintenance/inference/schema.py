# Phase 2.1 — Task Group 1
# Raw Engine-History Schema
#
# This module defines the raw FD001-style columns accepted by the
# production-style inference pipeline.
#
# The caller supplies RAW observations.
# Engineered temporal features remain internal implementation details.

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)


CYCLE_COLUMN = "cycles"


OPERATING_SETTING_COLUMNS = (
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
)


SENSOR_COLUMNS = tuple(
    f"sensor_measurement_{sensor_number}"
    for sensor_number in range(1, 22)
)


REQUIRED_RAW_HISTORY_COLUMNS = (
    GROUP_COLUMN,
    CYCLE_COLUMN,
    *OPERATING_SETTING_COLUMNS,
    *SENSOR_COLUMNS,
)


RAW_NUMERIC_COLUMNS = (
    GROUP_COLUMN,
    CYCLE_COLUMN,
    *OPERATING_SETTING_COLUMNS,
    *SENSOR_COLUMNS,
)


assert len(
    REQUIRED_RAW_HISTORY_COLUMNS
) == 26