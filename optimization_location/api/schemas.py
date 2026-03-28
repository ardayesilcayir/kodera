"""Pydantic API models for POST /api/v1/design/orbit (JSON ↔ internal dataclasses)."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from request_models import MissionType, OrbitFamily


class OrbitFamilySearchParamsPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    family: OrbitFamily
    altitude_km_min: float
    altitude_km_max: float
    altitude_km_step: float
    inclination_deg_min: float
    inclination_deg_max: float
    inclination_deg_step: float
    eccentricity_max: float
    sso_inclination_mode: Literal["none", "mean_sun_synchronous"] = Field(
        description='For SSO only: "mean_sun_synchronous" uses J2 mean sun-sync inclination.',
    )


class WalkerTopologyGridPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_satellites_T: List[int]
    planes_P: List[int]
    phase_F: List[int]


class CandidateGenerationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mission_type: MissionType
    allowed_families: List[OrbitFamily]
    family_search: List[OrbitFamilySearchParamsPayload]
    walker_grid: WalkerTopologyGridPayload
    max_satellites: int
    max_planes: int
    epoch_seconds_tai: float


class DesignerParamsPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grid_spacing_m: float = Field(gt=0.0)
    simulation_time_step_seconds: float = Field(gt=0.0)
    region_circle_vertices: int = Field(ge=8)
    early_stop_on_first_feasible_minimum_t: bool
    footprint_solid_angle_packing_factor: float = Field(
        gt=1.0,
        description="Conservative multiplier for solid-angle T lower bound in footprint pruning.",
    )
    top_candidates_limit: int = Field(ge=1)
    grid_include_boundary: bool
    propagation_model: Literal["two_body_kepler", "j2_mean_secular"] = "j2_mean_secular"
    earth_rotation_model: Literal["simple_spin", "vallado_gmst"] = "vallado_gmst"


class RecommendedArchitectureResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    orbit_family: str
    altitude_km: float
    inclination_deg: float
    total_satellites_T: int
    planes_P: int
    phase_F: int


class TopCandidateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int
    orbit_family: str
    altitude_km: float
    inclination_deg: float
    total_satellites_T: int
    planes_P: int
    phase_F: int
    feasible: bool
    mission_objective_met: bool
    cost_score: float
    complexity_score: float
    min_point_coverage: float
    worst_cell_gap_seconds: float


class FeasibilitySummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    continuous_coverage_required: bool
    continuous_coverage_strategy: str
    recommended_feasible: bool
    total_candidates_evaluated: int
    pruned_by_footprint: int
    simulated_continuous_infeasible: int


class CoverageMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_point_coverage: float
    mean_point_coverage: float
    overall_coverage_ratio: float
    max_gap_seconds: float
    worst_cell_gap_seconds: float
    revisit_mean_seconds: float
    revisit_median_seconds: float
    continuous_24_7_feasible: bool
    mission_objective_met: bool


class DesignOrbitResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommended_architecture: Optional[RecommendedArchitectureResponse] = None
    top_candidates: List[TopCandidateResponse]
    feasibility_summary: FeasibilitySummaryResponse
    coverage_metrics: Optional[CoverageMetricsResponse] = None
    explanation: List[str]
