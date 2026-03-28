"""Unit tests for orbit design request validation."""

from __future__ import annotations

import json
from pathlib import Path

from request_models import OrbitDesignRequest
from response_models import ValidationAcceptedResponse, ValidationRejectedResponse
from validation_service import validate_orbit_design_request

_SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def test_valid_sample_json_file_passes() -> None:
    raw = (_SAMPLES / "valid_request.json").read_text(encoding="utf-8")
    outcome = validate_orbit_design_request(raw)
    assert isinstance(outcome, ValidationAcceptedResponse)
    assert outcome.request.mission.type.value == "EARTH_OBSERVATION"


def test_invalid_sample_json_file_rejected() -> None:
    raw = (_SAMPLES / "invalid_request.json").read_text(encoding="utf-8")
    outcome = validate_orbit_design_request(raw)
    assert isinstance(outcome, ValidationRejectedResponse)
    assert outcome.errors


def test_missing_required_top_level_field() -> None:
    outcome = validate_orbit_design_request({"region": {}, "mission": {}})
    assert isinstance(outcome, ValidationRejectedResponse)
    assert "missing" in str(outcome.errors).lower() or any("missing" in e.msg.lower() for e in outcome.errors)


def test_region_point_radius_lat_out_of_range() -> None:
    payload = {
        "region": {
            "mode": "point_radius",
            "lat": 95.0,
            "lon": 0.0,
            "radius_km": 100.0,
        },
        "mission": {
            "type": "BALANCED",
            "continuous_coverage_required": True,
            "analysis_horizon_hours": 24.0,
            "validation_horizon_days": 7.0,
        },
        "sensor_model": {
            "type": "generic",
            "min_elevation_deg": 10.0,
            "sensor_half_angle_deg": 15.0,
            "max_off_nadir_deg": 5.0,
            "min_access_duration_s": 60.0,
        },
        "optimization": {
            "primary_goal": "MINIMIZE_SATELLITE_COUNT",
            "secondary_goals": [],
            "allowed_orbit_families": ["LEO"],
            "max_satellites": 12,
            "max_planes": 3,
        },
    }
    outcome = validate_orbit_design_request(payload)
    assert isinstance(outcome, ValidationRejectedResponse)


def test_polygon_not_closed() -> None:
    payload = _minimal_valid_payload_point_radius()
    payload["region"] = {
        "mode": "polygon",
        "polygon": {
            "type": "Polygon",
            "coordinates": [
                [
                    [0.0, 0.0],
                    [1.0, 0.0],
                    [1.0, 1.0],
                    [0.0, 1.0],
                ]
            ],
        },
    }
    outcome = validate_orbit_design_request(payload)
    assert isinstance(outcome, ValidationRejectedResponse)


def test_max_planes_exceeds_max_satellites() -> None:
    p = _minimal_valid_payload_point_radius()
    p["optimization"]["max_satellites"] = 4
    p["optimization"]["max_planes"] = 8
    outcome = validate_orbit_design_request(p)
    assert isinstance(outcome, ValidationRejectedResponse)


def test_invalid_json_string() -> None:
    outcome = validate_orbit_design_request("{ not json")
    assert isinstance(outcome, ValidationRejectedResponse)
    assert any(e.type == "parse_error" for e in outcome.errors)


def test_model_validate_direct_polygon() -> None:
    data = json.loads((_SAMPLES / "valid_request_polygon.json").read_text(encoding="utf-8"))
    m = OrbitDesignRequest.model_validate(data)
    assert m.region.mode == "polygon"


def _minimal_valid_payload_point_radius() -> dict:
    return {
        "region": {
            "mode": "point_radius",
            "lat": 39.0,
            "lon": 35.0,
            "radius_km": 500.0,
        },
        "mission": {
            "type": "BALANCED",
            "continuous_coverage_required": True,
            "analysis_horizon_hours": 24.0,
            "validation_horizon_days": 7.0,
        },
        "sensor_model": {
            "type": "generic",
            "min_elevation_deg": 10.0,
            "sensor_half_angle_deg": 15.0,
            "max_off_nadir_deg": 5.0,
            "min_access_duration_s": 60.0,
        },
        "optimization": {
            "primary_goal": "MINIMIZE_SATELLITE_COUNT",
            "secondary_goals": [],
            "allowed_orbit_families": ["LEO"],
            "max_satellites": 12,
            "max_planes": 3,
        },
    }
