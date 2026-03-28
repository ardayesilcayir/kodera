"""FastAPI design endpoint tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_design_orbit_returns_200_with_sample_payload(client: TestClient) -> None:
    path = _ROOT / "samples" / "api_design_request.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    r = client.post("/api/v1/design/orbit", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "recommended_architecture" in data
    assert "top_candidates" in data
    assert "feasibility_summary" in data
    assert "explanation" in data
    assert "coverage_metrics" in data


def test_design_orbit_public_contract_exact_body(client: TestClient) -> None:
    """Contract documented as the single public POST body (no wrapper keys)."""
    payload = {
        "region": {
            "mode": "point_radius",
            "lat": 38.3552,
            "lon": 38.3095,
            "radius_km": 75.0,
        },
        "mission": {
            "type": "EMERGENCY_COMMS",
            "continuous_coverage_required": True,
            "analysis_horizon_hours": 24,
            "validation_horizon_days": 7,
        },
        "sensor_model": {
            "type": "communications",
            "min_elevation_deg": 10.0,
            "sensor_half_angle_deg": 45.0,
            "max_off_nadir_deg": 45.0,
            "min_access_duration_s": 60,
        },
        "optimization": {
            "primary_goal": "MINIMIZE_SATELLITE_COUNT",
            "secondary_goals": [
                "MINIMIZE_LAUNCH_MASS",
                "MINIMIZE_PROPULSION_BUDGET",
            ],
            "allowed_orbit_families": ["LEO", "MEO", "GEO", "SSO"],
            "max_satellites": 48,
            "max_planes": 12,
        },
    }
    r = client.post("/api/v1/design/orbit", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "feasibility_summary" in data
    assert data["feasibility_summary"]["total_candidates_evaluated"] >= 1


def test_continuous_coverage_api_never_recommends_without_24_7_metrics(client: TestClient) -> None:
    """If continuous coverage is required, recommendation implies ``continuous_24_7_feasible``."""
    path = _ROOT / "samples" / "api_design_request_continuous_comms.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    r = client.post("/api/v1/design/orbit", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    fs = data["feasibility_summary"]
    assert fs["continuous_coverage_required"] is True
    if data["recommended_architecture"] is not None:
        assert data["coverage_metrics"] is not None
        assert data["coverage_metrics"]["continuous_24_7_feasible"] is True
        assert fs["recommended_feasible"] is True
    else:
        assert fs["recommended_feasible"] is False


def test_design_orbit_422_on_invalid_region(client: TestClient) -> None:
    path = _ROOT / "samples" / "api_design_request.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["region"] = {
        "mode": "point_radius",
        "lat": 41.0,
        "lon": 29.0,
    }
    r = client.post("/api/v1/design/orbit", json=payload)
    assert r.status_code == 422
