# Phase 2.2 — Task Group 6
# Shared fixtures for FastAPI tests.

import pytest

from fastapi.testclient import (
    TestClient,
)

from predictive_maintenance.api.main import (
    app,
)

from predictive_maintenance.config import (
    DATASET_NAME,
)

from predictive_maintenance.data.cmapss import (
    load_cmapss_subset,
)

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)


@pytest.fixture(
    scope="session"
)
def api_client():
    """
    Run one FastAPI application lifecycle for the API test session.

    Entering TestClient runs lifespan startup, including loading and
    verifying the Phase 2.1 inference pipeline.

    Leaving the context runs lifespan shutdown.
    """

    with TestClient(
        app
    ) as client:

        yield client

def raw_row_to_api_observation(
    row,
) -> dict:
    """
    Convert one FD001 dataframe row into the public API
    EngineObservation representation.
    """

    observation = {
        "cycle": int(
            row["cycles"]
        ),
        "op_setting_1": float(
            row["op_setting_1"]
        ),
        "op_setting_2": float(
            row["op_setting_2"]
        ),
        "op_setting_3": float(
            row["op_setting_3"]
        ),
    }


    for sensor_number in range(
        1,
        22,
    ):

        column = (
            f"sensor_measurement_{sensor_number}"
        )


        observation[column] = float(
            row[column]
        )


    return observation


@pytest.fixture(
    scope="session"
)
def valid_prediction_payload():
    """
    Build one real 20-cycle FD001 prediction request.
    """

    development_raw_df, _, _ = (
        load_cmapss_subset(
            DATASET_NAME
        )
    )


    engine_history = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(1)
        ]
        .head(20)
        .copy()
    )


    return {
        "engine_id": 1,
        "observations": [
            raw_row_to_api_observation(
                row
            )

            for _, row
            in engine_history.iterrows()
        ],
    }