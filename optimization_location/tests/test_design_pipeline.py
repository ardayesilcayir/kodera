"""Integration tests: full design pipeline (validate → enumerate → simulate → recommend)."""

from __future__ import annotations

import pytest

from candidate_models import (
    CandidateGenerationInput,
    OrbitFamilySearchParams,
    WalkerTopologyGrid,
)
from designer_service import run_design
from optimizer_models import DesignerParams
from request_models import (
    GeoJSONPolygon,
    MissionSpec,
    MissionType,
    OptimizationSpec,
    OrbitDesignRequest,
    PrimaryOptimizationGoal,
    RegionPolygon,
    SensorModelSpec,
    SensorModelType,
)


def _minimal_request(*, continuous: bool) -> OrbitDesignRequest:
    return OrbitDesignRequest(
        region=RegionPolygon(
            mode="polygon",
            polygon=GeoJSONPolygon(
                type="Polygon",
                coordinates=[
                    [
                        [29.0, 41.0],
                        [29.2, 41.0],
                        [29.2, 41.2],
                        [29.0, 41.2],
                        [29.0, 41.0],
                    ]
                ],
            ),
        ),
        mission=MissionSpec(
            type=MissionType.BALANCED,
            continuous_coverage_required=continuous,
            analysis_horizon_hours=0.25,
            validation_horizon_days=1.0,
        ),
        sensor_model=SensorModelSpec(
            type=SensorModelType.GENERIC,
            min_elevation_deg=5.0,
            sensor_half_angle_deg=30.0,
            max_off_nadir_deg=0.0,
            min_access_duration_s=1.0,
        ),
        optimization=OptimizationSpec(
            primary_goal=PrimaryOptimizationGoal.MINIMIZE_SATELLITE_COUNT,
            secondary_goals=[],
            allowed_orbit_families=["LEO"],
            max_satellites=6,
            max_planes=3,
        ),
    )


def test_design_pipeline_runs_and_returns_structured_result() -> None:
    req = _minimal_request(continuous=False)
    cgen = CandidateGenerationInput(
        mission_type=req.mission.type,
        allowed_families=tuple(req.optimization.allowed_orbit_families),
        family_search=(
            OrbitFamilySearchParams(
                family=req.optimization.allowed_orbit_families[0],
                altitude_km_min=500.0,
                altitude_km_max=500.0,
                altitude_km_step=1.0,
                inclination_deg_min=51.6,
                inclination_deg_max=51.6,
                inclination_deg_step=1.0,
                eccentricity_max=0.0,
                sso_inclination_mode="none",
            ),
        ),
        walker_grid=WalkerTopologyGrid(
            total_satellites_T=[4],
            planes_P=[2],
            phase_F=[0],
        ),
        max_satellites=req.optimization.max_satellites,
        max_planes=req.optimization.max_planes,
        epoch_seconds_tai=0.0,
    )
    dp = DesignerParams(
        grid_spacing_m=150_000.0,
        simulation_time_step_seconds=120.0,
        region_circle_vertices=24,
        early_stop_on_first_feasible_minimum_t=False,
        footprint_solid_angle_packing_factor=1.15,
        top_candidates_limit=5,
        grid_include_boundary=False,
    )
    result = run_design(req, cgen, dp)
    assert result.evaluations
    assert len(result.explanations) >= 1
    assert result.recommended is not None
    assert result.recommended.total_satellites_T == 4


def test_continuous_mode_may_yield_no_recommendation() -> None:
    """Strict continuous coverage often fails for toy grids; pipeline must still complete."""
    req = _minimal_request(continuous=True)
    cgen = CandidateGenerationInput(
        mission_type=req.mission.type,
        allowed_families=tuple(req.optimization.allowed_orbit_families),
        family_search=(
            OrbitFamilySearchParams(
                family=req.optimization.allowed_orbit_families[0],
                altitude_km_min=500.0,
                altitude_km_max=500.0,
                altitude_km_step=1.0,
                inclination_deg_min=51.6,
                inclination_deg_max=51.6,
                inclination_deg_step=1.0,
                eccentricity_max=0.0,
                sso_inclination_mode="none",
            ),
        ),
        walker_grid=WalkerTopologyGrid(
            total_satellites_T=[4],
            planes_P=[2],
            phase_F=[0],
        ),
        max_satellites=req.optimization.max_satellites,
        max_planes=req.optimization.max_planes,
        epoch_seconds_tai=0.0,
    )
    dp = DesignerParams(
        grid_spacing_m=150_000.0,
        simulation_time_step_seconds=120.0,
        region_circle_vertices=24,
        early_stop_on_first_feasible_minimum_t=True,
        footprint_solid_angle_packing_factor=1.15,
        top_candidates_limit=5,
        grid_include_boundary=False,
    )
    result = run_design(req, cgen, dp)
    assert result.continuous_coverage_required is True
    assert isinstance(result.explanations, tuple)
    if result.recommended is not None:
        assert result.recommended.metrics.continuous_24_7_feasible is True


def test_designer_rejects_mismatched_candidate_input() -> None:
    req = _minimal_request(continuous=False)
    bad = CandidateGenerationInput(
        mission_type=req.mission.type,
        allowed_families=tuple(req.optimization.allowed_orbit_families),
        family_search=(
            OrbitFamilySearchParams(
                family=req.optimization.allowed_orbit_families[0],
                altitude_km_min=500.0,
                altitude_km_max=500.0,
                altitude_km_step=1.0,
                inclination_deg_min=51.6,
                inclination_deg_max=51.6,
                inclination_deg_step=1.0,
                eccentricity_max=0.0,
                sso_inclination_mode="none",
            ),
        ),
        walker_grid=WalkerTopologyGrid(
            total_satellites_T=[4],
            planes_P=[2],
            phase_F=[0],
        ),
        max_satellites=99,
        max_planes=req.optimization.max_planes,
        epoch_seconds_tai=0.0,
    )
    dp = DesignerParams(
        grid_spacing_m=150_000.0,
        simulation_time_step_seconds=120.0,
        region_circle_vertices=24,
        early_stop_on_first_feasible_minimum_t=False,
        footprint_solid_angle_packing_factor=1.15,
        top_candidates_limit=5,
        grid_include_boundary=False,
    )
    with pytest.raises(ValueError, match="max_satellites"):
        run_design(req, bad, dp)
