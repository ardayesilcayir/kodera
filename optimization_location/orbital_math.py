"""
Earth orbit mechanics (MVP: circular / low-eccentricity).

Physical constants only (WGS84 radius, GM, J2, Earth rotation). J2+ hooks are structured
for future perturbation extensions; propagation is Keplerian two-body for MVP.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

# --- Physical constants (Earth gravity, rotation, shape) ---
MU_EARTH_M3_S2 = 3.986004418e14  # m^3/s^2
R_EARTH_EQUATORIAL_M = 6378137.0
J2 = 1.08262668e-3  # unnormalized
OMEGA_EARTH_RAD_S = 7.2921150e-5  # nominal sidereal Earth rotation

# Mean solar RAAN rate for sun-synchronous inclination constraint (rad/s)
OMEGA_DOT_SUN_SYNCHRONOUS_RAD_S = 2.0 * math.pi / (365.25 * 86400.0)


def mean_motion_rad_s(semi_major_axis_m: float) -> float:
    """Mean motion n = sqrt(mu / a^3) for two-body motion [rad/s]."""
    if semi_major_axis_m <= 0.0:
        raise ValueError("Semi-major axis must be positive.")
    return math.sqrt(MU_EARTH_M3_S2 / semi_major_axis_m**3)


def orbital_period_s(semi_major_axis_m: float) -> float:
    """Keplerian orbital period [s]."""
    n = mean_motion_rad_s(semi_major_axis_m)
    return 2.0 * math.pi / n


def semi_major_axis_m_from_altitude_km(altitude_km: float) -> float:
    """Circular / near-circular: a = R + h."""
    return R_EARTH_EQUATORIAL_M + altitude_km * 1000.0


def altitude_km_from_semi_major_axis_m(a_m: float) -> float:
    return (a_m - R_EARTH_EQUATORIAL_M) / 1000.0


def eccentric_anomaly_eccentric_rad(mean_anomaly_rad: float, eccentricity: float) -> float:
    """Solve Kepler M = E - e sin E for eccentric anomaly E (iterative)."""
    if eccentricity < 0.0 or eccentricity >= 1.0:
        raise ValueError("Eccentric anomaly iteration requires 0 <= e < 1.")
    e = eccentricity
    e_rad = mean_anomaly_rad
    if e < 1e-14:
        return e_rad
    e_ann = e_rad
    for _ in range(40):
        e_new = e_rad + e * math.sin(e_ann)
        if abs(e_new - e_ann) < 1e-14:
            return e_new
        e_ann = e_new
    return e_ann


def true_anomaly_rad_from_eccentric(eccentric_anomaly_rad: float, eccentricity: float) -> float:
    """True anomaly from eccentric anomaly (elliptic)."""
    e = eccentricity
    e_ann = eccentric_anomaly_rad
    beta = e / (1.0 + math.sqrt(1.0 - e * e))
    nu = e_ann + 2.0 * math.atan(beta * math.sin(e_ann) / (1.0 - beta * math.cos(e_ann)))
    return nu


def mean_anomaly_at_time_rad(
    mean_anomaly_epoch_rad: float,
    mean_motion_rad_s: float,
    delta_t_s: float,
) -> float:
    """M(t) = M0 + n * dt, wrapped to [-pi, pi)."""
    m = mean_anomaly_epoch_rad + mean_motion_rad_s * delta_t_s
    return math.atan2(math.sin(m), math.cos(m))


def r_eci_position_m(
    semi_major_axis_m: float,
    eccentricity: float,
    inclination_rad: float,
    raan_rad: float,
    arg_perigee_rad: float,
    true_anomaly_rad: float,
) -> NDArray[np.float64]:
    """
    Position in ECI (J2000-like) [m] from Keplerian elements.

    Near-circular / low-e: ``eccentricity`` is small; use ``arg_perigee`` + ``true_anomaly`` as ω+ν.
    """
    a = semi_major_axis_m
    e = eccentricity
    i = inclination_rad
    o = raan_rad
    w = arg_perigee_rad
    nu = true_anomaly_rad

    p = a * (1.0 - e * e)
    r = p / (1.0 + e * math.cos(nu))
    u = w + nu  # argument of latitude
    cosu = math.cos(u)
    sinu = math.sin(u)
    ci = math.cos(i)
    si = math.sin(i)
    coso = math.cos(o)
    sino = math.sin(o)
    x = r * (coso * cosu - sino * sinu * ci)
    y = r * (sino * cosu + coso * sinu * ci)
    z = r * (sinu * si)
    return np.array([x, y, z], dtype=np.float64)


def eci_to_ecef_rotation(theta_gmst_rad: float) -> NDArray[np.float64]:
    """
    Rotation matrix R such that r_ecef = R @ r_eci.

    ``theta_gmst_rad`` is Greenwich mean sidereal time (rotation about common z-axis).
    """
    c = math.cos(theta_gmst_rad)
    s = math.sin(theta_gmst_rad)
    return np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]], dtype=np.float64)


def eci_to_ecef_m(r_eci_m: NDArray[np.float64], theta_gmst_rad: float) -> NDArray[np.float64]:
    r = eci_to_ecef_rotation(theta_gmst_rad) @ np.asarray(r_eci_m, dtype=np.float64).reshape(3)
    return r


def gmst_rad_simplified(epoch_seconds_s: float, delta_t_s: float) -> float:
    """
    Simple GMST approximation: θ = ω_earth * (epoch + Δt).

    MVP uses a **linear** spin model; higher fidelity uses IAU GMST/ERA.
    """
    return OMEGA_EARTH_RAD_S * (epoch_seconds_s + delta_t_s)


def julian_date_from_posix_seconds(seconds_since_1970: float) -> float:
    """Julian date from POSIX seconds (UTC-like scale; matches propagator epoch usage)."""
    return 2440587.5 + seconds_since_1970 / 86400.0


def gmst_rad_vallado(epoch_seconds_s: float, delta_t_s: float) -> float:
    """
    Greenwich Mean Sidereal Time (Vallado-style, truncated nutation).

    Uses JD from POSIX epoch + ``delta_t``; GMST in degrees from
    ``280.46061837 + 360.98564736629 * (JD - 2451545.0)`` (low-order),
    then wrapped to ``[0, 2π)`` radians.
    """
    jd = julian_date_from_posix_seconds(epoch_seconds_s + delta_t_s)
    d = jd - 2451545.0
    gmst_deg = 280.46061837 + 360.98564736629 * d
    gmst_deg = gmst_deg % 360.0
    if gmst_deg < 0.0:
        gmst_deg += 360.0
    return math.radians(gmst_deg)


def j2_secular_element_rates_rad_s(
    semi_major_axis_m: float,
    eccentricity: float,
    inclination_rad: float,
) -> tuple[float, float, float]:
    """
    First-order J2 secular rates for mean elements (Vallado / Curtis form).

    Returns
    -------
    d_raan_dt, d_arg_perigee_dt, d_mean_anomaly_dt
        RAAN and argument of perigee rates [rad/s]; mean anomaly rate **includes**
        two-body mean motion plus J2 correction (use as dM/dt for propagation).
    """
    a = semi_major_axis_m
    e = eccentricity
    i = inclination_rad
    n = mean_motion_rad_s(a)
    p = a * (1.0 - e * e)
    if p <= 0.0:
        raise ValueError("Invalid semi-latus rectum.")
    rp = R_EARTH_EQUATORIAL_M / p
    inv = 1.0 / (1.0 - e * e) ** 2
    ci = math.cos(i)
    si = math.sin(i)

    d_raan_dt = -1.5 * J2 * rp * rp * n * ci * inv

    d_arg_perigee_dt = 0.75 * J2 * rp * rp * n * (4.0 - 5.0 * si * si) * inv

    sqrt_ome2 = math.sqrt(max(0.0, 1.0 - e * e))
    d_mean_anomaly_dt = n + 0.75 * J2 * rp * rp * n * sqrt_ome2 * (2.0 - 3.0 * si * si) * inv

    return d_raan_dt, d_arg_perigee_dt, d_mean_anomaly_dt


@dataclass
class J2PerturbationModel:
    """
    Placeholder for J2 nodal / apsidal precession (future).

    Expose structure only; callers continue to use two-body Kepler for MVP propagation.
    """

    j2: float = J2
    r_earth_m: float = R_EARTH_EQUATORIAL_M

    def raan_precession_rad_s(
        self,
        semi_major_axis_m: float,
        eccentricity: float,
        inclination_rad: float,
    ) -> float:
        """
        Ω̇ from J2 (approximate circular).

        dΩ/dt = -3/2 J2 (R/p)^2 n cos i / (1-e^2)^2  with p = a(1-e^2).
        """
        a = semi_major_axis_m
        e = eccentricity
        i = inclination_rad
        n = mean_motion_rad_s(a)
        p = a * (1.0 - e * e)
        rp = self.r_earth_m / p
        denom = (1.0 - e * e) ** 2
        return -1.5 * self.j2 * rp * rp * n * math.cos(i) / denom


def sun_synchronous_inclination_rad(
    semi_major_axis_m: float,
    eccentricity: float,
) -> float:
    """
    Inclination for mean sun-synchronous RAAN motion (J2 circularized form).

    cos i = - 2 Ω̇ (1-e^2)^2 / (3 J2 n (R/a)^2) with Ω̇ = 2π/(365.25·86400) rad/s.
    """
    a = semi_major_axis_m
    e = eccentricity
    n = mean_motion_rad_s(a)
    rp = R_EARTH_EQUATORIAL_M / a
    cos_i = (
        -2.0
        * OMEGA_DOT_SUN_SYNCHRONOUS_RAD_S
        * (1.0 - e * e) ** 2
        / (3.0 * J2 * n * rp * rp)
    )
    cos_i = max(-1.0, min(1.0, cos_i))
    return math.acos(cos_i)
