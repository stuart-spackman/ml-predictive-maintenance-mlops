import mlflow

from mlflow import MlflowClient


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


versions = sorted(
    versions,
    key=lambda version: int(
        version.version
    ),
)


for version in versions:

    full_version = (
        client.get_model_version(
            name=REGISTERED_MODEL_NAME,
            version=version.version,
        )
    )

    print(
        "\nVersion:",
        version.version,
    )

    print(
        "Run ID:",
        version.run_id,
    )

    print(
        "Creation timestamp:",
        version.creation_timestamp,
    )

    print(
        "Tags:",
        full_version.tags,
    )