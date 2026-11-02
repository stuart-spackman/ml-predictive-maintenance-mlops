from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn


REPORTS_DIR = Path("reports")

TG1_SUMMARY_PATH = (
    REPORTS_DIR
    / "phase_31_tg1_challenger_summary.csv"
)

TG2_SUMMARY_PATH = (
    REPORTS_DIR
    / "phase_31_tg2_tuning_summary.csv"
)

TG3_SUMMARY_PATH = (
    REPORTS_DIR
    / "phase_31_tg3_weighting_summary.csv"
)

TG3_RECIPE_PATH = (
    REPORTS_DIR
    / "phase_31_tg3_fixed_challenger_recipe.json"
)

PHASE31_CONTRACT_PATH = (
    REPORTS_DIR
    / "phase_31_experiment_contract.json"
)

LOCKED_SPEC_PATH = (
    REPORTS_DIR
    / "phase_16_locked_model_spec.json"
)

PYPROJECT_PATH = Path(
    "pyproject.toml"
)

CONSTRAINTS_PATH = Path(
    "requirements/constraints.txt"
)


# ------------------------------------------------------------
# 1. Helpers
# ------------------------------------------------------------

def sha256_file(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        for chunk in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def git_output(
    *args: str,
) -> str:

    result = subprocess.run(
        [
            "git",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


def require_file(
    path: Path,
) -> None:

    if not path.exists():
        raise FileNotFoundError(
            f"Required evidence file "
            f"does not exist: {path}"
        )


# ------------------------------------------------------------
# 2. Verify required evidence
# ------------------------------------------------------------

required_files = [
    TG1_SUMMARY_PATH,
    TG2_SUMMARY_PATH,
    TG3_SUMMARY_PATH,
    TG3_RECIPE_PATH,
    PHASE31_CONTRACT_PATH,
    LOCKED_SPEC_PATH,
    PYPROJECT_PATH,
    CONSTRAINTS_PATH,
]


for path in required_files:
    require_file(
        path
    )


# ------------------------------------------------------------
# 3. Load experimental evidence
# ------------------------------------------------------------

tg1 = pd.read_csv(
    TG1_SUMMARY_PATH
)

tg2 = pd.read_csv(
    TG2_SUMMARY_PATH
)

tg3 = pd.read_csv(
    TG3_SUMMARY_PATH
)


ledger_records = []


# ------------------------------------------------------------
# 4. TG1: model-family screening
# ------------------------------------------------------------

for _, row in tg1.iterrows():

    ledger_records.append(
        {
            "experiment_id": (
                f"phase31_tg1_{row['model']}"
            ),

            "task_group": "TG1",

            "experiment_type": (
                "model_family_screening"
            ),

            "candidate": row[
                "model"
            ],

            "training_objective": (
                "unweighted_rows"
            ),

            "feature_count": 36,

            "evaluation_procedure": (
                "5-fold engine-grouped OOF CV"
            ),

            "pooled_oof_rmse": row[
                "pooled_oof_rmse"
            ],

            "pooled_oof_mae": row[
                "pooled_oof_mae"
            ],

            "source_file": str(
                TG1_SUMMARY_PATH
            ),
        }
    )


# ------------------------------------------------------------
# 5. TG2: nested tuning comparison
# ------------------------------------------------------------

for _, row in tg2.iterrows():

    ledger_records.append(
        {
            "experiment_id": (
                f"phase31_tg2_{row['model']}"
            ),

            "task_group": "TG2",

            "experiment_type": (
                "nested_hyperparameter_tuning"
            ),

            "candidate": row[
                "model"
            ],

            "training_objective": (
                "unweighted_rows"
            ),

            "feature_count": 36,

            "evaluation_procedure": (
                "5 outer grouped folds; "
                "challenger tuned with "
                "3 inner grouped folds "
                "and 6 sampled configurations"
            ),

            "pooled_oof_rmse": row[
                "pooled_oof_rmse"
            ],

            "pooled_oof_mae": row[
                "pooled_oof_mae"
            ],

            "source_file": str(
                TG2_SUMMARY_PATH
            ),
        }
    )


# ------------------------------------------------------------
# 6. TG3: weighting experiment
# ------------------------------------------------------------

for _, row in tg3.iterrows():

    ledger_records.append(
        {
            "experiment_id": (
                "phase31_tg3_"
                f"{row['training_objective']}"
            ),

            "task_group": "TG3",

            "experiment_type": (
                "training_weighting"
            ),

            "candidate": (
                "fixed_extra_trees"
            ),

            "training_objective": row[
                "training_objective"
            ],

            "feature_count": 36,

            "evaluation_procedure": (
                "5-fold engine-grouped OOF CV "
                "using one fixed Extra Trees recipe"
            ),

            "pooled_oof_rmse": row[
                "pooled_oof_rmse"
            ],

            "pooled_oof_mae": row[
                "pooled_oof_mae"
            ],

            "source_file": str(
                TG3_SUMMARY_PATH
            ),
        }
    )


ledger = pd.DataFrame(
    ledger_records
)


# ------------------------------------------------------------
# 7. Save human-readable experiment ledger
# ------------------------------------------------------------

ledger_path = (
    REPORTS_DIR
    / "phase_31_experiment_ledger.csv"
)


ledger.to_csv(
    ledger_path,
    index=False,
)


# ------------------------------------------------------------
# 8. Record repository/environment provenance
# ------------------------------------------------------------

git_commit = git_output(
    "rev-parse",
    "HEAD",
)


git_status = git_output(
    "status",
    "--porcelain",
)


git_dirty = bool(
    git_status
)


with TG3_RECIPE_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    challenger_recipe = (
        json.load(
            file
        )
    )


manifest = {
    "phase": "3.1",

    "generated_at_utc": (
        datetime.now(
            timezone.utc
        ).isoformat()
    ),

    "dataset": (
        "NASA C-MAPSS FD001"
    ),

    "primary_metric": (
        "pooled_oof_rmse"
    ),

    "feature_count": 36,

    "git": {
        "commit": git_commit,
        "working_tree_dirty": (
            git_dirty
        ),
    },

    "environment": {
        "python_version": (
            platform.python_version()
        ),

        "numpy_version": (
            np.__version__
        ),

        "pandas_version": (
            pd.__version__
        ),

        "scikit_learn_version": (
            sklearn.__version__
        ),
    },

    "file_hashes": {
        str(
            PHASE31_CONTRACT_PATH
        ): sha256_file(
            PHASE31_CONTRACT_PATH
        ),

        str(
            LOCKED_SPEC_PATH
        ): sha256_file(
            LOCKED_SPEC_PATH
        ),

        str(
            PYPROJECT_PATH
        ): sha256_file(
            PYPROJECT_PATH
        ),

        str(
            CONSTRAINTS_PATH
        ): sha256_file(
            CONSTRAINTS_PATH
        ),
    },

    "current_challenger": {
        "model_family": (
            "ExtraTreesRegressor"
        ),

        "feature_count": 36,

        "training_objective": (
            "unweighted_rows"
        ),

        "recipe": (
            challenger_recipe
        ),

        "status": (
            "experimental_challenger"
        ),
    },

    "phase31_interpretation": {
        "tg1": (
            "The incumbent Random Forest "
            "outperformed default Extra Trees "
            "and default Histogram Gradient Boosting."
        ),

        "tg2": (
            "Bounded nested-CV tuning produced "
            "a credible Extra Trees challenger "
            "with modestly lower pooled OOF RMSE "
            "than the incumbent."
        ),

        "tg3": (
            "Engine-balanced weighting improved "
            "some supporting diagnostics but did "
            "not improve the declared primary "
            "pooled OOF RMSE, so the unweighted "
            "challenger recipe was retained."
        ),
    },

    "evidence_files": [
        str(
            TG1_SUMMARY_PATH
        ),

        str(
            TG2_SUMMARY_PATH
        ),

        str(
            TG3_SUMMARY_PATH
        ),

        str(
            ledger_path
        ),
    ],

    "scope_note": (
        "This manifest records Phase 3.1 "
        "experimental evidence. It does not "
        "represent model promotion."
    ),
}


manifest_path = (
    REPORTS_DIR
    / "phase_31_experiment_manifest.json"
)


with manifest_path.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        manifest,
        file,
        indent=2,
        sort_keys=True,
    )


print(
    "\nExperiment ledger:"
)

print(
    ledger.to_string(
        index=False
    )
)


print(
    "\nGit commit:",
    git_commit,
)

print(
    "Working tree dirty:",
    git_dirty,
)

print(
    "\nCreated:",
    ledger_path,
)

print(
    "Created:",
    manifest_path,
)