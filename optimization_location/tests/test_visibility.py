"""Elevation-angle visibility tests."""

from __future__ import annotations

import numpy as np
import pytest

from geo_utils import ecef_position_to_geodetic_up, llh_to_ecef
from visibility_service import (
    effective_nadir_limit_deg,
    elevation_angle_deg,
    is_link_accessible,
    is_visible,
    nadir_angle_deg,
)


def test_zenith_is_ninety_deg() -> None:
    g = llh_to_ecef(0.0, 0.0, 0.0)
    u = ecef_position_to_geodetic_up(float(g[0]), float(g[1]), float(g[2]))
    s = g + 7.0e6 * u
    assert elevation_angle_deg(s, g) == pytest.approx(90.0, abs=1e-6)


def test_horizontal_is_zero_deg() -> None:
    g = llh_to_ecef(0.0, 0.0, 0.0)
    u = ecef_position_to_geodetic_up(float(g[0]), float(g[1]), float(g[2]))
    w = np.array([0.0, 0.0, 1.0])
    v = np.cross(u, w)
    if float(np.linalg.norm(v)) < 1e-9:
        v = np.cross(u, np.array([0.0, 1.0, 0.0]))
    v = v / np.linalg.norm(v)
    s = g + 5.0e6 * v
    assert elevation_angle_deg(s, g) == pytest.approx(0.0, abs=1e-5)


def test_below_horizon_negative_elevation() -> None:
    g = llh_to_ecef(10.0, 20.0, 0.0)
    u = ecef_position_to_geodetic_up(float(g[0]), float(g[1]), float(g[2]))
    s = g - 5.0e6 * u
    el = elevation_angle_deg(s, g)
    assert el < -1.0


def test_is_visible_respects_threshold() -> None:
    g = llh_to_ecef(0.0, 0.0, 0.0)
    u = ecef_position_to_geodetic_up(float(g[0]), float(g[1]), float(g[2]))
    s = g + 1.0e7 * u
    assert is_visible(s, g, 5.0) is True
    assert is_visible(s, g, 91.0) is False


def test_nadir_angle_zero_near_zenith() -> None:
    g = llh_to_ecef(0.0, 0.0, 0.0)
    u = ecef_position_to_geodetic_up(float(g[0]), float(g[1]), float(g[2]))
    s = g + 7.0e6 * u
    assert nadir_angle_deg(s, g) == pytest.approx(0.0, abs=1e-4)


def test_effective_nadir_limit_when_max_off_zero_uses_sensor_only() -> None:
    assert effective_nadir_limit_deg(60.0, 0.0) == 60.0
    assert effective_nadir_limit_deg(60.0, 30.0) == 30.0


def test_wide_cone_matches_visibility_mask() -> None:
    """With a 90° nadir cap, geometry is limited by elevation only."""
    g = llh_to_ecef(0.0, 0.0, 0.0)
    u = ecef_position_to_geodetic_up(float(g[0]), float(g[1]), float(g[2]))
    s = g + 1.0e7 * u
    assert is_link_accessible(s, g, min_elevation_deg=5.0, max_nadir_angle_deg=90.0) == is_visible(
        s, g, 5.0
    )


def test_coincident_raises() -> None:
    g = llh_to_ecef(1.0, 2.0, 0.0)
    with pytest.raises(ValueError):
        elevation_angle_deg(g, g)
