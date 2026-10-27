from __future__ import annotations

import pandas as pd
import streamlit as st

from predictive_maintenance.demo.adapters import (
    build_prediction_payload,
)

from predictive_maintenance.demo.client import (
    PredictiveMaintenanceAPIClient,
    create_default_api_client,
)

from predictive_maintenance.demo.errors import (
    DemoAPIError,
    DemoConnectionError,
    DemoInputError,
    DemoProtocolError,
)


st.set_page_config(
    page_title="Predictive Maintenance RUL Demo",
    page_icon="✈️",
    layout="wide",
)


@st.cache_resource(
    scope="session",
    on_release=lambda client: client.close(),
)
def get_api_client(
) -> PredictiveMaintenanceAPIClient:
    return create_default_api_client()


client = get_api_client()


st.title(
    "Predictive Maintenance — RUL Estimator"
)

st.write(
    "Estimate remaining useful life from historical "
    "NASA C-MAPSS turbofan sensor observations."
)


# ------------------------------------------------------------
# Backend status
# ------------------------------------------------------------

st.subheader(
    "Inference Service"
)

try:
    client.health()

except DemoConnectionError:
    st.error(
        "Inference API unavailable. "
        "Start the FastAPI service and try again."
    )

except DemoAPIError as exc:
    st.error(
        f"Inference API health check failed "
        f"with status {exc.status_code}."
    )

except DemoProtocolError:
    st.error(
        "Inference API returned an unexpected "
        "health response."
    )

else:
    st.success(
        "Inference API available."
    )


# ------------------------------------------------------------
# Metadata
# ------------------------------------------------------------

with st.expander(
    "Backend metadata"
):
    try:
        metadata = client.metadata()

    except DemoConnectionError:
        st.write(
            "Metadata unavailable because "
            "the API could not be reached."
        )

    except (
        DemoAPIError,
        DemoProtocolError,
    ):
        st.write(
            "Backend metadata could not be retrieved."
        )

    else:
        st.json(
            metadata
        )


# ------------------------------------------------------------
# Input
# ------------------------------------------------------------

st.subheader(
    "Engine History"
)

uploaded_file = st.file_uploader(
    "Upload one engine-history CSV",
    type=["csv"],
)

history_df = None
payload = None


if uploaded_file is None:
    st.info(
        "Upload a CSV containing one engine's observed "
        "history to request a prediction."
    )

else:
    try:
        history_df = pd.read_csv(
            uploaded_file
        )

    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ):
        st.error(
            "The uploaded file could not be parsed as a CSV."
        )


if history_df is not None:
    st.caption(
        f"{len(history_df)} observed cycles"
    )

    st.dataframe(
        history_df,
        hide_index=True,
        width="stretch",
    )

    try:
        payload = build_prediction_payload(
            history_df
        )

    except DemoInputError as exc:
        st.error(
            str(exc)
        )


# ------------------------------------------------------------
# Prediction
# ------------------------------------------------------------

predict_clicked = st.button(
    "Predict Remaining Useful Life",
    type="primary",
    disabled=(
        payload is None
    ),
)


if predict_clicked:
    try:
        result = client.predict(
            payload
        )

    except DemoConnectionError:
        st.error(
            "The inference API could not be reached."
        )

    except DemoAPIError as exc:
        if exc.status_code == 422:
            st.warning(
                str(exc)
            )

        else:
            st.error(
                str(exc)
            )

    except DemoProtocolError:
        st.error(
            "The inference API returned "
            "an unexpected response."
        )

    else:
        predicted_rul = result[
            "predicted_rul"
        ]

        engine_id = result[
            "engine_id"
        ]

        current_cycle = result[
            "current_cycle"
        ]

        st.subheader(
            "Prediction"
        )

        st.metric(
            "Estimated Remaining Useful Life",
            f"{predicted_rul:.1f} cycles",
        )

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**Engine:** {engine_id}"
            )

        with col2:
            st.write(
                f"**Current cycle:** {current_cycle}"
            )