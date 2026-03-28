"""
Two-body Kepler propagation in ECI, then rotation to ECEF for visibility / ground geometry.

Supports pure two-body Kepler, or **J2 mean-element secular rates** on ``Ω``, ``ω``, and
``M`` (first-order). Earth rotation uses either simplified spin or a Vallado-style GMST.
"""

from __future__ import annotations

from typing import Literal, Tuple

import numpy as np
from numpy.typing import NDArray

from orbital_math import (
    eccentric_anomaly_eccentric_rad,
    eci_to_ecef_m,
    gmst_rad_simplified,
    gmst_rad_vallado,
    j2_secular_element_rates_rad_s,
    mean_anomaly_at_time_rad,
    mean_motion_rad_s,
    r_eci_position_m,
    true_anomaly_rad_from_eccentric,
)
from candidate_models import SatelliteKeplerianECI

PropagationModel = Literal["two_body_kepler", "j2_mean_secular"]
EarthRotationModel = Literal["simple_spin", "vallado_gmst"]


def propagate_keplerian_eci_m(
    el: SatelliteKeplerianECI,
    epoch_seconds: float,
    time_seconds_since_epoch: float,
    *,
    propagation_model: PropagationModel = "two_body_kepler",
) -> NDArray[np.float64]:
    """
    Position in ECI [m] at ``epoch + time_seconds_since_epoch``.

    ``two_body_kepler``: Kepler two-body with fixed ``Ω``, ``ω``, ``M0 + n dt``.
    ``j2_mean_secular``: first-order J2 secular drift on ``Ω``, ``ω``, and mean anomaly rate.
    """
    dt = time_seconds_since_epoch
    e = el.eccentricity
    a = el.semi_major_axis_m
    i = el.inclination_rad

    if propagation_model == "two_body_kepler":
        n = mean_motion_rad_s(a)
        m = mean_anomaly_at_time_rad(
            el.mean_anomaly_at_epoch_rad,
            n,
            dt,
        )
        raan = el.raan_rad
        argp = el.arg_of_perigee_rad
    else:
        d_o, d_w, d_m = j2_secular_element_rates_rad_s(a, e, i)
        m = el.mean_anomaly_at_epoch_rad + d_m * dt
        m = float(np.arctan2(np.sin(m), np.cos(m)))
        raan = el.raan_rad + d_o * dt
        argp = el.arg_of_perigee_rad + d_w * dt

    e_ann = eccentric_anomaly_eccentric_rad(m, e)
    nu = true_anomaly_rad_from_eccentric(e_ann, e)

    return r_eci_position_m(
        a,
        e,
        i,
        raan,
        argp,
        nu,
    )


def _gmst_rad(
    epoch_seconds: float,
    delta_t_s: float,
    earth_rotation_model: EarthRotationModel,
) -> float:
    if earth_rotation_model == "simple_spin":
        return gmst_rad_simplified(epoch_seconds, delta_t_s)
    return gmst_rad_vallado(epoch_seconds, delta_t_s)


def propagate_keplerian_ecef_m(
    el: SatelliteKeplerianECI,
    epoch_seconds: float,
    time_seconds_since_epoch: float,
    *,
    propagation_model: PropagationModel = "j2_mean_secular",
    earth_rotation_model: EarthRotationModel = "vallado_gmst",
) -> NDArray[np.float64]:
    """ECI position rotated to ECEF [m] using the selected Earth rotation model."""
    r_eci = propagate_keplerian_eci_m(
        el,
        epoch_seconds,
        time_seconds_since_epoch,
        propagation_model=propagation_model,
    )
    theta = _gmst_rad(epoch_seconds, time_seconds_since_epoch, earth_rotation_model)
    return eci_to_ecef_m(r_eci, theta)


def propagate_constellation_ecef_m(
    satellites: Tuple[SatelliteKeplerianECI, ...],
    epoch_seconds: float,
    time_seconds_since_epoch: float,
    *,
    propagation_model: PropagationModel = "j2_mean_secular",
    earth_rotation_model: EarthRotationModel = "vallado_gmst",
) -> NDArray[np.float64]:
    """``(N, 3)`` ECEF positions [m]."""
    if not satellites:
        return np.zeros((0, 3), dtype=np.float64)
    out = np.empty((len(satellites), 3), dtype=np.float64)
    for i, sat in enumerate(satellites):
        out[i, :] = propagate_keplerian_ecef_m(
            sat,
            epoch_seconds,
            time_seconds_since_epoch,
            propagation_model=propagation_model,
            earth_rotation_model=earth_rotation_model,
        )
    return out
