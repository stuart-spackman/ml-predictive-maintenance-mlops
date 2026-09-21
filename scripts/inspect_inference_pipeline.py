# Phase 2.1 — Task Group 4
# Exercise the complete production-style inference pipeline.

import numpy as np

from predictive_maintenance.config import (
    DATASET_NAME,
)

from predictive_maintenance.data.cmapss import (
    load_cmapss_subset,
)

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)

from predictive_maintenance.inference.pipeline import (
    create_default_inference_pipeline,
)


def main() -> None:

    development_raw_df, _, _ = (
        load_cmapss_subset(
            DATASET_NAME
        )
    )


    engine_id = 1

    history_cycles = 20


    engine_history = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(
                engine_id
            )
        ]
        .head(
            history_cycles
        )
        .copy()
    )


    # --------------------------------------------------------
    # Load + verify frozen artifacts once
    # --------------------------------------------------------

    pipeline = (
        create_default_inference_pipeline()
    )


    # --------------------------------------------------------
    # Inspect exact model input
    # --------------------------------------------------------

    X = (
        pipeline.build_model_input(
            engine_history
        )
    )


    print(
        "PHASE 2.1 END-TO-END INFERENCE AUDIT"
    )

    print(
        "=" * 60
    )


    print(
        "Engine:",
        engine_id,
    )


    print(
        "Observed history cycles:",
        len(
            engine_history
        ),
    )


    print(
        "Model input shape:",
        X.shape,
    )


    print(
        "Model input feature count:",
        X.shape[1],
    )


    print()


    print(
        "First five locked predictors:"
    )


    for feature in list(
        X.columns
    )[:5]:
        print(
            f"  - {feature}"
        )


    # --------------------------------------------------------
    # Generate prediction
    # --------------------------------------------------------

    result = (
        pipeline.predict(
            engine_history
        )
    )


    print()


    print(
        "Prediction result:"
    )


    print(
        "  Engine:",
        result.engine_id,
    )


    print(
        "  Current cycle:",
        result.current_cycle,
    )


    print(
        "  Predicted RUL:",
        result.predicted_rul,
    )


    # --------------------------------------------------------
    # Basic end-to-end assertions
    # --------------------------------------------------------

    assert X.shape == (
        1,
        36,
    )


    assert result.engine_id == (
        engine_id
    )


    assert result.current_cycle == (
        history_cycles
    )


    assert np.isfinite(
        result.predicted_rul
    )


    # --------------------------------------------------------
    # Deterministic repeated inference
    # --------------------------------------------------------

    repeated_result = (
        pipeline.predict(
            engine_history
        )
    )


    assert np.isclose(
        result.predicted_rul,
        repeated_result.predicted_rul,
    )


    print()

    print(
        "Repeated identical request gives identical prediction: YES"
    )

    print(
        "End-to-end inference audit: PASSED"
    )


if __name__ == "__main__":
    main()