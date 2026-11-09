from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from predictive_maintenance.config import (
    DATASET_NAME,
)

from predictive_maintenance.data.cmapss import (
    load_cmapss_subset,
)

from predictive_maintenance.features.feature_sets import (
    GROUP_COLUMN,
)

from predictive_maintenance.inference.contract import (
    PHASE_21_INFERENCE_CONTRACT,
)

from predictive_maintenance.inference.pipeline import (
    create_default_inference_pipeline,
)

from predictive_maintenance.inference.schema import (
    CYCLE_COLUMN,
    REQUIRED_RAW_HISTORY_COLUMNS,
)

from predictive_maintenance.monitoring.drift import (
    build_reference_cutpoints,
    population_stability_index,
)

from predictive_maintenance.monitoring.telemetry import (
    build_served_model_identity,
)


REPORTS_DIR = Path(
    "reports"
)


POLICY_PATH = (
    REPORTS_DIR
    / "phase_33_drift_policy.json"
)


REFERENCE_EVENTS_PATH = (
    REPORTS_DIR
    / "phase_33_reference_prediction_events.csv"
)


REFERENCE_BINS_PATH = (
    REPORTS_DIR
    / "phase_33_reference_bins.json"
)


REFERENCE_SUMMARY_PATH = (
    REPORTS_DIR
    / "phase_33_reference_baseline_summary.json"
)


LOCKED_SPEC_PATH = (
    REPORTS_DIR
    / "phase_16_locked_model_spec.json"
)


# ------------------------------------------------------------
# 1. Load monitoring policy
# ------------------------------------------------------------

if not POLICY_PATH.exists():

    raise FileNotFoundError(
        f"Missing drift policy: {POLICY_PATH}"
    )


with POLICY_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    policy = json.load(
        file
    )


target_bin_count = int(
    policy[
        "metric"
    ][
        "target_bin_count"
    ]
)


checkpoint_step = int(
    policy[
        "reference_sampling"
    ][
        "checkpoint_step_cycles"
    ]
)


# ------------------------------------------------------------
# 2. Load locked feature contract
# ------------------------------------------------------------

with LOCKED_SPEC_PATH.open(
    "r",
    encoding="utf-8",
) as file:

    locked_spec = json.load(
        file
    )


locked_features = list(
    locked_spec[
        "feature_names"
    ]
)


if len(
    locked_features
) != 36:

    raise RuntimeError(
        "Expected exactly 36 locked features."
    )


# ------------------------------------------------------------
# 3. Load the exact serving pipeline
# ------------------------------------------------------------

pipeline = (
    create_default_inference_pipeline()
)


served_model_identity = (
    build_served_model_identity()
)


# ------------------------------------------------------------
# 4. Load historical FD001 training engines
# ------------------------------------------------------------

train_df, _, _ = (
    load_cmapss_subset(
        DATASET_NAME
    )
)


minimum_cycles = int(
    PHASE_21_INFERENCE_CONTRACT
    .minimum_history_cycles
)


reference_rows = []


engine_ids = sorted(
    train_df[
        GROUP_COLUMN
    ]
    .unique()
)


# ------------------------------------------------------------
# 5. Simulate production-style prediction events
# ------------------------------------------------------------

for engine_index, engine_id in enumerate(
    engine_ids,
    start=1,
):

    engine_history = (
        train_df
        .loc[
            train_df[
                GROUP_COLUMN
            ]
            == engine_id,
            list(
                REQUIRED_RAW_HISTORY_COLUMNS
            ),
        ]
        .sort_values(
            CYCLE_COLUMN
        )
        .reset_index(
            drop=True
        )
    )


    max_cycle = int(
        engine_history[
            CYCLE_COLUMN
        ]
        .max()
    )


    if (
        max_cycle
        < minimum_cycles
    ):

        continue


    checkpoints = list(
        range(
            minimum_cycles,
            max_cycle + 1,
            checkpoint_step,
        )
    )


    if (
        checkpoints[-1]
        != max_cycle
    ):

        checkpoints.append(
            max_cycle
        )


    for current_cycle in checkpoints:

        history_prefix = (
            engine_history
            .loc[
                engine_history[
                    CYCLE_COLUMN
                ]
                <= current_cycle
            ]
            .copy()
        )


        result = (
            pipeline.predict(
                history_prefix
            )
        )


        model_input = (
            pipeline.build_model_input(
                history_prefix
            )
        )


        if (
            model_input.shape
            != (1, 36)
        ):

            raise RuntimeError(
                "Unexpected reference model-input "
                f"shape: {model_input.shape}"
            )


        if (
            list(
                model_input.columns
            )
            != locked_features
        ):

            raise RuntimeError(
                "Reference event feature order "
                "does not match locked schema."
            )


        row = {
            "reference_event_id": (
                f"engine-{int(engine_id)}"
                f"-cycle-{int(current_cycle)}"
            ),

            "engine_id": int(
                result.engine_id
            ),

            "current_cycle": int(
                result.current_cycle
            ),

            "predicted_rul": float(
                result.predicted_rul
            ),
        }


        row.update(
            {
                feature_name: float(
                    model_input.iloc[0][
                        feature_name
                    ]
                )

                for feature_name
                in locked_features
            }
        )


        reference_rows.append(
            row
        )


    if (
        engine_index
        % 10
        == 0
    ):

        print(
            "Processed engines:",
            engine_index,
            "/",
            len(
                engine_ids
            ),
        )


# ------------------------------------------------------------
# 6. Save reference event population
# ------------------------------------------------------------

reference_df = pd.DataFrame(
    reference_rows
)


if reference_df.empty:

    raise RuntimeError(
        "Reference population is empty."
    )


if (
    reference_df[
        "engine_id"
    ]
    .nunique()
    != len(
        engine_ids
    )
):

    raise RuntimeError(
        "Reference population does not "
        "contain all expected engines."
    )


REFERENCE_EVENTS_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


reference_df.to_csv(
    REFERENCE_EVENTS_PATH,
    index=False,
)


# ------------------------------------------------------------
# 7. Freeze reference PSI bins
# ------------------------------------------------------------

monitored_columns = (
    locked_features
    + [
        "predicted_rul"
    ]
)


reference_bins = {}


for column in monitored_columns:

    reference_bins[
        column
    ] = (
        build_reference_cutpoints(
            reference_df[
                column
            ],
            target_bin_count=(
                target_bin_count
            ),
        )
    )


with REFERENCE_BINS_PATH.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        {
            "target_bin_count": (
                target_bin_count
            ),

            "reference_only": True,

            "columns": (
                reference_bins
            ),
        },
        file,
        indent=2,
        sort_keys=True,
    )


# ------------------------------------------------------------
# 8. Self-comparison smoke test
# ------------------------------------------------------------

self_psi = {}


for column in monitored_columns:

    value = (
        population_stability_index(
            reference_df[
                column
            ],

            reference_df[
                column
            ],

            cutpoints=(
                reference_bins[
                    column
                ]
            ),
        )
    )


    self_psi[
        column
    ] = float(
        value
    )


max_self_psi = max(
    self_psi.values()
)


if (
    max_self_psi
    > 1e-12
):

    raise RuntimeError(
        "Reference self-comparison "
        "should have PSI approximately zero."
    )


# ------------------------------------------------------------
# 9. Save baseline summary
# ------------------------------------------------------------

summary = {
    "phase": "3.3",
    "task_group": "TG2",

    "reference_population": {
        "event_count": int(
            len(
                reference_df
            )
        ),

        "engine_count": int(
            reference_df[
                "engine_id"
            ]
            .nunique()
        ),

        "minimum_cycle": int(
            reference_df[
                "current_cycle"
            ]
            .min()
        ),

        "maximum_cycle": int(
            reference_df[
                "current_cycle"
            ]
            .max()
        ),

        "checkpoint_step_cycles": (
            checkpoint_step
        ),
    },

    "feature_contract": {
        "feature_count": (
            len(
                locked_features
            )
        ),

        "feature_names": (
            locked_features
        ),
    },

    "served_model": (
        served_model_identity
    ),

    "drift_metric": {
        "name": (
            "population_stability_index"
        ),

        "target_bin_count": (
            target_bin_count
        ),

        "reference_bins_frozen": (
            True
        ),

        "maximum_reference_self_psi": (
            max_self_psi
        ),
    },

    "artifacts": {
        "reference_events": (
            str(
                REFERENCE_EVENTS_PATH
            )
        ),

        "reference_bins": (
            str(
                REFERENCE_BINS_PATH
            )
        ),

        "drift_policy": (
            str(
                POLICY_PATH
            )
        ),
    },
}


with REFERENCE_SUMMARY_PATH.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        summary,
        file,
        indent=2,
        sort_keys=True,
    )


print(
    "\nPhase 3.3 TG2 complete."
)


print(
    "Reference events:",
    len(
        reference_df
    )
)


print(
    "Reference engines:",
    reference_df[
        "engine_id"
    ]
    .nunique()
)


print(
    "Monitored distributions:",
    len(
        monitored_columns
    )
)


print(
    "Maximum self PSI:",
    max_self_psi
)


print(
    "\nCreated:",
    REFERENCE_EVENTS_PATH
)


print(
    "Created:",
    REFERENCE_BINS_PATH
)


print(
    "Created:",
    REFERENCE_SUMMARY_PATH
)