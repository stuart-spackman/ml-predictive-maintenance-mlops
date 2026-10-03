# Phase 2.1 — Task Group 6
# Automated artifact-loading and integrity tests.

import json

import joblib
import pandas as pd
import pytest

from sklearn.dummy import (
    DummyRegressor,
)

import predictive_maintenance.inference.artifacts as artifact_module

from predictive_maintenance.inference.artifacts import (
    ArtifactIntegrityError,
    calculate_sha256,
    load_locked_model_artifacts,
)


def test_real_phase_1_artifacts_load_successfully():
    artifacts = (
        load_locked_model_artifacts()
    )

    assert callable(
        getattr(
            artifacts.model,
            "predict",
            None,
        )
    )

    assert (
        artifacts.locked_spec[
            "n_features"
        ]
        ==
        artifacts.model.n_features_in_
    )

def _create_temporary_valid_artifacts(
    tmp_path,
):
    """
    Create a small self-contained artifact set for destructive tests.

    These files are temporary and are NOT the real Phase 1 artifacts.
    """

    locked_spec_path = (
        tmp_path
        / "locked_spec.json"
    )

    model_path = (
        tmp_path
        / "model.joblib"
    )

    final_fit_record_path = (
        tmp_path
        / "final_fit_record.json"
    )


    # --------------------------------------------------------
    # Create a tiny fitted estimator
    # --------------------------------------------------------

    X = pd.DataFrame(
        {
            "feature_a": [
                1.0,
                2.0,
                3.0,
            ]
        }
    )

    y = [
        10.0,
        20.0,
        30.0,
    ]


    model = DummyRegressor(
        strategy="mean"
    )

    model.fit(
        X,
        y,
    )


    joblib.dump(
        model,
        model_path,
    )


    # --------------------------------------------------------
    # Create minimal locked specification
    # --------------------------------------------------------

    locked_spec = {
        "feature_names": [
            "feature_a"
        ],
        "n_features": 1,
    }


    with locked_spec_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            locked_spec,
            file,
        )


    # --------------------------------------------------------
    # Record the model fingerprint
    # --------------------------------------------------------

    model_sha256 = (
        calculate_sha256(
            model_path
        )
    )


    final_fit_record = {
        "model_sha256": model_sha256
    }


    with final_fit_record_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            final_fit_record,
            file,
        )


    return (
        locked_spec_path,
        model_path,
        final_fit_record_path,
    )

def test_model_hash_mismatch_is_rejected(
    tmp_path,
    monkeypatch,
):
    (
        locked_spec_path,
        model_path,
        final_fit_record_path,
    ) = (
        _create_temporary_valid_artifacts(
            tmp_path
        )
    )


    # --------------------------------------------------------
    # Corrupt the TEMPORARY model after its valid fingerprint
    # has already been recorded.
    # --------------------------------------------------------

    with model_path.open(
        "ab"
    ) as file:

        file.write(
            b"intentional-test-corruption"
        )


    # --------------------------------------------------------
    # Redirect the production loader only for this test.
    # --------------------------------------------------------

    monkeypatch.setattr(
        artifact_module,
        "LOCKED_MODEL_SPEC_PATH",
        locked_spec_path,
    )

    monkeypatch.setattr(
        artifact_module,
        "FITTED_MODEL_PATH",
        model_path,
    )

    monkeypatch.setattr(
        artifact_module,
        "FINAL_FIT_RECORD_PATH",
        final_fit_record_path,
    )


    with pytest.raises(
        ArtifactIntegrityError,
        match="SHA-256",
    ):
        artifact_module.load_locked_model_artifacts()