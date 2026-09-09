"""Evaluation utilities for RUL regression models."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)


@dataclass(frozen=True)
class RegressionMetrics:
    """Core regression metrics used during model development."""

    rmse: float
    mae: float


def calculate_regression_metrics(
    y_true,
    y_pred,
) -> RegressionMetrics:
    """Calculate the canonical Phase 1.4 regression metrics."""

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            y_pred,
        )
    )

    mae = mean_absolute_error(
        y_true,
        y_pred,
    )

    return RegressionMetrics(
        rmse=float(rmse),
        mae=float(mae),
    )


def build_prediction_frame(
    y_true,
    y_pred,
) -> pd.DataFrame:
    """Create aligned actual, predicted, and signed-error values."""

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must contain the same number of observations."
        )

    result = pd.DataFrame(
        {
            "actual_rul": np.asarray(y_true),
            "predicted_rul": np.asarray(y_pred),
        },
        index=getattr(
            y_true,
            "index",
            None,
        ),
    )

    result["prediction_error"] = (
        result["predicted_rul"]
        - result["actual_rul"]
    )

    result["absolute_error"] = (
        result["prediction_error"]
        .abs()
    )

    return result

def calculate_rmse_reduction(
    baseline_rmse: float,
    experiment_rmse: float,
) -> tuple[float, float]:
    """Return absolute and percentage RMSE reduction versus a baseline."""

    absolute_reduction = (
        baseline_rmse
        - experiment_rmse
    )

    percentage_reduction = (
        absolute_reduction
        / baseline_rmse
        * 100
    )

    return (
        float(absolute_reduction),
        float(percentage_reduction),
    )