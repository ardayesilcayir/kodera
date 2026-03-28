"""Mission coverage rules."""

from __future__ import annotations

from coverage_objectives import mission_coverage_feasible, mission_objective_met
from coverage_service import CoverageMetrics
from request_models import ContinuousCoverageStrategy, MissionSpec, MissionType


def _m(
    *,
    min_pc: float,
    worst_gap: float,
    strict_ok: bool,
) -> CoverageMetrics:
    return CoverageMetrics(
        min_point_coverage=min_pc,
        mean_point_coverage=min_pc,
        overall_coverage_ratio=min_pc,
        max_gap_seconds=worst_gap,
        worst_cell_gap_seconds=worst_gap,
        revisit_mean_seconds=0.0,
        revisit_median_seconds=0.0,
        continuous_24_7_feasible=strict_ok,
    )


def test_high_availability_accepts_below_strict_threshold() -> None:
    mission = MissionSpec(
        type=MissionType.EMERGENCY_COMMS,
        continuous_coverage_required=True,
        analysis_horizon_hours=24.0,
        validation_horizon_days=7.0,
        continuous_coverage_strategy=ContinuousCoverageStrategy.HIGH_AVAILABILITY,
        target_min_point_coverage=0.99,
        target_max_worst_cell_gap_seconds=None,
    )
    metrics = _m(min_pc=0.995, worst_gap=60.0, strict_ok=False)
    assert mission_coverage_feasible(metrics, mission) is True
    assert mission_objective_met(metrics, mission) is True


def test_strict_24_7_requires_full_matrix() -> None:
    mission = MissionSpec(
        type=MissionType.EMERGENCY_COMMS,
        continuous_coverage_required=True,
        analysis_horizon_hours=24.0,
        validation_horizon_days=7.0,
        continuous_coverage_strategy=ContinuousCoverageStrategy.STRICT_24_7,
    )
    metrics = _m(min_pc=0.99999, worst_gap=0.0, strict_ok=False)
    assert mission_coverage_feasible(metrics, mission) is False
