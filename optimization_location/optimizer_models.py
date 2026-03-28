"""Structured results for orbit/constellation design optimization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Tuple

from candidate_models import WalkerConstellationCandidate
from coverage_service import CoverageMetrics
from request_models import OrbitFamily

PropagationModel = Literal["two_body_kepler", "j2_mean_secular"]
EarthRotationModel = Literal["simple_spin", "vallado_gmst"]


@dataclass(frozen=True)
class DesignerParams:
    """
    Explicit simulation / region resolution.

    All fields must be supplied by the caller or a declared scenario file — no operational
    defaults are invented here.
    """

    grid_spacing_m: float
    simulation_time_step_seconds: float
    region_circle_vertices: int
    """Vertices for geodesic circle→polygon when ``region`` is point+radius (>= 8)."""
    early_stop_on_first_feasible_minimum_t: bool
    """
    When ``True`` and continuous coverage is required, stop after the first feasible
    candidate in T-sorted order (minimum satellite count among enumerated candidates).
    """
    footprint_solid_angle_packing_factor: float
    """
    Strictly > 1.0. Scales the conservative solid-angle lower bound used in footprint pruning.
    """
    top_candidates_limit: int
    """Number of ranked candidates to expose (>= 1)."""
    grid_include_boundary: bool
    """If True, include polygon boundary in ground grid; if False, strict interior only."""
    propagation_model: PropagationModel = "j2_mean_secular"
    """
    ``two_body_kepler``: fixed mean elements; ``j2_mean_secular``: J2 secular rates on
    ``Ω``, ``ω``, and mean anomaly (first-order mean-element theory).
    """
    earth_rotation_model: EarthRotationModel = "vallado_gmst"
    """``simple_spin``: ``ω_earth * t``; ``vallado_gmst``: truncated GMST from Julian date."""

    def __post_init__(self) -> None:
        if self.region_circle_vertices < 8:
            raise ValueError("region_circle_vertices must be >= 8 for a stable circle polygon.")
        if self.footprint_solid_angle_packing_factor <= 1.0:
            raise ValueError("footprint_solid_angle_packing_factor must be > 1.0.")
        if self.top_candidates_limit < 1:
            raise ValueError("top_candidates_limit must be >= 1.")
        if self.grid_spacing_m <= 0.0:
            raise ValueError("grid_spacing_m must be positive.")
        if self.simulation_time_step_seconds <= 0.0:
            raise ValueError("simulation_time_step_seconds must be positive.")


@dataclass(frozen=True)
class CandidateEvaluation:
    """Outcome of evaluating one Walker candidate (simulation or prune)."""

    candidate: WalkerConstellationCandidate
    pruned: bool
    prune_reason: Optional[str]
    metrics: Optional[CoverageMetrics]
    feasible: bool
    """Meets hard continuous-coverage constraint when required; else simulation succeeded."""
    infeasibility_reason: Optional[str]


@dataclass(frozen=True)
class RankedRecommendation:
    """Best-ranked feasible candidate with scores used for ordering."""

    orbit_family: OrbitFamily
    altitude_km: float
    inclination_deg: float
    total_satellites_T: int
    planes_P: int
    phase_F: int
    metrics: CoverageMetrics
    cost_score: float
    complexity_score: float
    candidate: WalkerConstellationCandidate = field(repr=False)


@dataclass(frozen=True)
class DesignResult:
    """Full designer output: recommendation, rejections, and narrative explanations."""

    continuous_coverage_required: bool
    recommended: Optional[RankedRecommendation]
    evaluations: Tuple[CandidateEvaluation, ...]
    explanations: Tuple[str, ...]
