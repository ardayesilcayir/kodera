"""Region resolution and interior grid generation."""

from __future__ import annotations

from grid_service import GridConfig, generate_grid
from region_service import resolve_region
from request_models import GeoJSONPolygon, RegionPolygon, RegionPointRadius


def test_point_radius_yields_polygon_metadata() -> None:
    r = RegionPointRadius(mode="point_radius", lat=41.0, lon=29.0, radius_km=50.0)
    g = resolve_region(r, circle_vertices=32)
    assert g.area_m2 > 0.0
    assert g.geodesic_circle_vertices == 32
    assert not g.polygon.is_empty


def test_grid_points_inside_polygon_only() -> None:
    poly = GeoJSONPolygon(
        type="Polygon",
        coordinates=[
            [
                [29.0, 41.0],
                [29.5, 41.0],
                [29.5, 41.5],
                [29.0, 41.5],
                [29.0, 41.0],
            ]
        ],
    )
    region = RegionPolygon(mode="polygon", polygon=poly)
    geom = resolve_region(region, circle_vertices=96)
    cfg = GridConfig(spacing_m=20000.0)
    pts = generate_grid(geom, cfg, include_boundary=False)
    assert pts.shape[0] > 0
    from shapely.geometry import Point

    for i in range(pts.shape[0]):
        p = Point(float(pts[i, 0]), float(pts[i, 1]))
        assert geom.polygon.contains(p)
