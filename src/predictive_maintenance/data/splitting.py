"""Utilities for leakage-safe engine-grouped dataset splitting."""

from sklearn.model_selection import GroupShuffleSplit


def grouped_train_validation_indices(
    X,
    y,
    groups,
    validation_size=0.20,
    random_state=42,
):
    """Return train/validation row indices while keeping groups intact."""

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=validation_size,
        random_state=random_state,
    )

    train_indices, validation_indices = next(
        splitter.split(
            X,
            y,
            groups=groups,
        )
    )

    return train_indices, validation_indices