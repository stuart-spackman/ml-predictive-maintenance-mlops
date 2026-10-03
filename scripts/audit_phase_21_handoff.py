# Phase 2.1 — Task Group 7
# Final Integration Audit & Handoff
#
# This script checks that the Phase 2.1 inference subsystem is ready
# to be consumed by Phase 2.2 without exposing or duplicating its internals.

import ast
from pathlib import Path

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

from predictive_maintenance.inference.artifacts import (
    load_locked_model_artifacts,
)

from predictive_maintenance.inference.errors import (
    InferenceInputError,
)

from predictive_maintenance.inference.pipeline import (
    create_default_inference_pipeline,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

INFERENCE_PACKAGE_DIR = (
    PROJECT_ROOT
    / "src"
    / "predictive_maintenance"
    / "inference"
)

def find_fit_calls(
    directory: Path,
) -> list[str]:
    """
    Return source locations containing actual Python calls to `.fit(...)`.

    We use the Python AST instead of a plain text search so comments and
    documentation mentioning `.fit()` do not trigger false positives.
    """

    violations: list[str] = []


    for file_path in sorted(
        directory.glob(
            "*.py"
        )
    ):

        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source,
            filename=str(
                file_path
            ),
        )


        for node in ast.walk(
            tree
        ):

            if not isinstance(
                node,
                ast.Call,
            ):
                continue


            if not isinstance(
                node.func,
                ast.Attribute,
            ):
                continue


            if node.func.attr == "fit":

                violations.append(
                    f"{file_path.name}:{node.lineno}"
                )


    return violations

def find_fastapi_imports(
    directory: Path,
) -> list[str]:
    """
    Detect imports of FastAPI inside the Phase 2.1 inference package.

    Phase 2.1 should remain transport-independent.
    """

    violations: list[str] = []


    for file_path in sorted(
        directory.glob(
            "*.py"
        )
    ):

        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source,
            filename=str(
                file_path
            ),
        )


        for node in ast.walk(
            tree
        ):

            if isinstance(
                node,
                ast.Import,
            ):

                for alias in node.names:

                    if (
                        alias.name
                        == "fastapi"
                        or alias.name.startswith(
                            "fastapi."
                        )
                    ):

                        violations.append(
                            f"{file_path.name}:{node.lineno}"
                        )


            elif isinstance(
                node,
                ast.ImportFrom,
            ):

                module = (
                    node.module
                    or ""
                )


                if (
                    module
                    == "fastapi"
                    or module.startswith(
                        "fastapi."
                    )
                ):

                    violations.append(
                        f"{file_path.name}:{node.lineno}"
                    )


    return violations

def main() -> None:

    print(
        "PHASE 2.1 INTEGRATION AUDIT & HANDOFF"
    )

    print(
        "=" * 60
    )


    # --------------------------------------------------------
    # 1. Verify frozen artifacts
    # --------------------------------------------------------

    artifacts = (
        load_locked_model_artifacts()
    )


    locked_features = tuple(
        artifacts.locked_spec[
            "feature_names"
        ]
    )


    assert len(
        locked_features
    ) == 36


    assert int(
        artifacts.model.n_features_in_
    ) == 36


    print(
        "Frozen artifact verification: PASSED"
    )

    print(
        "Locked feature count:",
        len(
            locked_features
        ),
    )

    print(
        "Estimator type:",
        type(
            artifacts.model
        ).__name__,
    )


    # --------------------------------------------------------
    # 2. Create the public inference pipeline
    # --------------------------------------------------------

    pipeline = (
        create_default_inference_pipeline()
    )


    print(
        "Default inference pipeline creation: PASSED"
    )


    # --------------------------------------------------------
    # 3. Load real FD001 history
    # --------------------------------------------------------

    development_raw_df, _, _ = (
        load_cmapss_subset(
            DATASET_NAME
        )
    )


    engine_id = 1

    valid_history = (
        development_raw_df
        .loc[
            development_raw_df[
                GROUP_COLUMN
            ]
            .eq(
                engine_id
            )
        ]
        .head(20)
        .copy()
    )


    # --------------------------------------------------------
    # 4. Verify exact model-ready matrix
    # --------------------------------------------------------

    X = (
        pipeline.build_model_input(
            valid_history
        )
    )


    assert X.shape == (
        1,
        36,
    )


    assert tuple(
        X.columns
    ) == locked_features


    print(
        "Locked model-input construction: PASSED"
    )


    # --------------------------------------------------------
    # 5. Verify successful prediction
    # --------------------------------------------------------

    result = (
        pipeline.predict(
            valid_history
        )
    )


    assert result.engine_id == (
        engine_id
    )

    assert result.current_cycle == 20

    assert np.isfinite(
        result.predicted_rul
    )


    print(
        "End-to-end prediction: PASSED"
    )

    print(
        "Predicted RUL:",
        result.predicted_rul,
    )


    # --------------------------------------------------------
    # 6. Verify expected input failure
    # --------------------------------------------------------

    invalid_history = (
        valid_history
        .head(7)
        .copy()
    )


    try:

        pipeline.predict(
            invalid_history
        )

    except InferenceInputError:

        print(
            "Known invalid-input handling: PASSED"
        )

    else:

        raise AssertionError(
            "Invalid engine history unexpectedly produced a prediction."
        )


    # --------------------------------------------------------
    # 7. Verify inference contains no training calls
    # --------------------------------------------------------

    fit_calls = (
        find_fit_calls(
            INFERENCE_PACKAGE_DIR
        )
    )


    assert not fit_calls, (
        "Phase 2.1 inference package contains unexpected `.fit()` calls: "
        f"{fit_calls}"
    )


    print(
        "No model fitting inside inference package: PASSED"
    )


    # --------------------------------------------------------
    # 8. Verify transport independence
    # --------------------------------------------------------

    fastapi_imports = (
        find_fastapi_imports(
            INFERENCE_PACKAGE_DIR
        )
    )


    assert not fastapi_imports, (
        "Phase 2.1 inference package unexpectedly depends on FastAPI: "
        f"{fastapi_imports}"
    )


    print(
        "Inference package remains FastAPI-independent: PASSED"
    )


    print()
    print(
        "Phase 2.1 integration audit: PASSED"
    )

    print(
        "Phase 2.1 is ready for Phase 2.2 model serving."
    )


if __name__ == "__main__":
    main()