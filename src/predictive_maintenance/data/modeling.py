"""Construction of reproducible modeling datasets for FD001."""

from dataclasses import dataclass

import pandas as pd

from predictive_maintenance.config import (
    DATASET_NAME,
    RANDOM_STATE,
)
from predictive_maintenance.data.cmapss import (
    load_cmapss_subset,
)
from predictive_maintenance.data.splitting import (
    grouped_train_validation_indices,
)
from predictive_maintenance.data.targets import (
    add_training_rul,
)
from predictive_maintenance.features.feature_sets import (
    BASELINE_RAW_FEATURES,
    CYCLE_ONLY_FEATURES,
    GROUP_COLUMN,
    SIMPLE_TEMPORAL_FEATURES,
    SIMPLE_TEMPORAL_MODEL_FEATURES,
    TARGET_COLUMN,
)
from predictive_maintenance.features.temporal import (
    add_simple_temporal_features,
)


@dataclass
class ModelingData:
    # Existing Phase 1.4 objects
    X_train_cycle: pd.DataFrame
    X_validation_cycle: pd.DataFrame

    X_train_raw: pd.DataFrame
    X_validation_raw: pd.DataFrame

    X_train_temporal: pd.DataFrame
    X_validation_temporal: pd.DataFrame

    y_train: pd.Series
    y_validation: pd.Series

    groups_train: pd.Series
    groups_validation: pd.Series

    X_test_endpoint_raw: pd.DataFrame
    X_test_endpoint_temporal: pd.DataFrame
    test_endpoint_groups: pd.Series

    # Full-history development objects for richer temporal engineering
    X_train_full_raw: pd.DataFrame
    X_validation_full_raw: pd.DataFrame

    y_train_full: pd.Series
    y_validation_full: pd.Series

    groups_train_full: pd.Series
    groups_validation_full: pd.Series

def build_fd001_modeling_data(
    dataset_name: str = DATASET_NAME,
    validation_size: float = 0.20,
    random_state: int = RANDOM_STATE,
) -> ModelingData:
    """Build the Phase 1.4 modeling datasets from raw FD001 data."""

    # Load the canonical raw data.
    #
    # The official test RUL labels are deliberately discarded here because
    # Phase 1.4 development must not use them.
    train_df, test_df, _ = load_cmapss_subset(
        dataset_name
    )

    # Construct retrospective row-level RUL labels for the complete
    # run-to-failure training trajectories.
    train_labeled_df = add_training_rul(
        train_df
    )

    # Build the objects needed to reproduce the engine-grouped split.
    X_all = train_labeled_df[
        BASELINE_RAW_FEATURES
    ].copy()

    y_all = train_labeled_df[
        TARGET_COLUMN
    ].copy()

    groups_all = train_labeled_df[
        GROUP_COLUMN
    ].copy()

    # Reproduce the Phase 1.3 train/validation engine assignment.
    train_indices, validation_indices = (
        grouped_train_validation_indices(
            X=X_all,
            y=y_all,
            groups=groups_all,
            validation_size=validation_size,
            random_state=random_state,
        )
    )

    # Retain full dataframe information while temporal features are built.
    train_partition_df = (
        train_labeled_df
        .iloc[train_indices]
        .copy()
    )

    validation_partition_df = (
        train_labeled_df
        .iloc[validation_indices]
        .copy()
    )

    # Retain full-history raw development objects before temporal filtering.
    #
    # These objects preserve cycles that may not be eligible as final modeling
    # rows but are still legal historical inputs for richer temporal features.

    X_train_full_raw = (
        train_partition_df[
            BASELINE_RAW_FEATURES
        ]
        .copy()
    )

    X_validation_full_raw = (
        validation_partition_df[
            BASELINE_RAW_FEATURES
        ]
        .copy()
    )

    y_train_full = (
        train_partition_df[
            TARGET_COLUMN
        ]
        .copy()
    )

    y_validation_full = (
        validation_partition_df[
            TARGET_COLUMN
        ]
        .copy()
    )

    groups_train_full = (
        train_partition_df[
            GROUP_COLUMN
        ]
        .copy()
    )

    groups_validation_full = (
        validation_partition_df[
            GROUP_COLUMN
        ]
        .copy()
    )
    
    # Construct identical causal temporal representations independently
    # within training, validation, and official test engine populations.
    train_temporal_df = add_simple_temporal_features(
        train_partition_df
    )

    validation_temporal_df = add_simple_temporal_features(
        validation_partition_df
    )

    test_temporal_df = add_simple_temporal_features(
        test_df
    )

    # Require complete temporal history for the controlled comparison.
    train_complete_mask = (
        train_temporal_df[
            SIMPLE_TEMPORAL_FEATURES
        ]
        .notna()
        .all(axis=1)
    )

    validation_complete_mask = (
        validation_temporal_df[
            SIMPLE_TEMPORAL_FEATURES
        ]
        .notna()
        .all(axis=1)
    )

    # Create matched cycle-only, raw, and temporal representations.
    X_train_cycle = train_temporal_df.loc[
        train_complete_mask,
        CYCLE_ONLY_FEATURES,
    ].copy()

    X_validation_cycle = validation_temporal_df.loc[
        validation_complete_mask,
        CYCLE_ONLY_FEATURES,
    ].copy()

    X_train_raw = train_temporal_df.loc[
        train_complete_mask,
        BASELINE_RAW_FEATURES,
    ].copy()

    X_validation_raw = validation_temporal_df.loc[
        validation_complete_mask,
        BASELINE_RAW_FEATURES,
    ].copy()

    X_train_temporal = train_temporal_df.loc[
        train_complete_mask,
        SIMPLE_TEMPORAL_MODEL_FEATURES,
    ].copy()

    X_validation_temporal = validation_temporal_df.loc[
        validation_complete_mask,
        SIMPLE_TEMPORAL_MODEL_FEATURES,
    ].copy()

    # Extract targets and engine-group metadata from the SAME sorted and
    # filtered dataframes so row alignment is preserved.
    y_train = train_temporal_df.loc[
        train_complete_mask,
        TARGET_COLUMN,
    ].copy()

    y_validation = validation_temporal_df.loc[
        validation_complete_mask,
        TARGET_COLUMN,
    ].copy()

    groups_train = train_temporal_df.loc[
        train_complete_mask,
        GROUP_COLUMN,
    ].copy()

    groups_validation = validation_temporal_df.loc[
        validation_complete_mask,
        GROUP_COLUMN,
    ].copy()

    # Identify the final observed cycle of every official test engine.
    test_endpoint_indices = (
        test_temporal_df
        .groupby(
            GROUP_COLUMN,
            sort=True,
        )["cycles"]
        .idxmax()
    )

    X_test_endpoint_raw = test_temporal_df.loc[
        test_endpoint_indices,
        BASELINE_RAW_FEATURES,
    ].copy()

    X_test_endpoint_temporal = test_temporal_df.loc[
        test_endpoint_indices,
        SIMPLE_TEMPORAL_MODEL_FEATURES,
    ].copy()

    test_endpoint_groups = test_temporal_df.loc[
        test_endpoint_indices,
        GROUP_COLUMN,
    ].copy()

    return ModelingData(
        X_train_cycle=X_train_cycle,
        X_validation_cycle=X_validation_cycle,
        X_train_raw=X_train_raw,
        X_validation_raw=X_validation_raw,
        X_train_temporal=X_train_temporal,
        X_validation_temporal=X_validation_temporal,
        y_train=y_train,
        y_validation=y_validation,
        groups_train=groups_train,
        groups_validation=groups_validation,
        X_test_endpoint_raw=X_test_endpoint_raw,
        X_test_endpoint_temporal=X_test_endpoint_temporal,
        test_endpoint_groups=test_endpoint_groups,

        # Full-history development objects
        X_train_full_raw=X_train_full_raw,
        X_validation_full_raw=X_validation_full_raw,
        y_train_full=y_train_full,
        y_validation_full=y_validation_full,
        groups_train_full=groups_train_full,
        groups_validation_full=groups_validation_full,
    )