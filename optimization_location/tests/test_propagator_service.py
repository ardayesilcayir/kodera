"""ECI → ECEF propagation smoke test."""

from __future__ import annotations

import math

import numpy as np
import pytest

from candidate_models import SatelliteKeplerianECI
from orbital_math import semi_major_axis_m_from_altitude_km
from propagator_service import propagate_keplerian_ecef_m, propagate_keplerian_eci_m


def test_circular_leo_radius_near_sma() -> None:
    a_m = semi_major_axis_m_from_altitude_km(400.0)
    el = SatelliteKeplerianECI(
        semi_major_axis_m=a_m,
        eccentricity=0.0,
        inclination_rad=math.radians(51.6),
        raan_rad=0.0,
        arg_of_perigee_rad=0.0,
        mean_anomaly_at_epoch_rad=0.0,
    )
    r_eci = propagate_keplerian_eci_m(el, epoch_seconds=0.0, time_seconds_since_epoch=0.0)
    assert float(np.linalg.norm(r_eci)) == pytest.approx(a_m, rel=1e-6)


def test_j2_secular_differs_from_two_body_over_one_day() -> None:
    """J2 mean-element propagation should diverge from pure two-body over 24 h."""
    a_m = semi_major_axis_m_from_altitude_km(400.0)
    el = SatelliteKeplerianECI(
        semi_major_axis_m=a_m,
        eccentricity=0.0,
        inclination_rad=math.radians(51.6),
        raan_rad=0.0,
        arg_of_perigee_rad=0.0,
        mean_anomaly_at_epoch_rad=0.0,
    )
    r_tb = propagate_keplerian_ecef_m(
        el, 0.0, 86400.0, propagation_model="two_body_kepler", earth_rotation_model="vallado_gmst"
    )
    r_j2 = propagate_keplerian_ecef_m(
        el, 0.0, 86400.0, propagation_model="j2_mean_secular", earth_rotation_model="vallado_gmst"
    )
    assert float(np.linalg.norm(r_tb - r_j2)) > 5_000.0


def test_ecef_differs_from_eci_after_time() -> None:
    a_m = semi_major_axis_m_from_altitude_km(400.0)
    el = SatelliteKeplerianECI(
        semi_major_axis_m=a_m,
        eccentricity=0.0,
        inclination_rad=math.radians(51.6),
        raan_rad=0.0,
        arg_of_perigee_rad=0.0,
        mean_anomaly_at_epoch_rad=0.0,
    )
    r0 = propagate_keplerian_ecef_m(el, 0.0, 0.0)
    r1 = propagate_keplerian_ecef_m(el, 0.0, 3600.0)
    assert float(np.linalg.norm(r0)) == pytest.approx(float(np.linalg.norm(r1)), rel=1e-5)
    assert float(np.linalg.norm(r0 - r1)) > 1e3
