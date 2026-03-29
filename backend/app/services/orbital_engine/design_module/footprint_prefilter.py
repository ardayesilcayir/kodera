"""
Conservative footprint-based pruning before full time-domain visibility simulation.

Uses spherical-Earth geometry: each satellite at altitude ``h`` can serve ground points within
an angular radius ``γ`` (from sub-satellite) where elevation ≥ ``min_elevation_deg`` when the
satellite is instantaneously at zenith of that sub-satellite point (best-case geometry).

A lower bound on required satellite count is derived from solid-angle coverage (cap vs region).
This is **conservative**: it may fail-open (never prune a feasible case) when uncertain;
when it prunes, the case is **clearly** capacity-starved for instantaneous blanket coverage.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

from orbital_math import R_EARTH_EQUATORIAL_M
from region_service import RegionGeometry
from visibility_service import elevation_angle_deg

import numpy as np


def _satellite_position_zenith_equator(altitude_km: float) -> np.ndarray:
    """ECEF [m] of circular orbit satellite at zenith of (lat=0, lon=0)."""
    from geo_utils import llh_to_ecef

    g0 = llh_to_ecef(0.0, 0.0, 0.0)
    u = g0 / np.linalg.norm(g0)
    r_m = R_EARTH_EQUATORIAL_M + altitude_km * 1000.0
    return u * r_m


def _ground_point_at_angular_offset_rad(angular_offset_rad: float) -> np.ndarray:
    """Great-circle offset north from (0,0) by ``angular_offset_rad`` on the sphere."""
    from pyproj import Geod

    geod = Geod(ellps="WGS84")
    lon0, lat0 = 0.0, 0.0
    az_deg = 0.0  # north
    dist_m = angular_offset_rad * R_EARTH_EQUATORIAL_M
    lon, lat, _ = geod.fwd(lon0, lat0, az_deg, dist_m)
    from geo_utils import llh_to_ecef

    return llh_to_ecef(float(lat), float(lon), 0.0)


def footprint_angular_radius_rad(altitude_km: float, min_elevation_deg: float) -> float:
    """
    Maximum Earth central angle from sub-satellite to a ground point that can still have
    elevation ≥ ``min_elevation_deg`` when the satellite is at zenith of the sub-satellite.
    """
    sat = _satellite_position_zenith_equator(altitude_km)

    def el_at_gamma(gamma_rad: float) -> float:
        g = _ground_point_at_angular_offset_rad(gamma_rad)
        return elevation_angle_deg(sat, g)

    lo, hi = 0.0, 0.5 * math.pi
    if el_at_gamma(hi) >= min_elevation_deg:
        return hi
    if el_at_gamma(0.0) < min_elevation_deg:
        return 0.0

    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if el_at_gamma(mid) >= min_elevation_deg:
            lo = mid
        else:
            hi = mid
    return lo


def region_max_geodesic_extent_m(geometry: RegionGeometry) -> float:
    """Maximum pairwise geodesic distance between polygon vertices and bbox corners [m]."""
    from pyproj import Geod

    geod = Geod(ellps="WGS84")
    pts: list[tuple[float, float]] = list(geometry.polygon.exterior.coords)[:-1]
    minx, miny, maxx, maxy = geometry.bbox_min_lon, geometry.bbox_min_lat, geometry.bbox_max_lon, geometry.bbox_max_lat
    for lon, lat in ((minx, miny), (minx, maxy), (maxx, miny), (maxx, maxy)):
        pts.append((lon, lat))

    max_m = 0.0
    for i, a in enumerate(pts):
        for b in pts[i + 1 :]:
            _, _, d = geod.inv(a[0], a[1], b[0], b[1])
            max_m = max(max_m, abs(d))
    return max_m


def solid_angle_cap_omega_rad2(angular_radius_rad: float) -> float:
    """Solid angle of a spherical cap of angular radius γ on unit sphere × R² scaling omitted."""
    g = angular_radius_rad
    return 2.0 * math.pi * (1.0 - math.cos(g))


def minimum_satellites_lower_bound(
    altitude_km: float,
    min_elevation_deg: float,
    region_geometry: RegionGeometry,
    *,
    solid_angle_packing_factor: float,
) -> int:
    """
    Loose lower bound on satellite count from solid-angle coverage (caller supplies
    ``solid_angle_packing_factor`` > 1).
    """
    if solid_angle_packing_factor <= 1.0:
        raise ValueError("solid_angle_packing_factor must be > 1.0.")
    gamma = footprint_angular_radius_rad(altitude_km, min_elevation_deg)
    if gamma <= 0.0:
        return 10**9
    omega_cap = solid_angle_cap_omega_rad2(gamma)
    # Region solid angle ~ A / R^2 (small-patch approx; capped)
    a = max(region_geometry.area_m2, 1.0)
    omega_reg = min(2.0 * math.pi, a / (R_EARTH_EQUATORIAL_M**2))
    return max(1, math.ceil(solid_angle_packing_factor * omega_reg / omega_cap))


def prune_candidate_by_footprint(
    total_satellites_T: int,
    altitude_km: float,
    min_elevation_deg: float,
    region_geometry: RegionGeometry,
    *,
    solid_angle_packing_factor: float,
) -> Tuple[bool, Optional[str]]:
    """
    Returns ``(True, reason)`` if candidate should be pruned (clearly under-capacity).

    If ``False``, second value is ``None`` (run full simulation).
    """
    t_lb = minimum_satellites_lower_bound(
        altitude_km,
        min_elevation_deg,
        region_geometry,
        solid_angle_packing_factor=solid_angle_packing_factor,
    )
    if total_satellites_T < t_lb:
        return (
            True,
            f"Footprint lower bound: T={total_satellites_T} < estimated minimum {t_lb} "
            f"for altitude {altitude_km:.1f} km and min elevation {min_elevation_deg:.1f}° "
            f"(region solid-angle vs single-satellite cap; packing_factor={solid_angle_packing_factor}).",
        )
    return (False, None)
