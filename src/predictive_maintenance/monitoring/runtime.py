from __future__ import annotations

from collections.abc import (
    Iterable,
    Mapping,
)

import math

import pandas as pd

from predictive_maintenance.monitoring.drift import (
    classify_psi,
    population_stability_index,
)


def prediction_events_to_frame(
    events: Iterable[
        Mapping
    ],
    *,
    locked_features: list[str],
) -> pd.DataFrame:
    """
    Convert structured prediction telemetry into
    a flat monitoring dataframe.

    The model-input dictionary is keyed by feature
    name, so monitoring does not depend on JSON
    dictionary ordering.
    """

    rows = []


    expected_features = set(
        locked_features
    )


    for event in events:

        if (
            event.get(
                "event_type"
            )
            != "prediction"
        ):

            continue


        model_input = (
            event.get(
                "model_input"
            )
        )


        if not isinstance(
            model_input,
            Mapping,
        ):

            raise ValueError(
                "Prediction event is missing "
                "a valid model_input mapping."
            )


        if (
            set(
                model_input.keys()
            )
            != expected_features
        ):

            raise ValueError(
                "Prediction event model-input "
                "schema does not match the "
                "locked feature contract."
            )


        served_model = (
            event.get(
                "served_model"
            )
        )


        if not isinstance(
            served_model,
            Mapping,
        ):

            raise ValueError(
                "Prediction event is missing "
                "served-model identity."
            )


        predicted_rul = float(
            event[
                "predicted_rul"
            ]
        )


        if not math.isfinite(
            predicted_rul
        ):

            raise ValueError(
                "Prediction telemetry contains "
                "non-finite predicted_rul."
            )


        row = {
            "timestamp_utc": (
                event.get(
                    "timestamp_utc"
                )
            ),

            "request_id": (
                event.get(
                    "request_id"
                )
            ),

            "model_artifact_sha256": (
                served_model.get(
                    "model_artifact_sha256"
                )
            ),

            "locked_spec_sha256": (
                served_model.get(
                    "locked_spec_sha256"
                )
            ),

            "engine_id": int(
                event[
                    "engine_id"
                ]
            ),

            "current_cycle": int(
                event[
                    "current_cycle"
                ]
            ),

            "predicted_rul": (
                predicted_rul
            ),
        }


        for feature_name in locked_features:

            value = float(
                model_input[
                    feature_name
                ]
            )


            if not math.isfinite(
                value
            ):

                raise ValueError(
                    "Prediction telemetry contains "
                    "a non-finite feature value: "
                    f"{feature_name}"
                )


            row[
                feature_name
            ] = value


        rows.append(
            row
        )


    return pd.DataFrame(
        rows
    )


def aggregate_drift_status(
    statuses: Iterable[str],
) -> str:
    """
    Convert individual distribution states into
    one overall window state.

    Worst observed state wins.
    """

    statuses = list(
        statuses
    )


    if "alert" in statuses:

        return "alert"


    if "warning" in statuses:

        return "warning"


    return "stable"


def evaluate_runtime_window(
    *,
    reference_df: pd.DataFrame,
    prediction_events_df: pd.DataFrame,
    locked_features: list[str],
    reference_bins: dict[
        str,
        list[float],
    ],
    expected_model_sha256: str,
    expected_locked_spec_sha256: str,
    minimum_events: int,
    window_size: int,
    epsilon: float,
    warning_threshold: float,
    alert_threshold: float,
) -> dict:
    """
    Evaluate the latest production prediction window
    against the frozen Phase 3.3 reference baseline.
    """

    if (
        window_size
        < minimum_events
    ):

        raise ValueError(
            "window_size cannot be smaller "
            "than minimum_events."
        )


    available_events = len(
        prediction_events_df
    )


    if (
        available_events
        == 0
    ):

        return {
            "status": (
                "insufficient_data"
            ),

            "prediction_events_available": 0,

            "prediction_events_required": (
                minimum_events
            ),

            "distribution_results": [],
        }


    current_window = (
        prediction_events_df
        .tail(
            window_size
        )
        .copy()
    )


    # --------------------------------------------------------
    # Identity compatibility check comes before PSI.
    # --------------------------------------------------------

    model_matches = (
        current_window[
            "model_artifact_sha256"
        ]
        ==
        expected_model_sha256
    )


    spec_matches = (
        current_window[
            "locked_spec_sha256"
        ]
        ==
        expected_locked_spec_sha256
    )


    if not (
        model_matches.all()
        and spec_matches.all()
    ):

        return {
            "status": (
                "reference_incompatible"
            ),

            "prediction_events_available": (
                available_events
            ),

            "prediction_events_in_window": int(
                len(
                    current_window
                )
            ),

            "reason": (
                "At least one current prediction "
                "event does not match the model "
                "artifact and locked specification "
                "used to build the reference baseline."
            ),

            "distribution_results": [],
        }


    # --------------------------------------------------------
    # Sample sufficiency
    # --------------------------------------------------------

    if (
        len(
            current_window
        )
        < minimum_events
    ):

        return {
            "status": (
                "insufficient_data"
            ),

            "prediction_events_available": (
                available_events
            ),

            "prediction_events_required": (
                minimum_events
            ),

            "prediction_events_in_window": int(
                len(
                    current_window
                )
            ),

            "distribution_results": [],
        }


    monitored_columns = (
        locked_features
        + [
            "predicted_rul"
        ]
    )


    results = []


    # --------------------------------------------------------
    # PSI evaluation
    # --------------------------------------------------------

    for column in monitored_columns:

        psi = (
            population_stability_index(
                reference_df[
                    column
                ],

                current_window[
                    column
                ],

                cutpoints=(
                    reference_bins[
                        column
                    ]
                ),

                epsilon=(
                    epsilon
                ),
            )
        )


        status = (
            classify_psi(
                psi,

                warning_threshold=(
                    warning_threshold
                ),

                alert_threshold=(
                    alert_threshold
                ),
            )
        )


        results.append(
            {
                "distribution_type": (
                    "prediction"
                    if (
                        column
                        == "predicted_rul"
                    )
                    else
                    "model_input_feature"
                ),

                "column": (
                    column
                ),

                "psi": float(
                    psi
                ),

                "status": (
                    status
                ),
            }
        )


    overall_status = (
        aggregate_drift_status(
            result[
                "status"
            ]
            for result
            in results
        )
    )


    return {
        "status": (
            overall_status
        ),

        "prediction_events_available": (
            available_events
        ),

        "prediction_events_in_window": int(
            len(
                current_window
            )
        ),

        "prediction_events_required": (
            minimum_events
        ),

        "distribution_results": (
            results
        ),
    }