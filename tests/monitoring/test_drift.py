import numpy as np
import pytest

from predictive_maintenance.monitoring.drift import (
    build_reference_cutpoints,
    classify_psi,
    population_stability_index,
)


def test_identical_distribution_has_zero_psi():

    reference = np.arange(
        1,
        101,
        dtype=float,
    )


    cutpoints = (
        build_reference_cutpoints(
            reference
        )
    )


    psi = (
        population_stability_index(
            reference,
            reference.copy(),
            cutpoints=cutpoints,
        )
    )


    assert psi == pytest.approx(
        0.0,
        abs=1e-12,
    )


def test_shifted_distribution_has_positive_psi():

    reference = np.arange(
        1,
        101,
        dtype=float,
    )


    current = (
        reference
        + 40.0
    )


    cutpoints = (
        build_reference_cutpoints(
            reference
        )
    )


    psi = (
        population_stability_index(
            reference,
            current,
            cutpoints=cutpoints,
        )
    )


    assert psi > 0.0


def test_reference_cutpoints_are_sorted():

    reference = np.arange(
        1,
        101,
        dtype=float,
    )


    cutpoints = (
        build_reference_cutpoints(
            reference
        )
    )


    assert cutpoints == sorted(
        cutpoints
    )


def test_psi_rejects_nonfinite_values():

    reference = [
        1.0,
        2.0,
        3.0,
    ]


    current = [
        1.0,
        np.nan,
        3.0,
    ]


    cutpoints = [
        1.5,
        2.5,
    ]


    with pytest.raises(
        ValueError,
        match="finite",
    ):

        population_stability_index(
            reference,
            current,
            cutpoints=cutpoints,
        )


@pytest.mark.parametrize(
    (
        "psi",
        "expected",
    ),
    [
        (
            0.05,
            "stable",
        ),
        (
            0.10,
            "warning",
        ),
        (
            0.249,
            "warning",
        ),
        (
            0.25,
            "alert",
        ),
    ],
)
def test_classify_psi(
    psi,
    expected,
):

    assert (
        classify_psi(
            psi
        )
        == expected
    )