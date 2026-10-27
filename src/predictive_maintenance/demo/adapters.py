from __future__ import annotations

from typing import Any

import pandas as pd

from predictive_maintenance.demo.errors import (
    DemoInputError,
)


def build_prediction_payload(
    history_df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Convert one uploaded raw engine-history DataFrame
    into the Phase 2.2 prediction-request representation.

    This function performs representation-level checks only.
    Authoritative inference-domain validation remains on
    the backend.
    """

    if history_df.empty:
        raise DemoInputError(
            "The uploaded engine-history CSV is empty."
        )

    if "unit_no" not in history_df.columns:
        raise DemoInputError(
            "The uploaded CSV must contain a 'unit_no' column."
        )

    if "cycles" not in history_df.columns:
        raise DemoInputError(
            "The uploaded CSV must contain a 'cycles' column."
        )

    engine_ids = (
        history_df["unit_no"]
        .dropna()
        .unique()
    )

    if len(engine_ids) != 1:
        raise DemoInputError(
            "The uploaded CSV must represent exactly one engine."
        )

    engine_id = engine_ids[0]

    # Convert NumPy scalar to ordinary Python scalar when needed.
    if hasattr(
        engine_id,
        "item",
    ):
        engine_id = engine_id.item()

    observation_df = (
        history_df
        .drop(
            columns=["unit_no"]
        )
        .rename(
            columns={
                "cycles": "cycle",
            }
        )
    )

    observations = (
        observation_df
        .to_dict(
            orient="records"
        )
    )

    return {
        "engine_id": engine_id,
        "observations": observations,
    }