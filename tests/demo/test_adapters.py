import pandas as pd
import pytest

from predictive_maintenance.demo.adapters import (
    build_prediction_payload,
)

from predictive_maintenance.demo.errors import (
    DemoInputError,
)


def test_build_prediction_payload_maps_engine_and_cycles():
    history_df = pd.DataFrame(
        {
            "unit_no": [7, 7],
            "cycles": [1, 2],
            "sensor_1": [100.0, 101.0],
        }
    )

    payload = build_prediction_payload(
        history_df
    )

    assert payload["engine_id"] == 7

    assert payload["observations"][0][
        "cycle"
    ] == 1

    assert (
        "unit_no"
        not in payload["observations"][0]
    )

    assert (
        "cycles"
        not in payload["observations"][0]
    )


def test_build_prediction_payload_rejects_multiple_engines():
    history_df = pd.DataFrame(
        {
            "unit_no": [1, 2],
            "cycles": [1, 1],
        }
    )

    with pytest.raises(
        DemoInputError
    ):
        build_prediction_payload(
            history_df
        )