from __future__ import annotations

from collections.abc import (
    Iterable,
)

import numpy as np


def _as_finite_array(
    values: Iterable[float],
) -> np.ndarray:

    array = np.asarray(
        list(values),
        dtype=float,
    )


    if array.size == 0:

        raise ValueError(
            "Drift input cannot be empty."
        )


    if not np.isfinite(
        array
    ).all():

        raise ValueError(
            "Drift input must contain "
            "only finite values."
        )


    return array


def build_reference_cutpoints(
    reference_values: Iterable[float],
    *,
    target_bin_count: int = 10,
) -> list[float]:
    """
    Build deterministic finite quantile cutpoints
    from the reference population only.

    The returned values are internal cutpoints.
    PSI later adds -inf and +inf around them.
    """

    reference = (
        _as_finite_array(
            reference_values
        )
    )


    if (
        target_bin_count
        < 2
    ):

        raise ValueError(
            "target_bin_count must be >= 2."
        )


    unique_values = (
        np.unique(
            reference
        )
    )


    if (
        unique_values.size
        < 2
    ):

        raise ValueError(
            "Reference distribution must "
            "contain at least two unique values."
        )


    quantiles = np.linspace(
        0.0,
        1.0,
        target_bin_count + 1,
    )[1:-1]


    cutpoints = np.unique(
        np.quantile(
            reference,
            quantiles,
        )
    )


    reference_min = float(
        reference.min()
    )

    reference_max = float(
        reference.max()
    )


    cutpoints = cutpoints[
        (
            cutpoints
            > reference_min
        )
        &
        (
            cutpoints
            < reference_max
        )
    ]


    # Extremely discrete distributions can collapse
    # all quantile cutpoints. Preserve at least two bins.
    if (
        cutpoints.size
        == 0
    ):

        cutpoints = np.array(
            [
                (
                    reference_min
                    + reference_max
                )
                / 2.0
            ]
        )


    return [
        float(value)
        for value in cutpoints
    ]


def population_stability_index(
    reference_values: Iterable[float],
    current_values: Iterable[float],
    *,
    cutpoints: Iterable[float],
    epsilon: float = 1e-6,
) -> float:
    """
    Compare current distribution with a frozen
    reference-bin definition using PSI.
    """

    reference = (
        _as_finite_array(
            reference_values
        )
    )


    current = (
        _as_finite_array(
            current_values
        )
    )


    if (
        epsilon
        <= 0.0
    ):

        raise ValueError(
            "epsilon must be positive."
        )


    internal_cutpoints = np.asarray(
        list(
            cutpoints
        ),
        dtype=float,
    )


    if (
        internal_cutpoints.size
        > 0
        and not np.isfinite(
            internal_cutpoints
        ).all()
    ):

        raise ValueError(
            "PSI cutpoints must be finite."
        )


    internal_cutpoints = np.unique(
        internal_cutpoints
    )


    edges = np.concatenate(
        [
            np.array(
                [-np.inf]
            ),

            internal_cutpoints,

            np.array(
                [np.inf]
            ),
        ]
    )


    reference_counts, _ = (
        np.histogram(
            reference,
            bins=edges,
        )
    )


    current_counts, _ = (
        np.histogram(
            current,
            bins=edges,
        )
    )


    reference_proportions = (
        reference_counts
        / reference_counts.sum()
    )


    current_proportions = (
        current_counts
        / current_counts.sum()
    )


    reference_proportions = np.clip(
        reference_proportions,
        epsilon,
        None,
    )


    current_proportions = np.clip(
        current_proportions,
        epsilon,
        None,
    )


    # Re-normalize after epsilon smoothing.
    reference_proportions = (
        reference_proportions
        / reference_proportions.sum()
    )


    current_proportions = (
        current_proportions
        / current_proportions.sum()
    )


    psi = np.sum(
        (
            current_proportions
            - reference_proportions
        )
        *
        np.log(
            current_proportions
            / reference_proportions
        )
    )


    return float(
        psi
    )


def classify_psi(
    psi: float,
    *,
    warning_threshold: float = 0.10,
    alert_threshold: float = 0.25,
) -> str:

    if not np.isfinite(
        psi
    ):

        raise ValueError(
            "PSI must be finite."
        )


    if not (
        0.0
        <= warning_threshold
        < alert_threshold
    ):

        raise ValueError(
            "Thresholds must satisfy "
            "0 <= warning < alert."
        )


    if (
        psi
        >= alert_threshold
    ):

        return "alert"


    if (
        psi
        >= warning_threshold
    ):

        return "warning"


    return "stable"