from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)

import hashlib
import json
import logging
from pathlib import Path
import threading
from typing import Any, Mapping


logger = logging.getLogger(
    __name__
)


# ------------------------------------------------------------
# Runtime paths
# ------------------------------------------------------------

DEFAULT_TELEMETRY_PATH = Path(
    "runtime/telemetry/events.jsonl"
)


SERVED_MODEL_ARTIFACT_PATH = Path(
    "reports/phase_16_final_fitted_model.joblib"
)


LOCKED_SPEC_PATH = Path(
    "reports/phase_16_locked_model_spec.json"
)


# ------------------------------------------------------------
# Basic helpers
# ------------------------------------------------------------

def utc_now_iso() -> str:
    """
    Return an explicit UTC timestamp suitable for telemetry.
    """

    return (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )


def sha256_file(
    path: Path,
) -> str:
    """
    Calculate SHA-256 for one file.
    """

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        for chunk in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):

            digest.update(
                chunk
            )

    return digest.hexdigest()


def _json_safe(
    value: Any,
) -> Any:
    """
    Recursively convert common NumPy / pandas scalar values
    into standard JSON-serializable Python values.
    """

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key): _json_safe(
                item
            )
            for key, item
            in value.items()
        }


    if isinstance(
        value,
        (list, tuple),
    ):
        return [
            _json_safe(
                item
            )
            for item in value
        ]


    # NumPy scalar values generally expose .item().
    if hasattr(
        value,
        "item",
    ):
        try:
            return value.item()

        except (
            ValueError,
            AttributeError,
        ):
            pass


    return value


# ------------------------------------------------------------
# Actual served-model identity
# ------------------------------------------------------------

def build_served_model_identity() -> dict:
    """
    Identify the artifact that the current FastAPI serving path
    actually loads.

    This deliberately does NOT infer model identity from the
    mutable MLflow `champion` alias.
    """

    if not SERVED_MODEL_ARTIFACT_PATH.exists():

        raise FileNotFoundError(
            "Served model artifact is missing: "
            f"{SERVED_MODEL_ARTIFACT_PATH}"
        )


    if not LOCKED_SPEC_PATH.exists():

        raise FileNotFoundError(
            "Locked model specification is missing: "
            f"{LOCKED_SPEC_PATH}"
        )


    return {
        "source": (
            "phase_16_frozen_joblib"
        ),

        "model_artifact_path": (
            str(
                SERVED_MODEL_ARTIFACT_PATH
            )
        ),

        "model_artifact_sha256": (
            sha256_file(
                SERVED_MODEL_ARTIFACT_PATH
            )
        ),

        "locked_spec_path": (
            str(
                LOCKED_SPEC_PATH
            )
        ),

        "locked_spec_sha256": (
            sha256_file(
                LOCKED_SPEC_PATH
            )
        ),
    }


# ------------------------------------------------------------
# Event builders
# ------------------------------------------------------------

def build_service_event(
    *,
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    latency_ms: float,
) -> dict:

    return {
        "schema_version": 1,

        "event_type": (
            "service_request"
        ),

        "timestamp_utc": (
            utc_now_iso()
        ),

        "request_id": (
            request_id
        ),

        "method": (
            method
        ),

        "path": (
            path
        ),

        "status_code": int(
            status_code
        ),

        "success": bool(
            200
            <= status_code
            < 300
        ),

        "latency_ms": float(
            latency_ms
        ),
    }


def build_prediction_event(
    *,
    request_id: str,
    model_identity: Mapping[
        str,
        Any,
    ],
    engine_id: int,
    current_cycle: int,
    predicted_rul: float,
    inference_latency_ms: float,
    model_input: Mapping[
        str,
        Any,
    ],
) -> dict:

    return {
        "schema_version": 1,

        "event_type": (
            "prediction"
        ),

        "timestamp_utc": (
            utc_now_iso()
        ),

        "request_id": (
            request_id
        ),

        "served_model": dict(
            model_identity
        ),

        "engine_id": int(
            engine_id
        ),

        "current_cycle": int(
            current_cycle
        ),

        "predicted_rul": float(
            predicted_rul
        ),

        "inference_latency_ms": float(
            inference_latency_ms
        ),

        "model_input": dict(
            model_input
        ),
    }


# ------------------------------------------------------------
# Append-only local telemetry store
# ------------------------------------------------------------

class JsonlTelemetryStore:
    """
    Minimal process-local append-only JSONL telemetry store.

    This is appropriate for the local portfolio deployment.
    It is not intended to substitute for a distributed
    production observability backend.
    """

    def __init__(
        self,
        path: Path = DEFAULT_TELEMETRY_PATH,
    ) -> None:

        self.path = Path(
            path
        )

        self._write_lock = (
            threading.Lock()
        )


    def append(
        self,
        event: Mapping[
            str,
            Any,
        ],
    ) -> None:

        safe_event = (
            _json_safe(
                dict(
                    event
                )
            )
        )


        # Fail rather than silently serialize NaN / infinity,
        # because those are not valid monitoring values.
        line = json.dumps(
            safe_event,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            allow_nan=False,
        )


        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        with self._write_lock:

            with self.path.open(
                "a",
                encoding="utf-8",
            ) as file:

                file.write(
                    line
                    + "\n"
                )


    def try_append(
        self,
        event: Mapping[
            str,
            Any,
        ],
    ) -> bool:
        """
        Best-effort telemetry.

        Monitoring failure must not turn a valid prediction
        request into an application failure.
        """

        try:

            self.append(
                event
            )

            return True

        except Exception:

            logger.exception(
                "Failed to write telemetry event."
            )

            return False