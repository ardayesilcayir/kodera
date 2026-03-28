"""Tests for WGS84 LLH ↔ ECEF and geodetic normal."""

from __future__ import annotations

import numpy as np
import pytest

from geo_utils import (
    WGS84_A,
    WGS84_B,
    ecef_position_to_geodetic_up,
    ecef_to_llh,
    geodetic_up_unit_ecef,
    llh_to_ecef,
)


@pytest.mark.parametrize(
    "lat,lon,h",
    [
        (0.0, 0.0, 0.0),
        (40.7128, -74.0060, 10.0),
        (-33.8688, 151.2093, 50.0),
        (89.0, 45.0, 2.0),
    ],
)
def test_llh_ecef_roundtrip(lat: float, lon: float, h: float) -> None:
    x, y, z = llh_to_ecef(lat, lon, h)
    lat2, lon2, h2 = ecef_to_llh(float(x), float(y), float(z))
    assert lat2 == pytest.approx(lat, abs=1e-9)
    assert lon2 == pytest.approx(lon, abs=1e-9)
    assert h2 == pytest.approx(h, abs=1e-6)


def test_equator_surface_on_x_axis() -> None:
    """At (lat=0, lon=0, h=0) surface point lies on +X with magnitude ~a."""
    x, y, z = llh_to_ecef(0.0, 0.0, 0.0)
    assert y == pytest.approx(0.0, abs=1e-6)
    assert z == pytest.approx(0.0, abs=1e-6)
    assert x > 0.0
    assert x == pytest.approx(WGS84_A, rel=1e-9)


def test_geodetic_up_unit_length() -> None:
    u = geodetic_up_unit_ecef(12.5, -3.0)
    assert float(np.linalg.norm(u)) == pytest.approx(1.0, abs=1e-12)


def test_geodetic_up_matches_gradient() -> None:
    """Normal from analytic ellipsoid gradient vs geodetic formula."""
    x, y, z = llh_to_ecef(30.0, 45.0, 0.0)
    g = np.array(
        [2.0 * x / (WGS84_A**2), 2.0 * y / (WGS84_A**2), 2.0 * z / (WGS84_B**2)],
        dtype=np.float64,
    )
    g = g / np.linalg.norm(g)
    u = ecef_position_to_geodetic_up(float(x), float(y), float(z))
    # Ellipsoid gradient vs geodetic normal: parallel within numerical noise.
    assert np.dot(g, u) == pytest.approx(1.0, abs=1e-4)


def test_pole_latitude() -> None:
    x, y, z = llh_to_ecef(90.0, 0.0, 0.0)
    lat, lon, h = ecef_to_llh(float(x), float(y), float(z))
    assert lat == pytest.approx(90.0, abs=1e-6)
    assert h == pytest.approx(0.0, abs=0.5)
