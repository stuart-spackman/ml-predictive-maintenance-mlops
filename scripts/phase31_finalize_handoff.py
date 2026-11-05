from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


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

TG4_LEDGER_PATH = (
    REPORTS_DIR
    / "phase_31_experiment_ledger.csv"
)

TG4_MANIFEST_PATH = (
    REPORTS_DIR
    / "phase_31_experiment_manifest.json"
)

PHASE31_CONTRACT_PATH = (
    REPORTS_DIR
    / "phase_31_experiment_contract.json"
)

LOCKED_SPEC_PATH = (
    REPORTS_DIR
    / "phase_16_locked_model_spec.json"
)

INCUMBENT_MODEL_PATH = (
    REPORTS_DIR
    / "phase_16_final_fitted_model.joblib"
)

INCUMBENT_FIT_RECORD_PATH = (
    REPORTS_DIR
    / "phase_16_final_fit_record.json"
)


HANDOFF_JSON_PATH = (
    REPORTS_DIR
    / "phase_31_handoff.json"
)

HANDOFF_CSV_PATH = (
    REPORTS_DIR
    / "phase_31_handoff_model_comparison.csv"
)


# ------------------------------------------------------------
# 1. Verify Phase 3.1 evidence package
# ------------------------------------------------------------

required_files = [
    TG1_SUMMARY_PATH,
    TG2_SUMMARY_PATH,
    TG3_SUMMARY_PATH,
    TG3_RECIPE_PATH,
    TG4_LEDGER_PATH,
    TG4_MANIFEST_PATH,
    PHASE31_CONTRACT_PATH,
    LOCKED_SPEC_PATH,
    INCUMBENT_MODEL_PATH,
    INCUMBENT_FIT_RECORD_PATH,
]


for path in required_files:

    if not path.exists():
        raise FileNotFoundError(
            f"Missing required Phase 3.1 handoff file: "
            f"{path}"
        )


# ------------------------------------------------------------
# 2. Load the evidence
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


with TG3_RECIPE_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    challenger_recipe = json.load(
        file
    )


with LOCKED_SPEC_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    locked_spec = json.load(
        file
    )


# ------------------------------------------------------------
# 3. Extract incumbent reference evidence
# ------------------------------------------------------------

incumbent_rows = tg2.loc[
    tg2["model"].eq(
        "incumbent_random_forest"
    )
]


if len(
    incumbent_rows
) != 1:
    raise RuntimeError(
        "Expected exactly one incumbent row "
        "in TG2 summary."
    )


incumbent_row = (
    incumbent_rows.iloc[0]
)


incumbent_rmse = float(
    incumbent_row[
        "pooled_oof_rmse"
    ]
)

incumbent_mae = float(
    incumbent_row[
        "pooled_oof_mae"
    ]
)


# ------------------------------------------------------------
# 4. Extract fixed unweighted challenger evidence
# ------------------------------------------------------------

challenger_rows = tg3.loc[
    tg3[
        "training_objective"
    ].eq(
        "unweighted_rows"
    )
]


if len(
    challenger_rows
) != 1:
    raise RuntimeError(
        "Expected exactly one unweighted "
        "fixed-challenger row in TG3 summary."
    )


challenger_row = (
    challenger_rows.iloc[0]
)


challenger_rmse = float(
    challenger_row[
        "pooled_oof_rmse"
    ]
)

challenger_mae = float(
    challenger_row[
        "pooled_oof_mae"
    ]
)


# ------------------------------------------------------------
# 5. Validate challenger contract
# ------------------------------------------------------------

if (
    challenger_recipe[
        "model_family"
    ]
    != "ExtraTreesRegressor"
):
    raise RuntimeError(
        "Unexpected Phase 3.1 challenger family."
    )


if (
    challenger_recipe[
        "n_estimators"
    ]
    != 300
):
    raise RuntimeError(
        "Unexpected challenger n_estimators."
    )


if len(
    locked_spec[
        "feature_names"
    ]
) != 36:
    raise RuntimeError(
        "Expected locked 36-feature schema."
    )


expected_params = {
    "max_depth": 20,
    "max_features": "sqrt",
    "min_samples_leaf": 2,
    "min_samples_split": 5,
}


if (
    challenger_recipe[
        "hyperparameters"
    ]
    != expected_params
):
    raise RuntimeError(
        "Challenger recipe does not match "
        "the Phase 3.1 fixed recipe."
    )


# ------------------------------------------------------------
# 6. Calculate comparison
# ------------------------------------------------------------

rmse_delta = (
    challenger_rmse
    - incumbent_rmse
)


rmse_improvement_percent = (
    (
        incumbent_rmse
        - challenger_rmse
    )
    / incumbent_rmse
    * 100.0
)


challenger_beats_incumbent = (
    challenger_rmse
    < incumbent_rmse
)


# ------------------------------------------------------------
# 7. Produce simple model comparison table
# ------------------------------------------------------------

comparison = pd.DataFrame(
    [
        {
            "lifecycle_role": (
                "incumbent"
            ),

            "model_family": (
                "RandomForestRegressor"
            ),

            "training_objective": (
                "unweighted_rows"
            ),

            "feature_count": 36,

            "pooled_oof_rmse": (
                incumbent_rmse
            ),

            "pooled_oof_mae": (
                incumbent_mae
            ),

            "status": (
                "currently_served"
            ),
        },

        {
            "lifecycle_role": (
                "challenger"
            ),

            "model_family": (
                "ExtraTreesRegressor"
            ),

            "training_objective": (
                "unweighted_rows"
            ),

            "feature_count": 36,

            "pooled_oof_rmse": (
                challenger_rmse
            ),

            "pooled_oof_mae": (
                challenger_mae
            ),

            "status": (
                "advance_to_phase_32"
            ),
        },
    ]
)


comparison.to_csv(
    HANDOFF_CSV_PATH,
    index=False,
)


# ------------------------------------------------------------
# 8. Build Phase 3.1 handoff record
# ------------------------------------------------------------

handoff = {
    "phase": "3.1",

    "handoff_to": (
        "Phase 3.2 — Model Evaluation, "
        "Versioning, and Promotion"
    ),

    "incumbent": {
        "model_family": (
            "RandomForestRegressor"
        ),

        "fitted_artifact": str(
            INCUMBENT_MODEL_PATH
        ),

        "fit_record": str(
            INCUMBENT_FIT_RECORD_PATH
        ),

        "feature_count": 36,

        "reference_pooled_oof_rmse": (
            incumbent_rmse
        ),

        "reference_pooled_oof_mae": (
            incumbent_mae
        ),

        "status": (
            "currently_served"
        ),
    },

    "challenger": {
        "model_family": (
            "ExtraTreesRegressor"
        ),

        "recipe": (
            challenger_recipe
        ),

        "feature_count": 36,

        "feature_contract": str(
            LOCKED_SPEC_PATH
        ),

        "training_objective": (
            "unweighted_rows"
        ),

        "reference_pooled_oof_rmse": (
            challenger_rmse
        ),

        "reference_pooled_oof_mae": (
            challenger_mae
        ),

        "status": (
            "experimental_challenger"
        ),
    },

    "comparison": {
        "challenger_minus_incumbent_rmse": (
            rmse_delta
        ),

        "challenger_rmse_improvement_percent": (
            rmse_improvement_percent
        ),

        "challenger_lower_rmse": (
            challenger_beats_incumbent
        ),
    },

    "phase31_conclusions": [
        (
            "Default challenger families did not "
            "beat the incumbent during TG1 screening."
        ),
        (
            "Bounded nested grouped-CV tuning made "
            "Extra Trees a credible challenger."
        ),
        (
            "The fixed Extra Trees recipe retained "
            "nearly all of the tuned procedure's "
            "performance."
        ),
        (
            "Engine-balanced weighting did not improve "
            "the declared primary pooled OOF RMSE and "
            "was therefore rejected."
        ),
        (
            "The unweighted fixed Extra Trees recipe "
            "advances to Phase 3.2 for formal "
            "promotion evaluation."
        ),
    ],

    "important_limitations": [
        (
            "Phase 3.1 development evidence has "
            "participated in challenger selection."
        ),
        (
            "The official test set must not be used "
            "for additional challenger tuning."
        ),
        (
            "A modest RMSE advantage does not by itself "
            "authorize production promotion."
        ),
        (
            "No challenger fitted artifact has replaced "
            "the incumbent artifact."
        ),
    ],

    "evidence": {
        "experiment_contract": str(
            PHASE31_CONTRACT_PATH
        ),

        "tg1_summary": str(
            TG1_SUMMARY_PATH
        ),

        "tg2_summary": str(
            TG2_SUMMARY_PATH
        ),

        "tg3_summary": str(
            TG3_SUMMARY_PATH
        ),

        "experiment_ledger": str(
            TG4_LEDGER_PATH
        ),

        "experiment_manifest": str(
            TG4_MANIFEST_PATH
        ),

        "model_comparison": str(
            HANDOFF_CSV_PATH
        ),
    },

    "phase31_decision": (
        "Advance the fixed unweighted Extra Trees "
        "challenger to Phase 3.2. Do not promote "
        "or alter serving during Phase 3.1."
    ),
}


with HANDOFF_JSON_PATH.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        handoff,
        file,
        indent=2,
        sort_keys=True,
    )


# ------------------------------------------------------------
# 9. Human-readable closeout
# ------------------------------------------------------------

print(
    "\nPhase 3.1 model comparison:"
)

print(
    comparison.to_string(
        index=False
    )
)


print(
    "\nRMSE delta "
    "(challenger - incumbent):",
    round(
        rmse_delta,
        6,
    ),
)


print(
    "Relative RMSE improvement:",
    f"{rmse_improvement_percent:.3f}%",
)


print(
    "\nPhase 3.1 decision:"
)

print(
    handoff[
        "phase31_decision"
    ]
)


print(
    "\nCreated:",
    HANDOFF_JSON_PATH,
)

print(
    "Created:",
    HANDOFF_CSV_PATH,
)