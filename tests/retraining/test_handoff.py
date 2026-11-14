from predictive_maintenance.retraining.handoff import (
    build_retraining_handoff,
)


MODEL_SHA = "model-abc"
SPEC_SHA = "spec-abc"


def test_noneligible_decision_blocks_retraining():

    result = (
        build_retraining_handoff(
            performance_decision={
                "status": (
                    "investigate_before_retraining"
                )
            },

            incumbent_model_sha256=(
                MODEL_SHA
            ),

            incumbent_spec_sha256=(
                SPEC_SHA
            ),

            real_new_labeled_data_available=(
                True
            ),
        )
    )


    assert (
        result[
            "status"
        ]
        == "retraining_not_authorized"
    )


    assert (
        result[
            "challenger_fit_authorized"
        ]
        is False
    )


def test_missing_real_production_data_blocks_real_fit():

    result = (
        build_retraining_handoff(
            performance_decision={
                "status": (
                    "eligible_to_retrain"
                )
            },

            incumbent_model_sha256=(
                MODEL_SHA
            ),

            incumbent_spec_sha256=(
                SPEC_SHA
            ),

            real_new_labeled_data_available=(
                False
            ),
        )
    )


    assert (
        result[
            "status"
        ]
        ==
        "workflow_validated_but_real_fit_blocked"
    )


    assert (
        result[
            "incumbent_preserved"
        ]
        is True
    )


    assert (
        result[
            "registry_action"
        ]
        == "none"
    )


    assert (
        result[
            "deployment_action"
        ]
        == "none"
    )


def test_real_labeled_data_can_authorize_challenger_fit():

    result = (
        build_retraining_handoff(
            performance_decision={
                "status": (
                    "eligible_to_retrain"
                )
            },

            incumbent_model_sha256=(
                MODEL_SHA
            ),

            incumbent_spec_sha256=(
                SPEC_SHA
            ),

            real_new_labeled_data_available=(
                True
            ),
        )
    )


    assert (
        result[
            "status"
        ]
        == "authorized_to_fit_challenger"
    )


    assert (
        result[
            "challenger_fit_authorized"
        ]
        is True
    )


    assert (
        result[
            "incumbent_preserved"
        ]
        is True
    )


    assert (
        result[
            "registry_action"
        ]
        == "none"
    )


    assert (
        result[
            "deployment_action"
        ]
        == "none"
    )