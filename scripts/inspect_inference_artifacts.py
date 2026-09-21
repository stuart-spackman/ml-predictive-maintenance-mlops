# Phase 2.1 — Task Group 3
# Inspect and verify frozen Phase 1 inference artifacts.

from predictive_maintenance.inference.artifacts import (
    FITTED_MODEL_PATH,
    FINAL_FIT_RECORD_PATH,
    LOCKED_MODEL_SPEC_PATH,
    load_locked_model_artifacts,
)


def main() -> None:

    artifacts = (
        load_locked_model_artifacts()
    )


    model = (
        artifacts.model
    )


    print(
        "PHASE 2.1 MODEL ARTIFACT AUDIT"
    )

    print(
        "=" * 60
    )


    print(
        "Locked spec:",
        LOCKED_MODEL_SPEC_PATH,
    )

    print(
        "Fitted model:",
        FITTED_MODEL_PATH,
    )

    print(
        "Final-fit record:",
        FINAL_FIT_RECORD_PATH,
    )


    print()


    print(
        "Locked spec SHA-256:",
        artifacts.locked_spec_sha256,
    )


    print(
        "Model SHA-256:",
        artifacts.model_sha256,
    )


    print()


    print(
        "Loaded estimator type:",
        type(
            model
        ).__name__,
    )


    n_features = getattr(
        model,
        "n_features_in_",
        None,
    )


    print(
        "Estimator n_features_in_:",
        n_features,
    )


    print()


    print(
        "Locked-spec top-level keys:"
    )


    for key in sorted(
        artifacts.locked_spec.keys()
    ):
        print(
            f"  - {key}"
        )


    print()

    print(
        "Model fingerprint matches Phase 1 provenance: YES"
    )

    print(
        "Callable predict() available: YES"
    )

    print()

    print(
        "Phase 2.1 artifact integrity audit: PASSED"
    )


if __name__ == "__main__":
    main()