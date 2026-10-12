# Phase 2.3 — Task Group 1
# Shared API test infrastructure.

from copy import deepcopy

import pytest

from fastapi.testclient import (
    TestClient,
)

from predictive_maintenance.api.dependencies import (
    get_inference_pipeline,
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


# ------------------------------------------------------------
# Application lifecycle
# ------------------------------------------------------------

@pytest.fixture(
    scope="session"
)
def api_client():
    """
    Run one real FastAPI lifespan for the API test session.

    The verified inference pipeline is therefore loaded once and
    reused across API tests.
    """

    with TestClient(
        app
    ) as client:

        yield client

def raw_row_to_api_observation(
    row,
) -> dict:

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
def _prediction_payload_template():
    """
    Build one canonical 20-cycle API request template.

    Tests should not mutate this shared session-scoped object directly.
    Function-scoped fixtures below return fresh copies.
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

@pytest.fixture
def prediction_payload_factory(
    _prediction_payload_template,
):
    """
    Return a factory that creates fresh API payloads.

    Each call receives an independent deep copy so tests can safely
    mutate their own payload.
    """

    def build_payload(
        *,
        n_cycles: int = 20,
    ) -> dict:

        payload = deepcopy(
            _prediction_payload_template
        )


        payload[
            "observations"
        ] = payload[
            "observations"
        ][:n_cycles]


        return payload


    return build_payload

@pytest.fixture
def valid_prediction_payload(
    prediction_payload_factory,
):
    """
    Fresh known-good prediction request for one test.
    """

    return prediction_payload_factory()

def test_short_history_returns_domain_422(
    api_client,
    prediction_payload_factory,
):

    payload = (
        prediction_payload_factory(
            n_cycles=7
        )
    )


    response = (
        api_client.post(
            "/predict",
            json=payload,
        )
    )


    assert response.status_code == 422

    assert (
        response.json()[
            "error_code"
        ]
        ==
        "invalid_inference_request"
    )

@pytest.fixture
def override_inference_pipeline():
    """
    Temporarily replace FastAPI's inference-pipeline dependency.

    The complete dependency-overrides dictionary is restored after
    the test, even if the test fails.
    """

    original_overrides = dict(
        app.dependency_overrides
    )


    def install_override(
        pipeline,
    ) -> None:

        app.dependency_overrides[
            get_inference_pipeline
        ] = (
            lambda: pipeline
        )


    yield install_override


    app.dependency_overrides.clear()

    app.dependency_overrides.update(
        original_overrides
    )