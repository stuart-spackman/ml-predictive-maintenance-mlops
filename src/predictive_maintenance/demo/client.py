from __future__ import annotations

import os
from typing import Any

import httpx

from predictive_maintenance.demo.errors import (
    DemoAPIError,
    DemoConnectionError,
    DemoProtocolError,
)


DEFAULT_API_URL = "http://127.0.0.1:8000"
DEFAULT_TIMEOUT_SECONDS = 5.0

API_URL_ENV_VAR = (
    "PREDICTIVE_MAINTENANCE_API_URL"
)


class PredictiveMaintenanceAPIClient:
    """
    Thin HTTP client for the predictive-maintenance FastAPI service.

    This class knows the public HTTP contract.

    It does NOT:
    - load model artifacts,
    - validate inference-domain rules,
    - engineer features,
    - or generate predictions locally.
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_API_URL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
        )

    def close(self) -> None:
        self._client.close()

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = self._client.request(
                method,
                path,
                json=json,
            )

        except httpx.RequestError as exc:
            raise DemoConnectionError(
                "Could not communicate with the inference API."
            ) from exc

        # HTTP 4xx / 5xx response
        if response.is_error:
            try:
                error_payload = response.json()
            except ValueError:
                error_payload = {}

            error_code = None
            message = (
                f"API request failed with status "
                f"{response.status_code}."
            )

            if isinstance(
                error_payload,
                dict,
            ):
                error_code = error_payload.get(
                    "error_code"
                )

                public_message = error_payload.get(
                    "message"
                )

                if isinstance(
                    public_message,
                    str,
                ):
                    message = public_message

                elif "detail" in error_payload:
                    message = (
                        f"API request failed with status "
                        f"{response.status_code}. "
                        f"Details: {error_payload['detail']}"
                    )

            raise DemoAPIError(
                status_code=response.status_code,
                error_code=error_code,
                message=message,
            )

        # Successful HTTP status, but response must still be valid JSON.
        try:
            payload = response.json()

        except ValueError as exc:
            raise DemoProtocolError(
                "API returned a successful response "
                "that was not valid JSON."
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise DemoProtocolError(
                "API returned JSON in an unexpected format."
            )

        return payload

    def health(
        self,
    ) -> dict[str, Any]:
        return self._request_json(
            "GET",
            "/health",
        )

    def metadata(
        self,
    ) -> dict[str, Any]:
        return self._request_json(
            "GET",
            "/metadata",
        )

    def predict(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
    
        response_payload = (
            self._request_json(
                "POST",
                "/predict",
                json=payload,
            )
        )
    
        required_fields = {
            "engine_id",
            "current_cycle",
            "predicted_rul",
        }
    
        missing_fields = (
            required_fields
            - set(
                response_payload
            )
        )
    
        if missing_fields:
            raise DemoProtocolError(
                "Prediction response is missing required fields: "
                f"{sorted(missing_fields)}"
            )
    
        return response_payload


def create_default_api_client(
) -> PredictiveMaintenanceAPIClient:
    base_url = os.getenv(
        API_URL_ENV_VAR,
        DEFAULT_API_URL,
    )

    return PredictiveMaintenanceAPIClient(
        base_url=base_url
    )