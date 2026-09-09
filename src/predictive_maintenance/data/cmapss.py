from pathlib import Path

import pandas as pd

from predictive_maintenance.paths import CMAPSS_DATA_DIR


ID_COLUMNS = [
    "unit_no",
    "cycles",
]

OPERATING_SETTING_COLUMNS = [
    f"op_setting_{i}" for i in range(1, 4)
]

SENSOR_COLUMNS = [
    f"sensor_measurement_{i}" for i in range(1, 22)
]

CMAPSS_COLUMNS = (
    ID_COLUMNS
    + OPERATING_SETTING_COLUMNS
    + SENSOR_COLUMNS
)


def _load_engine_file(path: Path) -> pd.DataFrame:
    """Load a C-MAPSS train or test file using the standard schema."""
    return pd.read_csv(
        path,
        sep=r"\s+",
        header=None,
        names=CMAPSS_COLUMNS,
    )


def load_cmapss_subset(
    dataset_name: str,
    data_dir: Path = CMAPSS_DATA_DIR,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load train, test, and endpoint-RUL files for one C-MAPSS subset."""

    dataset_name = dataset_name.upper()

    train_path = data_dir / f"train_{dataset_name}.txt"
    test_path = data_dir / f"test_{dataset_name}.txt"
    rul_path = data_dir / f"RUL_{dataset_name}.txt"

    required_paths = [train_path, test_path, rul_path]
    missing_paths = [
        path for path in required_paths
        if not path.exists()
    ]

    if missing_paths:
        missing = "\n".join(str(path) for path in missing_paths)
        raise FileNotFoundError(
            f"Required C-MAPSS files were not found:\n{missing}"
        )

    train = _load_engine_file(train_path)
    test = _load_engine_file(test_path)

    test_rul = pd.read_csv(
        rul_path,
        sep=r"\s+",
        header=None,
        names=["endpoint_rul"],
    )

    return train, test, test_rul