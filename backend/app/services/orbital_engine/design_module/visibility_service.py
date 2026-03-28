"""
Line-of-sight visibility using geodetic elevation angle above the local horizon.

The horizon plane is tangent to the WGS84 ellipsoid at the ground station; ``up`` is the
outward surface normal at the station's geodetic coordinates.
"""

from __future__ import annotations

import math
import numpy as np
from numpy.typing import NDArray

from geo_utils import ecef_position_to_geodetic_up


def elevation_angle_deg(
    satellite_ecef_m: NDArray[np.float64],
    ground_ecef_m: NDArray[np.float64],
) -> float:
    """
    Elevation angle [deg] of the satellite above the local horizon at the ground point.

    Returns a value in ``[-90, 90]``. Below-horizon geometry yields negative elevation.
    """
    sat = np.asarray(satellite_ecef_m, dtype=np.float64).reshape(3)
    gnd = np.asarray(ground_ecef_m, dtype=np.float64).reshape(3)
    los = sat - gnd
    dist = float(np.linalg.norm(los))
    if dist < 1e-6:
        raise ValueError("Satellite and ground positions coincide.")
    u_los = los / dist
    gx, gy, gz = float(gnd[0]), float(gnd[1]), float(gnd[2])
    u_up = ecef_position_to_geodetic_up(gx, gy, gz)
    sin_el = float(np.dot(u_los, u_up))
    sin_el = max(-1.0, min(1.0, sin_el))
    return math.degrees(math.asin(sin_el))


def is_visible(
    satellite_ecef_m: NDArray[np.float64],
    ground_ecef_m: NDArray[np.float64],
    min_elevation_deg: float,
) -> bool:
    """``True`` iff elevation ≥ ``min_elevation_deg``."""
    el = elevation_angle_deg(satellite_ecef_m, ground_ecef_m)
    return el >= float(min_elevation_deg)


def nadir_angle_deg(
    satellite_ecef_m: NDArray[np.float64],
    ground_ecef_m: NDArray[np.float64],
) -> float:
    """
    Angle [deg] between satellite→ground LOS and satellite nadir (toward Earth center).

    ``0°`` when the ground point is along the nadir; increases as the target moves toward
    the limb (subject to geometry).
    """
    sat = np.asarray(satellite_ecef_m, dtype=np.float64).reshape(3)
    gnd = np.asarray(ground_ecef_m, dtype=np.float64).reshape(3)
    r = float(np.linalg.norm(sat))
    if r < 1.0:
        raise ValueError("Invalid satellite position.")
    nadir = -sat / r
    los = gnd - sat
    d = float(np.linalg.norm(los))
    if d < 1e-3:
        raise ValueError("Satellite and ground positions coincide.")
    u = los / d
    c = float(np.dot(u, nadir))
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))


def effective_nadir_limit_deg(sensor_half_angle_deg: float, max_off_nadir_deg: float) -> float:
    """
    Combined boresight / steering limit for nadir-pointing instruments.

    If ``max_off_nadir_deg > 0``, use ``min(sensor_half_angle_deg, max_off_nadir_deg)``.
    If ``max_off_nadir_deg == 0``, treat as *no extra steering cap* and use the sensor cone
    only (``sensor_half_angle_deg``).
    """
    sh = float(sensor_half_angle_deg)
    if max_off_nadir_deg > 0.0:
        return min(sh, float(max_off_nadir_deg))
    return sh


def is_link_accessible(
    satellite_ecef_m: NDArray[np.float64],
    ground_ecef_m: NDArray[np.float64],
    min_elevation_deg: float,
    max_nadir_angle_deg: float,
) -> bool:
    """
    Geometric link: min elevation mask **and** ground within a nadir-centered cone of
    half-angle ``max_nadir_angle_deg`` (sensor FOV / steering envelope).
    """
    if not is_visible(satellite_ecef_m, ground_ecef_m, min_elevation_deg):
        return False
    na = nadir_angle_deg(satellite_ecef_m, ground_ecef_m)
    return na <= float(max_nadir_angle_deg) + 1e-9


def elevation_angle_deg_batch(
    satellite_ecef_m: NDArray[np.float64],
    ground_ecef_m: NDArray[np.float64],
) -> NDArray[np.float64]:
    """
    Vectorized elevation [deg] for one satellite position and ``N`` ground points.

    ``ground_ecef_m`` has shape ``(N, 3)``; returns shape ``(N,)``.
    """
    sat = np.asarray(satellite_ecef_m, dtype=np.float64).reshape(3)
    gnd = np.asarray(ground_ecef_m, dtype=np.float64)
    if gnd.ndim != 2 or gnd.shape[1] != 3:
        raise ValueError("ground_ecef_m must have shape (N, 3).")
    los = sat[np.newaxis, :] - gnd
    dist = np.linalg.norm(los, axis=1)
    if np.any(dist < 1e-6):
        raise ValueError("Satellite and at least one ground position coincide.")
    u_los = los / dist[:, np.newaxis]
    # Geodetic up per row
    n = gnd.shape[0]
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        u_up = ecef_position_to_geodetic_up(float(gnd[i, 0]), float(gnd[i, 1]), float(gnd[i, 2]))
        s = float(np.dot(u_los[i], u_up))
        s = max(-1.0, min(1.0, s))
        out[i] = math.degrees(math.asin(s))
    return out
