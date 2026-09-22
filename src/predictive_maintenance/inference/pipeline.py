# Phase 2.1 — Task Group 4
# End-to-End RUL Prediction Pipeline
#
# Responsibility:
# - combine validated feature construction with verified Phase 1 artifacts,
# - construct the exact locked feature matrix,
# - generate one latest-cycle RUL prediction.
#
# This module NEVER fits or retrains a model.

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)

from predictive_maintenance.inference.artifacts import (
    LoadedModelArtifacts,
    load_locked_model_artifacts,
)

from predictive_maintenance.inference.features import (
    build_latest_temporal_row,
)

from predictive_maintenance.inference.schema import (
    CYCLE_COLUMN,
)

from predictive_maintenance.inference.errors import (
    InferenceFeatureError,
    InferenceModelContractError,
    InferencePredictionError,
)

@dataclass(frozen=True)
class PredictionResult:
    """
    Result of one successful Phase 2.1 inference request.
    """

    engine_id: int

    current_cycle: int

    predicted_rul: float

class RULInferencePipeline:
    """
    Production-style inference pipeline for the frozen Phase 1 model.

    The pipeline owns:

    - verified model artifacts,
    - locked feature configuration,
    - model-input construction,
    - prediction generation.

    The fitted estimator remains frozen throughout inference.
    """

    def __init__(
        self,
        artifacts: LoadedModelArtifacts,
    ) -> None:

        self._artifacts = artifacts

        self._model = artifacts.model

        self._locked_spec = artifacts.locked_spec

        self._feature_names = (
            self._read_locked_feature_names()
        )

        self._validate_model_contract()

    def _read_locked_feature_names(
        self,
    ) -> tuple[str, ...]:
        """
        Read and validate the ordered feature schema from the
        frozen Phase 1 model specification.
        """

        raw_feature_names = (
            self._locked_spec.get(
                "feature_names"
            )
        )


        if not isinstance(
            raw_feature_names,
            list,
        ):
            raise ValueError(
                "Locked model specification must contain "
                "'feature_names' as a list."
            )


        if not raw_feature_names:
            raise ValueError(
                "Locked feature list cannot be empty."
            )


        if not all(
            isinstance(
                feature,
                str,
            )
            for feature
            in raw_feature_names
        ):
            raise ValueError(
                "Every locked feature name must be a string."
            )


        if len(
            raw_feature_names
        ) != len(
            set(
                raw_feature_names
            )
        ):
            raise ValueError(
                "Locked feature names contain duplicates."
            )


        return tuple(
            raw_feature_names
        )

    def _validate_model_contract(
        self,
    ) -> None:
        """
        Verify agreement between the locked specification and
        the fitted estimator before any predictions are allowed.
        """

        locked_n_features = (
            self._locked_spec.get(
                "n_features"
            )
        )


        if locked_n_features != len(
            self._feature_names
        ):
            raise InferenceModelContractError(
                "Locked specification feature count does not match "
                "the length of feature_names."
            )


        model_n_features = getattr(
            self._model,
            "n_features_in_",
            None,
        )


        if model_n_features is None:
            raise InferenceModelContractError(
                "Loaded estimator does not expose n_features_in_."
            )


        if int(
            model_n_features
        ) != len(
            self._feature_names
        ):
            raise InferenceModelContractError(
                "Fitted estimator feature count does not match "
                "the locked specification."
            )


        # --------------------------------------------------------
        # Stronger feature-name check when sklearn recorded names
        # during fitting.
        # --------------------------------------------------------

        model_feature_names = getattr(
            self._model,
            "feature_names_in_",
            None,
        )


        if model_feature_names is not None:

            model_feature_names_tuple = tuple(
                str(
                    feature
                )
                for feature
                in model_feature_names
            )


            if model_feature_names_tuple != (
                self._feature_names
            ):
                raise ValueError(
                    "Fitted estimator feature names/order do not match "
                    "the locked model specification."
                )

    def build_model_input(
        self,
        history_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Build the exact one-row predictor matrix expected by the model.
        """

        latest_row = (
            build_latest_temporal_row(
                history_df
            )
        )


        return self._select_locked_features(
            latest_row
        )

    def predict(
        self,
        history_df: pd.DataFrame,
    ) -> PredictionResult:
        """
        Generate one latest-cycle RUL prediction for one engine history.
        """

        latest_row = (
            build_latest_temporal_row(
                history_df
            )
        )


        X = (
            self._select_locked_features(
                latest_row
            )
        )


        raw_predictions = (
            self._model.predict(
                X
            )
        )


        predictions = (
            np.asarray(
                raw_predictions,
                dtype=float,
            )
            .reshape(-1)
        )


        if predictions.shape != (
            1,
        ):
            raise InferencePredictionError(
                "Expected exactly one prediction from the fitted model."
            )


        predicted_rul = float(
            predictions[0]
        )


        if not np.isfinite(
            predicted_rul
        ):
            raise InferencePredictionError(
                "Fitted model returned a non-finite RUL prediction."
            )


        engine_id = int(
            latest_row[
                GROUP_COLUMN
            ].iloc[0]
        )


        current_cycle = int(
            latest_row[
                CYCLE_COLUMN
            ].iloc[0]
        )


        return PredictionResult(
            engine_id=engine_id,
            current_cycle=current_cycle,
            predicted_rul=predicted_rul,
        )

    def _select_locked_features(
        self,
        latest_row: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Select and validate the exact ordered predictor matrix expected
        by the frozen fitted estimator.
        """

        missing_features = [
            feature
            for feature
            in self._feature_names
            if feature
            not in latest_row.columns
        ]


        if missing_features:
            raise InferenceFeatureError(
                "Inference feature construction is missing locked "
                f"model features: {missing_features}"
            )


        X = (
            latest_row
            .loc[
                :,
                list(
                    self._feature_names
                ),
            ]
            .copy()
        )


        expected_shape = (
            1,
            len(
                self._feature_names
            ),
        )


        if X.shape != expected_shape:
            raise InferenceFeatureError(
                "Model input has unexpected shape. "
                f"Expected {expected_shape}, received {X.shape}."
            )


        if tuple(
            X.columns
        ) != self._feature_names:
            raise InferenceFeatureError(
                "Model input feature order does not match "
                "the locked specification."
            )


        if not np.isfinite(
            X.to_numpy(
                dtype=float
            )
        ).all():
            raise InferenceFeatureError(
                "Model input contains NaN or infinite values."
            )


        return X

def create_default_inference_pipeline(
) -> RULInferencePipeline:
    """
    Load and verify the frozen Phase 1 artifacts once, then construct
    the default Phase 2.1 inference pipeline.
    """

    artifacts = (
        load_locked_model_artifacts()
    )


    return RULInferencePipeline(
        artifacts=artifacts
    )