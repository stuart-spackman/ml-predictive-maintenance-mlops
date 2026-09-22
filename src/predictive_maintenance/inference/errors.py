# Phase 2.1 — Task Group 5
# Inference Error Taxonomy
#
# These exception classes give different failure categories explicit meaning.
#
# Later, FastAPI can translate these categories into appropriate HTTP
# responses without putting domain logic inside the transport layer.


class InferenceError(Exception):
    """
    Base exception for known Phase 2 inference failures.
    """


class InferenceInputError(InferenceError):
    """
    Incoming engine history violates the inference contract.
    """


class InferenceArtifactError(InferenceError):
    """
    Required frozen model artifacts are missing, malformed,
    inconsistent, or fail integrity verification.
    """


class InferenceFeatureError(InferenceError):
    """
    Validated input could not be transformed into the required
    model-ready feature representation.
    """


class InferenceModelContractError(InferenceError):
    """
    The locked specification and fitted estimator disagree.
    """


class InferencePredictionError(InferenceError):
    """
    The fitted estimator produced an invalid prediction result.
    """