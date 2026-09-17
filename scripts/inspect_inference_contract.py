# Phase 2.1 — Task Group 0
# Inspect the inference contract from the command line.

from dataclasses import asdict

from predictive_maintenance.inference.contract import (
    PHASE_21_INFERENCE_CONTRACT,
)


def main() -> None:
    """Print the active Phase 2.1 inference contract."""

    contract_dict = asdict(
        PHASE_21_INFERENCE_CONTRACT
    )

    print("PHASE 2.1 INFERENCE CONTRACT")
    print("=" * 40)

    for key, value in contract_dict.items():
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()