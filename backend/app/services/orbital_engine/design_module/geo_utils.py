"""
WGS84 ellipsoid geodetic (LLH) ↔ ECEF conversions.

Physical model: WGS84 (a, f) — no operational mission defaults.
"""

from __future__ import annotations

import math
from typing import Tuple

import numpy as np
from numpy.typing import NDArray

# WGS84 (NIMA TR8350.2)
WGS84_A = 6378137.0  # semi-major axis [m]
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)  # first eccentricity squared
WGS84_B = WGS84_A * (1.0 - WGS84_F)  # semi-minor axis [m]


def llh_to_ecef(
    lat_deg: float,
    lon_deg: float,
    h_m: float,
) -> NDArray[np.float64]:
    """
    Geodetic latitude / longitude / height above ellipsoid → ECEF [m].

    Latitude and longitude are geodetic (not geocentric).
    """
    phi = math.radians(lat_deg)
    lam = math.radians(lon_deg)
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)

    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_phi * sin_phi)
    x = (n + h_m) * cos_phi * cos_lam
    y = (n + h_m) * cos_phi * sin_lam
    z = (n * (1.0 - WGS84_E2) + h_m) * sin_phi
    return np.array([x, y, z], dtype=np.float64)


def ecef_to_llh(
    x: float,
    y: float,
    z: float,
    *,
    tol: float = 1e-14,
    max_iter: int = 15,
) -> Tuple[float, float, float]:
    """
    ECEF [m] → geodetic latitude [deg], longitude [deg], height above ellipsoid [m].

    Iterative geodetic inverse (Heiskanen / standard GNSS formulation).
    """
    lon = math.atan2(y, x)
    p = math.hypot(x, y)
    if p < tol and abs(z) < tol:
        return 0.0, math.degrees(lon), -WGS84_A

    # Near polar axis
    if p < tol:
        lat = math.copysign(math.pi / 2.0, z)
        h = abs(z) - WGS84_B
        return math.degrees(lat), math.degrees(lon), h

    lat = math.atan2(z, p * (1.0 - WGS84_E2))
    h = 0.0
    for _ in range(max_iter):
        sin_lat = math.sin(lat)
        n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
        lat_new = math.atan2(z + WGS84_E2 * n * sin_lat, p)
        if abs(lat_new - lat) < tol:
            lat = lat_new
            break
        lat = lat_new

    sin_lat = math.sin(lat)
    cos_lat = math.cos(lat)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
    if abs(cos_lat) < tol:
        h = abs(z) / abs(sin_lat) - n * (1.0 - WGS84_E2)
    else:
        h = p / cos_lat - n

    return math.degrees(lat), math.degrees(lon), h


def geodetic_up_unit_ecef(lat_deg: float, lon_deg: float) -> NDArray[np.float64]:
    """
    Unit vector along ellipsoid **outward normal** at geodetic (lat, lon).

    û = (cos φ cos λ, cos φ sin λ, (1 − e²) sin φ) / √(1 − e² sin² φ)
    """
    phi = math.radians(lat_deg)
    lam = math.radians(lon_deg)
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)

    w = math.sqrt(1.0 - WGS84_E2 * sin_phi * sin_phi)
    ux = cos_phi * cos_lam / w
    uy = cos_phi * sin_lam / w
    uz = (1.0 - WGS84_E2) * sin_phi / w
    u = np.array([ux, uy, uz], dtype=np.float64)
    nrm = float(np.linalg.norm(u))
    if nrm == 0.0:
        raise ValueError("Degenerate geodetic up vector.")
    return u / nrm


def ecef_position_to_geodetic_up(x: float, y: float, z: float) -> NDArray[np.float64]:
    """
    Outward ellipsoid normal at the geodetic location of ECEF point (x,y,z).

    Uses geodetic latitude/longitude of the point (height ignored for the normal direction).
    """
    lat_deg, lon_deg, _h = ecef_to_llh(x, y, z)
    return geodetic_up_unit_ecef(lat_deg, lon_deg)
