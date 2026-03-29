"""
ORBITA-R — Target Region
=========================
Target region representation and spatial utility functions.

Supports:
  - Bounding box (bbox) regions
  - Circular regions (center + radius)
  - Polygon regions (list of vertices)
  - Ground point sampling for coverage analysis
  - Haversine (great-circle) distance computation

Coordinate convention:
  - Latitude: geodetic, degrees, [-90, 90]
  - Longitude: degrees, [-180, 180]
  - All distances in km
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .satellite_models import R_EARTH, DEG_TO_RAD, RAD_TO_DEG


# ──────────────────────────────────────────────
# Spatial Utilities
# ──────────────────────────────────────────────

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two points on Earth using the Haversine formula.

    Accurate to ~0.3% vs WGS84 ellipsoidal distance for most practical cases.

    Args:
        lat1, lon1: Point 1 coordinates in degrees.
        lat2, lon2: Point 2 coordinates in degrees.

    Returns:
        Distance in km.
    """
    phi1 = lat1 * DEG_TO_RAD
    phi2 = lat2 * DEG_TO_RAD
    dphi = (lat2 - lat1) * DEG_TO_RAD
    dlam = (lon2 - lon1) * DEG_TO_RAD

    a = math.sin(dphi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    a = min(a, 1.0)  # Clamp for numerical stability
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R_EARTH * c


def point_in_bbox(lat: float, lon: float,
                   bbox: Tuple[float, float, float, float]) -> bool:
    """
    Check if a point is inside a bounding box.

    Args:
        lat, lon: Point coordinates in degrees.
        bbox: (min_lat, min_lon, max_lat, max_lon) in degrees.

    Returns:
        True if the point is inside the bbox.
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def point_in_polygon(lat: float, lon: float,
                      polygon: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a polygon using the ray-casting algorithm.

    The polygon is defined as a list of (lat, lon) vertices.
    Uses the standard even-odd rule.

    Args:
        lat, lon: Point coordinates in degrees.
        polygon: List of (lat, lon) vertices defining the polygon.

    Returns:
        True if the point is inside the polygon.
    """
    n = len(polygon)
    if n < 3:
        return False

    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i]
        yj, xj = polygon[j]

        if ((yi > lat) != (yj > lat)) and \
           (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-15) + xi):
            inside = not inside
        j = i

    return inside


def destination_point(lat: float, lon: float,
                       bearing_deg: float, distance_km: float) -> Tuple[float, float]:
    """
    Compute destination point given start, bearing, and distance.

    Uses spherical Earth approximation.

    Args:
        lat, lon: Start coordinates in degrees.
        bearing_deg: Bearing in degrees (0=North, 90=East).
        distance_km: Distance in km.

    Returns:
        (lat, lon) of the destination in degrees.
    """
    phi1 = lat * DEG_TO_RAD
    lam1 = lon * DEG_TO_RAD
    brng = bearing_deg * DEG_TO_RAD
    d_r = distance_km / R_EARTH

    phi2 = math.asin(
        math.sin(phi1) * math.cos(d_r) +
        math.cos(phi1) * math.sin(d_r) * math.cos(brng)
    )
    lam2 = lam1 + math.atan2(
        math.sin(brng) * math.sin(d_r) * math.cos(phi1),
        math.cos(d_r) - math.sin(phi1) * math.sin(phi2)
    )

    return phi2 * RAD_TO_DEG, lam2 * RAD_TO_DEG


# ──────────────────────────────────────────────
# Target Region
# ──────────────────────────────────────────────

@dataclass
class TargetRegion:
    """
    A geographic target region for satellite coverage.

    Can be defined by:
      - center_lat/center_lon + radius_km (circular)
      - bbox (rectangular, min/max lat/lon)
      - polygon (list of vertices)

    At minimum, center_lat and center_lon must be specified.
    """
    center_lat: float           # Geodetic latitude in degrees
    center_lon: float           # Geodetic longitude in degrees
    radius_km: Optional[float] = None
    bbox: Optional[Tuple[float, float, float, float]] = None  # (min_lat, min_lon, max_lat, max_lon)
    polygon: Optional[List[Tuple[float, float]]] = None

    def __post_init__(self):
        if not -90 <= self.center_lat <= 90:
            raise ValueError(f"center_lat must be in [-90, 90], got {self.center_lat}")
        if not -180 <= self.center_lon <= 180:
            raise ValueError(f"center_lon must be in [-180, 180], got {self.center_lon}")

        # If no shape is specified, default to a 200 km radius circle
        if self.radius_km is None and self.bbox is None and self.polygon is None:
            self.radius_km = 200.0

    def contains(self, lat: float, lon: float) -> bool:
        """Check if a point is inside this region."""
        if self.polygon is not None:
            return point_in_polygon(lat, lon, self.polygon)
        if self.bbox is not None:
            return point_in_bbox(lat, lon, self.bbox)
        if self.radius_km is not None:
            dist = haversine_distance(self.center_lat, self.center_lon, lat, lon)
            return dist <= self.radius_km
        return False

    def get_effective_radius_km(self) -> float:
        """
        Approximate effective radius of the region in km.
        Used when an approximate size is needed regardless of shape type.
        """
        if self.radius_km is not None:
            return self.radius_km
        if self.bbox is not None:
            min_lat, min_lon, max_lat, max_lon = self.bbox
            # Diagonal distance / 2
            diag = haversine_distance(min_lat, min_lon, max_lat, max_lon)
            return diag / 2.0
        if self.polygon is not None and len(self.polygon) >= 3:
            # Average distance from center to vertices
            total = 0.0
            for plat, plon in self.polygon:
                total += haversine_distance(self.center_lat, self.center_lon, plat, plon)
            return total / len(self.polygon)
        return 200.0  # Fallback default


def sample_region_points(region: TargetRegion, n_samples: int = 50,
                          seed: Optional[int] = 42) -> List[Tuple[float, float]]:
    """
    Generate sample ground points within a target region for coverage analysis.

    Uses stratified sampling within the region bounds for better spatial coverage.

    Args:
        region: The target region.
        n_samples: Number of sample points to generate.
        seed: Random seed for reproducibility.

    Returns:
        List of (lat, lon) tuples.
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    points: List[Tuple[float, float]] = []

    # Always include the center point
    points.append((region.center_lat, region.center_lon))

    if region.bbox is not None:
        min_lat, min_lon, max_lat, max_lon = region.bbox
    elif region.radius_km is not None:
        # Approximate bbox from center + radius
        lat_delta = (region.radius_km / R_EARTH) * RAD_TO_DEG
        lon_delta = lat_delta / max(math.cos(region.center_lat * DEG_TO_RAD), 0.01)
        min_lat = max(region.center_lat - lat_delta, -90)
        max_lat = min(region.center_lat + lat_delta, 90)
        min_lon = region.center_lon - lon_delta
        max_lon = region.center_lon + lon_delta
    elif region.polygon is not None and len(region.polygon) >= 3:
        lats = [p[0] for p in region.polygon]
        lons = [p[1] for p in region.polygon]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
    else:
        # Fallback: small region around center
        min_lat = region.center_lat - 2.0
        max_lat = region.center_lat + 2.0
        min_lon = region.center_lon - 2.0
        max_lon = region.center_lon + 2.0

    attempts = 0
    max_attempts = n_samples * 20  # Avoid infinite loop for small regions

    while len(points) < n_samples and attempts < max_attempts:
        lat = rng.uniform(min_lat, max_lat)
        lon = rng.uniform(min_lon, max_lon)

        if region.contains(lat, lon):
            points.append((lat, lon))
        attempts += 1

    return points


def region_area_approx(region: TargetRegion) -> float:
    """
    Approximate area of the target region in km².

    Uses simple geometric approximations.
    """
    if region.radius_km is not None:
        return math.pi * region.radius_km ** 2

    if region.bbox is not None:
        min_lat, min_lon, max_lat, max_lon = region.bbox
        lat_dist = haversine_distance(min_lat, min_lon, max_lat, min_lon)
        avg_lat = (min_lat + max_lat) / 2.0
        lon_dist = haversine_distance(avg_lat, min_lon, avg_lat, max_lon)
        return lat_dist * lon_dist

    if region.polygon is not None and len(region.polygon) >= 3:
        # Shoelace formula approximation on a flat projection (reasonable for small regions)
        coords = region.polygon
        n = len(coords)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            # Convert to approximate km coordinates
            lat_i, lon_i = coords[i]
            lat_j, lon_j = coords[j]
            x_i = lon_i * math.cos(math.radians((lat_i + region.center_lat) / 2)) * 111.32
            y_i = lat_i * 110.574
            x_j = lon_j * math.cos(math.radians((lat_j + region.center_lat) / 2)) * 111.32
            y_j = lat_j * 110.574
            area += x_i * y_j - x_j * y_i
        return abs(area) / 2.0

    # Fallback
    r = region.get_effective_radius_km()
    return math.pi * r ** 2
