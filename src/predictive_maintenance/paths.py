import os
from pathlib import Path


_DEFAULT_PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


PROJECT_ROOT = Path(
    os.getenv(
        "PREDICTIVE_MAINTENANCE_PROJECT_ROOT",
        str(_DEFAULT_PROJECT_ROOT),
    )
).resolve()


DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

CMAPSS_DATA_DIR = RAW_DATA_DIR / "CMAPSSData"