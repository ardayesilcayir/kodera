"""Walker Delta divisibility and slot count."""

from __future__ import annotations

import math

import pytest

from walker_service import validate_walker_delta, walker_delta_slots


def test_t_must_divide_p() -> None:
    with pytest.raises(ValueError, match="divisible"):
        validate_walker_delta(5, 2, 0)


def test_f_must_be_lt_p() -> None:
    with pytest.raises(ValueError, match="F"):
        validate_walker_delta(6, 3, 3)


def test_walker_slot_count_and_raan_spacing() -> None:
    slots = walker_delta_slots(6, 3, 1)
    assert len(slots) == 6
    raans = sorted({round(s.raan_rad, 9) for s in slots})
    assert len(raans) == 3
    assert raans[1] - raans[0] == pytest.approx(2.0 * math.pi / 3.0)


def test_validate_returns_satellites_per_plane() -> None:
    assert validate_walker_delta(12, 4, 2) == 3
