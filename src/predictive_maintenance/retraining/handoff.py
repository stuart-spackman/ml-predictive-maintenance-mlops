from __future__ import annotations

from collections.abc import Mapping


def build_retraining_handoff(
    *,
    performance_decision: Mapping,
    incumbent_model_sha256: str,
    incumbent_spec_sha256: str,
    real_new_labeled_data_available: bool,
) -> dict:
    """
    Convert a retraining-eligibility decision into a safe
    challenger-development handoff.

    This function does not train, promote, register, or deploy
    a model.
    """

    decision_status = (
        performance_decision.get(
            "status"
        )
    )


    if (
        decision_status
        != "eligible_to_retrain"
    ):

        return {
            "status": (
                "retraining_not_authorized"
            ),

            "challenger_fit_authorized": (
                False
            ),

            "incumbent_preserved": (
                True
            ),
        }


    if not real_new_labeled_data_available:

        return {
            "status": (
                "workflow_validated_but_real_fit_blocked"
            ),

            "reason": (
                "No genuine newly labeled production "
                "data is available in this portfolio "
                "environment."
            ),

            "challenger_fit_authorized": (
                False
            ),

            "incumbent_preserved": (
                True
            ),

            "incumbent_identity": {
                "model_artifact_sha256": (
                    incumbent_model_sha256
                ),

                "locked_spec_sha256": (
                    incumbent_spec_sha256
                ),
            },

            "registry_action": (
                "none"
            ),

            "deployment_action": (
                "none"
            ),
        }


    return {
        "status": (
            "authorized_to_fit_challenger"
        ),

        "challenger_fit_authorized": (
            True
        ),

        "incumbent_preserved": (
            True
        ),

        "incumbent_identity": {
            "model_artifact_sha256": (
                incumbent_model_sha256
            ),

            "locked_spec_sha256": (
                incumbent_spec_sha256
            ),
        },

        "next_required_stage": (
            "fit_new_challenger_then_run_evaluation_and_promotion_gates"
        ),

        "registry_action": (
            "none"
        ),

        "deployment_action": (
            "none"
        ),
    }