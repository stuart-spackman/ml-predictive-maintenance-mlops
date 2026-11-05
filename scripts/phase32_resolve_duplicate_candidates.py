import mlflow
import mlflow.sklearn

from mlflow import MlflowClient
from sklearn.ensemble import (
    ExtraTreesRegressor,
)


TRACKING_URI = (
    "http://127.0.0.1:5000"
)

REGISTERED_MODEL_NAME = (
    "fd001-rul"
)


mlflow.set_tracking_uri(
    TRACKING_URI
)


client = MlflowClient()


versions = (
    client.search_model_versions(
        filter_string=(
            f"name='{REGISTERED_MODEL_NAME}'"
        )
    )
)


pending_candidates = []


for version in versions:

    full_version = (
        client.get_model_version(
            name=REGISTERED_MODEL_NAME,
            version=version.version,
        )
    )


    tags = (
        full_version.tags
        or {}
    )


    if (
        tags.get(
            "lifecycle_role"
        )
        == "candidate"
        and
        tags.get(
            "validation_status"
        )
        == "pending"
    ):

        pending_candidates.append(
            full_version
        )


if len(
    pending_candidates
) < 2:

    raise RuntimeError(
        "Expected at least two duplicate "
        "pending candidates."
    )


# ------------------------------------------------------------
# Verify every pending version is the exact frozen candidate.
# ------------------------------------------------------------

expected_params = {
    "n_estimators": 300,
    "max_depth": 20,
    "max_features": "sqrt",
    "min_samples_leaf": 2,
    "min_samples_split": 5,
}


for version in pending_candidates:

    model = (
        mlflow.sklearn.load_model(
            (
                f"models:/"
                f"{REGISTERED_MODEL_NAME}/"
                f"{version.version}"
            )
        )
    )


    if not isinstance(
        model,
        ExtraTreesRegressor,
    ):

        raise RuntimeError(
            f"Version {version.version} "
            "is not ExtraTreesRegressor."
        )


    params = model.get_params(
        deep=False
    )


    for (
        parameter,
        expected_value,
    ) in expected_params.items():

        if (
            params[
                parameter
            ]
            != expected_value
        ):

            raise RuntimeError(
                f"Version {version.version} "
                "does not match frozen recipe."
            )


    if (
        model.n_features_in_
        != 36
    ):

        raise RuntimeError(
            f"Version {version.version} "
            "does not expect 36 features."
        )


# ------------------------------------------------------------
# Highest registry version becomes authoritative candidate.
# ------------------------------------------------------------

pending_candidates = sorted(
    pending_candidates,
    key=lambda version: int(
        version.version
    ),
)


authoritative = (
    pending_candidates[-1]
)


duplicates = (
    pending_candidates[:-1]
)


print(
    "Authoritative candidate version:",
    authoritative.version,
)


# ------------------------------------------------------------
# Preserve older versions, but mark them superseded.
# ------------------------------------------------------------

for version in duplicates:

    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=version.version,
        key="validation_status",
        value="superseded",
    )


    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=version.version,
        key="lifecycle_role",
        value="candidate_duplicate",
    )


    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=version.version,
        key="superseded_by_version",
        value=authoritative.version,
    )


    print(
        "Superseded version:",
        version.version,
    )


# ------------------------------------------------------------
# Make authoritative candidate explicit.
# ------------------------------------------------------------

client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=authoritative.version,
    key="validation_status",
    value="pending",
)


client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=authoritative.version,
    key="lifecycle_role",
    value="candidate",
)


client.set_model_version_tag(
    name=REGISTERED_MODEL_NAME,
    version=authoritative.version,
    key="candidate_authority",
    value="phase32_active_candidate",
)


print(
    "\nDuplicate candidate resolution complete."
)