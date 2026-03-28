"""
Walker Delta–style constellation topology (uniform RAAN, consistent inter-plane phasing).

Notation: ``T`` satellites, ``P`` planes, ``S = T/P`` satellites per plane, phase ``F`` in ``[0, P-1]``.

References: Ballard, “Satellite Constellations”; Walker (1984).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class WalkerSlot:
    """One satellite slot in a Walker Delta pattern."""

    index: int
    plane_index: int
    slot_in_plane: int
    raan_rad: float
    mean_anomaly_at_epoch_rad: float


def validate_walker_delta(total_satellites_T: int, planes_P: int, phase_F: int) -> int:
    """
    Enforce divisibility ``T % P == 0`` and ``F ∈ [0, P-1]``.

    Returns ``S = T / P`` (satellites per plane).
    """
    if total_satellites_T < 1 or planes_P < 1:
        raise ValueError("T and P must be positive integers.")
    if total_satellites_T % planes_P != 0:
        raise ValueError("Walker Delta requires T divisible by P (integer satellites per plane).")
    s = total_satellites_T // planes_P
    if s < 1:
        raise ValueError("Invalid T/P ratio.")
    if phase_F < 0 or phase_F >= planes_P:
        raise ValueError("Walker phase F must satisfy 0 <= F < P.")
    return s


def walker_delta_slots(
    total_satellites_T: int,
    planes_P: int,
    phase_F: int,
) -> Tuple[WalkerSlot, ...]:
    """
    Build ``T`` slots with:

    - ``Ω_p = 2π p / P`` for plane ``p = 0 … P-1``
    - ``M_{p,k} = 2π k / S + F · 2π p / T`` with ``k = 0 … S-1``, ``S = T/P``
    """
    s = validate_walker_delta(total_satellites_T, planes_P, phase_F)
    slots: List[WalkerSlot] = []
    for idx in range(total_satellites_T):
        p = idx // s
        k = idx % s
        raan = (2.0 * math.pi / planes_P) * p
        m0 = (2.0 * math.pi / s) * k + (2.0 * math.pi / total_satellites_T) * phase_F * p
        m0 = math.atan2(math.sin(m0), math.cos(m0))
        slots.append(
            WalkerSlot(
                index=idx,
                plane_index=p,
                slot_in_plane=k,
                raan_rad=raan,
                mean_anomaly_at_epoch_rad=m0,
            )
        )
    return tuple(slots)
