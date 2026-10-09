# Phase 2.2 — Task Group 6
# Automated tests for health and metadata endpoints.

from predictive_maintenance.api.main import (
    app,
)

from predictive_maintenance.config import (
    DATASET_NAME,
)


def test_health_returns_ok(
    api_client,
):
    response = (
        api_client.get(
            "/health"
        )
    )


    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }

def test_metadata_matches_running_application(
    api_client,
):
    response = (
        api_client.get(
            "/metadata"
        )
    )


    assert response.status_code == 200


    body = response.json()


    # Metadata should describe the application and pipeline that are
    # actually running rather than duplicating hard-coded truths.

    pipeline = (
        app.state
        .inference_pipeline
    )


    assert (
        body[
            "service_version"
        ]
        ==
        app.version
    )

    assert (
        body[
            "dataset"
        ]
        ==
        DATASET_NAME
    )

    assert (
        body[
            "model_family"
        ]
        ==
        pipeline.model_family
    )

    assert (
        body[
            "feature_count"
        ]
        ==
        pipeline.feature_count
    )

def test_openapi_contains_expected_routes(
    api_client,
):
    response = (
        api_client.get(
            "/openapi.json"
        )
    )


    assert response.status_code == 200


    paths = response.json()[
        "paths"
    ]


    assert "get" in paths[
        "/health"
    ]

    assert "get" in paths[
        "/metadata"
    ]

    assert "post" in paths[
        "/predict"
    ]