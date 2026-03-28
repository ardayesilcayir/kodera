"""
Regular ground grid over a regional polygon (WGS84 lon/lat).

Spacing is specified in meters and converted to degree steps at the region centroid latitude.
Points are filtered to the polygon interior (Shapely ``contains``; boundary excluded).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from shapely.geometry import Point

from region_service import RegionGeometry

# Mean Earth radius for degree ↔ meter at a given latitude (spherical approximation for spacing only).
_EARTH_R_M = 6371008.8


@dataclass(frozen=True)
class GridConfig:
    """Uniform approximate spacing on the ground in meters."""

    spacing_m: float

    def __post_init__(self) -> None:
        if self.spacing_m <= 0.0:
            raise ValueError("spacing_m must be positive.")


def _meters_to_deg(spacing_m: float, lat_deg: float) -> tuple[float, float]:
    lat_rad = np.radians(lat_deg)
    cos_lat = max(float(np.cos(lat_rad)), 1e-9)
    dlat = spacing_m / _EARTH_R_M * (180.0 / np.pi)
    dlon = spacing_m / (_EARTH_R_M * cos_lat) * (180.0 / np.pi)
    return float(dlat), float(dlon)


def generate_grid(
    region: RegionGeometry,
    config: GridConfig,
    *,
    include_boundary: bool,
) -> NDArray[np.float64]:
    """
    Return ``N × 2`` array of ``[lon, lat]`` in degrees, rows = grid points inside the region.

    Parameters
    ----------
    include_boundary
        If ``False`` (default), points on the polygon boundary are excluded (strict interior).
    """
    poly = region.polygon
    if poly.is_empty:
        return np.zeros((0, 2), dtype=np.float64)

    dlat, dlon = _meters_to_deg(config.spacing_m, region.centroid_lat)
    minx, miny, maxx, maxy = poly.bounds

    lons = np.arange(minx, maxx + dlon, dlon, dtype=np.float64)
    lats = np.arange(miny, maxy + dlat, dlat, dtype=np.float64)
    if lons.size == 0 or lats.size == 0:
        return np.zeros((0, 2), dtype=np.float64)

    pts: list[tuple[float, float]] = []
    pred = poly.covers if include_boundary else poly.contains
    for lat in lats:
        for lon in lons:
            p = Point(float(lon), float(lat))
            if pred(p):
                pts.append((float(lon), float(lat)))

    if not pts:
        return np.zeros((0, 2), dtype=np.float64)
    return np.asarray(pts, dtype=np.float64)
