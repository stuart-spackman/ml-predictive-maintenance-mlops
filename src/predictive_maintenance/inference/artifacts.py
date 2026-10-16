# Phase 2.1 — Task Group 3
# Locked Model Artifact Loading & Integrity Verification
#
# Responsibility:
# - locate the frozen Phase 1 inference artifacts,
# - load locked configuration metadata,
# - verify the fitted model's fingerprint,
# - deserialize the fitted estimator.
#
# This module NEVER fits or retrains a model.

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import joblib

from predictive_maintenance.inference.errors import (
    InferenceArtifactError,
)

from predictive_maintenance.paths import (
    REPORTS_DIR,
)

# ------------------------------------------------------------
# Project artifact locations
# ------------------------------------------------------------

LOCKED_MODEL_SPEC_PATH = (
    REPORTS_DIR
    / "phase_16_locked_model_spec.json"
)

FITTED_MODEL_PATH = (
    REPORTS_DIR
    / "phase_16_final_fitted_model.joblib"
)

FINAL_FIT_RECORD_PATH = (
    REPORTS_DIR
    / "phase_16_final_fit_record.json"
)


class ArtifactIntegrityError(
    InferenceArtifactError
):
    """
    Raised when a frozen Phase 1 artifact is missing, malformed,
    inconsistent, or fails integrity verification.
    """

@dataclass(frozen=True)
class LoadedModelArtifacts:
    """
    Verified Phase 1 artifacts required for inference.
    """

    locked_spec: dict[str, Any]

    final_fit_record: dict[str, Any]

    model: Any

    locked_spec_sha256: str

    model_sha256: str

def calculate_sha256(
    file_path: Path,
) -> str:
    """
    Calculate the SHA-256 fingerprint of a file.

    Files are read in chunks so this works without loading the entire
    artifact into memory at once.
    """

    sha256 = hashlib.sha256()

    with file_path.open(
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()

def load_json_object(
    file_path: Path,
) -> dict[str, Any]:
    """
    Load a JSON file and require its top-level value to be an object.
    """

    if not file_path.exists():
        raise ArtifactIntegrityError(
            f"Required artifact does not exist: {file_path}"
        )

    try:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

    except json.JSONDecodeError as error:
        raise ArtifactIntegrityError(
            f"Artifact is not valid JSON: {file_path}"
        ) from error


    if not isinstance(
        data,
        dict,
    ):
        raise ArtifactIntegrityError(
            "Expected JSON artifact to contain a top-level object: "
            f"{file_path}"
        )


    return data


def _collect_string_values(
    value: Any,
) -> list[str]:
    """
    Recursively collect string values from nested JSON-compatible data.
    """

    collected: list[str] = []


    if isinstance(
        value,
        str,
    ):
        collected.append(
            value
        )


    elif isinstance(
        value,
        dict,
    ):

        for nested_value in value.values():

            collected.extend(
                _collect_string_values(
                    nested_value
                )
            )


    elif isinstance(
        value,
        list,
    ):

        for nested_value in value:

            collected.extend(
                _collect_string_values(
                    nested_value
                )
            )


    return collected

def metadata_contains_sha256(
    metadata: dict[str, Any],
    sha256_digest: str,
) -> bool:
    """
    Return True if an exact SHA-256 string appears anywhere in metadata.
    """

    string_values = (
        _collect_string_values(
            metadata
        )
    )


    normalized_digest = (
        sha256_digest
        .strip()
        .lower()
    )


    return any(
        value.strip().lower()
        == normalized_digest

        for value
        in string_values
    )

def load_locked_model_artifacts(
) -> LoadedModelArtifacts:
    """
    Load and verify the frozen Phase 1 artifacts required for inference.

    Important:
    This function DESERIALIZES the fitted model.
    It never calls `.fit()`.
    """

    # --------------------------------------------------------
    # 1. Required file existence
    # --------------------------------------------------------

    required_paths = (
        LOCKED_MODEL_SPEC_PATH,
        FITTED_MODEL_PATH,
        FINAL_FIT_RECORD_PATH,
    )


    missing_paths = [
        path
        for path
        in required_paths
        if not path.exists()
    ]


    if missing_paths:
        raise ArtifactIntegrityError(
            "Required Phase 1 inference artifacts are missing: "
            f"{missing_paths}"
        )


    # --------------------------------------------------------
    # 2. Load human/machine-readable metadata
    # --------------------------------------------------------

    locked_spec = (
        load_json_object(
            LOCKED_MODEL_SPEC_PATH
        )
    )


    final_fit_record = (
        load_json_object(
            FINAL_FIT_RECORD_PATH
        )
    )


    if not locked_spec:
        raise ArtifactIntegrityError(
            "Locked model specification is empty."
        )


    # --------------------------------------------------------
    # 3. Calculate current fingerprints BEFORE model loading
    # --------------------------------------------------------

    locked_spec_sha256 = (
        calculate_sha256(
            LOCKED_MODEL_SPEC_PATH
        )
    )


    model_sha256 = (
        calculate_sha256(
            FITTED_MODEL_PATH
        )
    )


    # --------------------------------------------------------
    # 4. Verify the fitted artifact against Phase 1 provenance
    # --------------------------------------------------------

    if not metadata_contains_sha256(
        metadata=final_fit_record,
        sha256_digest=model_sha256,
    ):
        raise ArtifactIntegrityError(
            "The fitted model SHA-256 does not match the fingerprint "
            "recorded in the Phase 1 final-fit provenance."
        )


    # --------------------------------------------------------
    # 5. Deserialize the already-fitted estimator
    # --------------------------------------------------------

    try:
        model = joblib.load(
            FITTED_MODEL_PATH
        )

    except Exception as error:
        raise ArtifactIntegrityError(
            "The fitted model artifact could not be deserialized."
        ) from error


    # --------------------------------------------------------
    # 6. Minimal behavioral interface check
    # --------------------------------------------------------

    if not callable(
        getattr(
            model,
            "predict",
            None,
        )
    ):
        raise ArtifactIntegrityError(
            "Loaded artifact does not expose a callable predict() method."
        )


    return LoadedModelArtifacts(
        locked_spec=locked_spec,
        final_fit_record=final_fit_record,
        model=model,
        locked_spec_sha256=locked_spec_sha256,
        model_sha256=model_sha256,
    )