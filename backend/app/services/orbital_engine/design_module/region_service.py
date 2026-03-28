"""
Regional geometry: resolve point+radius or GeoJSON polygon to a closed polygon and metadata.

Circle approximation uses WGS84 geodesic forward steps (physically consistent, not planar buffer).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from pyproj import Geod
from shapely.geometry import Polygon

from request_models import GeoJSONPolygon, RegionPointRadius, RegionPolygon

_WGS84_GEOD = Geod(ellps="WGS84")


@dataclass(frozen=True)
class RegionGeometry:
    """
    Normalized region in WGS84 lon/lat (degrees).

    ``polygon`` exterior is counter-clockwise as in GeoJSON; coordinates are (lon, lat).
    """

    polygon: Polygon
    centroid_lon: float
    centroid_lat: float
    bbox_min_lon: float
    bbox_min_lat: float
    bbox_max_lon: float
    bbox_max_lat: float
    area_m2: float
    perimeter_m: float
    geodesic_circle_vertices: Optional[int]
    """If the region came from point+radius, number of vertices used; else ``None``."""


def _geojson_to_shapely(g: GeoJSONPolygon) -> Polygon:
    exterior = [(c[0], c[1]) for c in g.coordinates[0]]
    holes: List[List[Tuple[float, float]]] = []
    for ring in g.coordinates[1:]:
        holes.append([(c[0], c[1]) for c in ring])
    return Polygon(exterior, holes)


def _circle_to_polygon_lonlat(
    lon_deg: float,
    lat_deg: float,
    radius_km: float,
    n_vertices: int,
) -> Polygon:
    if n_vertices < 8:
        raise ValueError("n_vertices must be at least 8 for a stable circle approximation.")
    radius_m = radius_km * 1000.0
    ring: List[Tuple[float, float]] = []
    for i in range(n_vertices):
        azimuth_deg = 360.0 * i / n_vertices
        lon2, lat2, _ = _WGS84_GEOD.fwd(lon_deg, lat_deg, azimuth_deg, radius_m)
        ring.append((float(lon2), float(lat2)))
    ring.append(ring[0])
    return Polygon(ring)


def _utm_epsg(lon_deg: float, lat_deg: float) -> int:
    zone = int((lon_deg + 180.0) // 6.0) + 1
    zone = min(max(zone, 1), 60)
    if lat_deg >= 0:
        return 32600 + zone
    return 32700 + zone


def _centroid_lonlat(poly: Polygon) -> Tuple[float, float]:
    """Planar centroid in a local UTM zone, then back to lon/lat (adequate for regional AOIs)."""
    from pyproj import Transformer

    minx, miny, maxx, maxy = poly.bounds
    cx = 0.5 * (minx + maxx)
    cy = 0.5 * (miny + maxy)
    epsg = _utm_epsg(cx, cy)
    fwd = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    inv = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    gx, gy = poly.exterior.xy
    xs = list(gx)
    ys = list(gy)
    px, py = fwd.transform(xs, ys)
    pp = Polygon(list(zip(px, py)))
    c = pp.centroid
    lon, lat = inv.transform(c.x, c.y)
    return float(lon), float(lat)


def _geodesic_area_perimeter(poly: Polygon) -> Tuple[float, float]:
    """Signed geodesic area (m²) and perimeter (m) on WGS84."""
    if poly.is_empty:
        return 0.0, 0.0
    lon, lat = poly.exterior.xy
    lons = list(lon) + [list(lon)[0]]
    lats = list(lat) + [list(lat)[0]]
    area, perim = _WGS84_GEOD.polygon_area_perimeter(lons, lats)
    return abs(float(area)), abs(float(perim))


def resolve_region(
    region: Union[RegionPointRadius, RegionPolygon],
    *,
    circle_vertices: int,
) -> RegionGeometry:
    """
    Build a single Shapely polygon (lon/lat °) and compute metadata.

    Point+radius is replaced by a geodesic ``circle_vertices``-gon (caller-supplied; no default).
    """
    if isinstance(region, RegionPointRadius):
        poly = _circle_to_polygon_lonlat(
            region.lon,
            region.lat,
            region.radius_km,
            circle_vertices,
        )
        geo_vertices = circle_vertices
    else:
        poly = _geojson_to_shapely(region.polygon)
        geo_vertices = None

    if not poly.is_valid:
        poly = poly.buffer(0)

    minx, miny, maxx, maxy = poly.bounds
    c_lon, c_lat = _centroid_lonlat(poly)
    area_m2, perim_m = _geodesic_area_perimeter(poly)

    return RegionGeometry(
        polygon=poly,
        centroid_lon=c_lon,
        centroid_lat=c_lat,
        bbox_min_lon=minx,
        bbox_min_lat=miny,
        bbox_max_lon=maxx,
        bbox_max_lat=maxy,
        area_m2=area_m2,
        perimeter_m=perim_m,
        geodesic_circle_vertices=geo_vertices,
    )
