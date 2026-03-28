"""Ranking rules: continuous 24/7 vs EO-style feasibility."""

from __future__ import annotations

from candidate_models import (
    CandidateGenerationInput,
    OrbitFamilySearchParams,
    WalkerTopologyGrid,
)
from coverage_service import CoverageMetrics
from orbit_family_service import generate_walker_candidates
from optimizer_models import CandidateEvaluation
from recommendation_service import rank_and_select_best
from request_models import MissionType, OptimizationSpec, OrbitFamily, PrimaryOptimizationGoal


def _sample_candidate():
    inp = CandidateGenerationInput(
        mission_type=MissionType.BALANCED,
        allowed_families=(OrbitFamily.LEO,),
        family_search=(
            OrbitFamilySearchParams(
                family=OrbitFamily.LEO,
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
        max_satellites=6,
        max_planes=3,
        epoch_seconds_tai=0.0,
    )
    return generate_walker_candidates(inp)[0]


def _metrics(continuous_ok: bool) -> CoverageMetrics:
    return CoverageMetrics(
        min_point_coverage=0.5,
        mean_point_coverage=0.6,
        overall_coverage_ratio=0.55,
        max_gap_seconds=100.0,
        worst_cell_gap_seconds=200.0,
        revisit_mean_seconds=50.0,
        revisit_median_seconds=40.0,
        continuous_24_7_feasible=continuous_ok,
    )


def _opt() -> OptimizationSpec:
    return OptimizationSpec(
        primary_goal=PrimaryOptimizationGoal.MINIMIZE_SATELLITE_COUNT,
        secondary_goals=[],
        allowed_orbit_families=[OrbitFamily.LEO],
        max_satellites=24,
        max_planes=6,
    )


def test_rank_and_select_best_ignores_infeasible_candidates() -> None:
    cand = _sample_candidate()
    bad = CandidateEvaluation(
        candidate=cand,
        pruned=False,
        prune_reason=None,
        metrics=_metrics(False),
        feasible=False,
        infeasibility_reason="coverage",
    )
    assert rank_and_select_best((bad,), optimization=_opt()) is None


def test_rank_and_select_best_accepts_feasible_pool() -> None:
    cand = _sample_candidate()
    good = CandidateEvaluation(
        candidate=cand,
        pruned=False,
        prune_reason=None,
        metrics=_metrics(True),
        feasible=True,
        infeasibility_reason=None,
    )
    rec = rank_and_select_best((good,), optimization=_opt())
    assert rec is not None
    assert rec.metrics.continuous_24_7_feasible is True
