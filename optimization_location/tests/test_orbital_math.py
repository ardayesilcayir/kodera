"""Orbital mechanics: mean motion and sun-synchronous inclination."""

from __future__ import annotations

import math

import pytest

from orbital_math import (
    MU_EARTH_M3_S2,
    R_EARTH_EQUATORIAL_M,
    mean_motion_rad_s,
    orbital_period_s,
    semi_major_axis_m_from_altitude_km,
    sun_synchronous_inclination_rad,
)


def test_mean_motion_matches_two_body() -> None:
    a_m = semi_major_axis_m_from_altitude_km(400.0)
    n = mean_motion_rad_s(a_m)
    expected = math.sqrt(MU_EARTH_M3_S2 / a_m**3)
    assert n == pytest.approx(expected, rel=1e-12)


def test_mean_motion_period_consistency() -> None:
    a_m = semi_major_axis_m_from_altitude_km(800.0)
    n = mean_motion_rad_s(a_m)
    t = orbital_period_s(a_m)
    assert t == pytest.approx(2.0 * math.pi / n, rel=1e-12)


def test_sun_sync_inclination_is_retrograde_leo() -> None:
    a_m = semi_major_axis_m_from_altitude_km(700.0)
    i_rad = sun_synchronous_inclination_rad(a_m, 0.0)
    assert i_rad > math.radians(90.0)
    assert i_rad < math.radians(102.0)
