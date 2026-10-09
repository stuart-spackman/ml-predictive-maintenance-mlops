# Phase 2.2 — Task Group 7
# Final FastAPI Integration Audit & Handoff
#
# This script exercises the most important public Phase 2.2 behaviors
# using the real application and real Phase 2.1 inference pipeline.

from copy import deepcopy
import math

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


EXPECTED_ROUTE_METHODS = {
    "/health": "get",
    "/metadata": "get",
    "/predict": "post",
}

def raw_row_to_api_observation(
    row,
) -> dict:
    """
    Convert one canonical FD001 row into the public
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

def build_valid_prediction_payload() -> dict:
    """
    Build one real 20-cycle FD001 HTTP prediction payload.
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

def main() -> None:

    print(
        "PHASE 2.2 INTEGRATION AUDIT & HANDOFF"
    )

    print(
        "=" * 60
    )


    valid_payload = (
        build_valid_prediction_payload()
    )


    with TestClient(
        app
    ) as client:

        # ----------------------------------------------------
        # 1. Application-scoped inference dependency
        # ----------------------------------------------------

        pipeline = getattr(
            app.state,
            "inference_pipeline",
            None,
        )


        assert pipeline is not None


        print(
            "Application lifespan / inference dependency: PASSED"
        )

        # ----------------------------------------------------
        # 2. Public route contract
        # ----------------------------------------------------

        openapi_response = (
            client.get(
                "/openapi.json"
            )
        )


        assert (
            openapi_response.status_code
            ==
            200
        )


        paths = (
            openapi_response
            .json()[
                "paths"
            ]
        )


        for (
            path,
            method,
        ) in EXPECTED_ROUTE_METHODS.items():

            assert path in paths

            assert method in paths[
                path
            ]


        print(
            "Declared HTTP service surface: PASSED"
        )

        # ----------------------------------------------------
        # 3. Service readiness
        # ----------------------------------------------------

        health_response = (
            client.get(
                "/health"
            )
        )


        assert (
            health_response.status_code
            ==
            200
        )


        assert (
            health_response.json()
            ==
            {
                "status": "ok"
            }
        )


        print(
            "GET /health: PASSED"
        )

        # ----------------------------------------------------
        # 4. Runtime metadata
        # ----------------------------------------------------

        metadata_response = (
            client.get(
                "/metadata"
            )
        )


        assert (
            metadata_response.status_code
            ==
            200
        )


        metadata = (
            metadata_response.json()
        )


        assert (
            metadata[
                "service_version"
            ]
            ==
            app.version
        )


        assert (
            metadata[
                "dataset"
            ]
            ==
            DATASET_NAME
        )


        assert (
            metadata[
                "model_family"
            ]
            ==
            pipeline.model_family
        )


        assert (
            metadata[
                "feature_count"
            ]
            ==
            pipeline.feature_count
        )


        print(
            "GET /metadata: PASSED"
        )

        # ----------------------------------------------------
        # 5. Successful prediction
        # ----------------------------------------------------

        prediction_response = (
            client.post(
                "/predict",
                json=valid_payload,
            )
        )


        assert (
            prediction_response.status_code
            ==
            200
        )


        prediction_body = (
            prediction_response.json()
        )


        assert (
            prediction_body[
                "engine_id"
            ]
            ==
            1
        )


        assert (
            prediction_body[
                "current_cycle"
            ]
            ==
            20
        )


        assert math.isfinite(
            prediction_body[
                "predicted_rul"
            ]
        )


        print(
            "POST /predict successful path: PASSED"
        )

        print(
            "Predicted RUL:",
            prediction_body[
                "predicted_rul"
            ],
        )

        # ----------------------------------------------------
        # 6. Domain-invalid inference request
        # ----------------------------------------------------

        short_payload = deepcopy(
            valid_payload
        )


        short_payload[
            "observations"
        ] = (
            short_payload[
                "observations"
            ][:7]
        )


        short_response = (
            client.post(
                "/predict",
                json=short_payload,
            )
        )


        assert (
            short_response.status_code
            ==
            422
        )


        assert (
            short_response.json()[
                "error_code"
            ]
            ==
            "invalid_inference_request"
        )


        print(
            "Inference-domain HTTP translation: PASSED"
        )

        # ----------------------------------------------------
        # 7. API-schema rejection
        # ----------------------------------------------------

        malformed_payload = deepcopy(
            valid_payload
        )


        del (
            malformed_payload[
                "observations"
            ][0][
                "sensor_measurement_12"
            ]
        )


        malformed_response = (
            client.post(
                "/predict",
                json=malformed_payload,
            )
        )


        assert (
            malformed_response.status_code
            ==
            422
        )


        assert (
            "detail"
            in malformed_response.json()
        )


        print(
            "Pydantic/API-schema rejection: PASSED"
        )

    print()

    print(
        "Phase 2.2 integration audit: PASSED"
    )

    print(
        "Phase 2.2 is ready for handoff."
    )


if __name__ == "__main__":
    main()