"""
Coverage feasibility against mission objectives (strict vs high-availability targets).
"""

from __future__ import annotations

from typing import Optional

from coverage_service import CoverageMetrics
from request_models import ContinuousCoverageStrategy, MissionSpec


def mission_coverage_feasible(metrics: CoverageMetrics, mission: MissionSpec) -> bool:
    """
    Whether ``metrics`` satisfies the mission's coverage rules when continuous service is required.

    ``strict_24_7`` → ``metrics.continuous_24_7_feasible``.
    ``high_availability`` → per-point floor and optional worst-cell gap ceiling.
    """
    if not mission.continuous_coverage_required:
        return True
    if mission.continuous_coverage_strategy == ContinuousCoverageStrategy.STRICT_24_7:
        return metrics.continuous_24_7_feasible
    return _high_availability_feasible(metrics, mission)


def _high_availability_feasible(metrics: CoverageMetrics, mission: MissionSpec) -> bool:
    if metrics.min_point_coverage < mission.target_min_point_coverage:
        return False
    cap = mission.target_max_worst_cell_gap_seconds
    if cap is not None and metrics.worst_cell_gap_seconds > cap:
        return False
    return True


def mission_infeasibility_reason(metrics: CoverageMetrics, mission: MissionSpec) -> Optional[str]:
    """Human-readable reason when ``mission_coverage_feasible`` is false."""
    if not mission.continuous_coverage_required:
        return None
    if mission.continuous_coverage_strategy == ContinuousCoverageStrategy.STRICT_24_7:
        if metrics.continuous_24_7_feasible:
            return None
        return "Continuous 24/7 coverage not satisfied (not all grid points visible at all time steps)."
    if metrics.min_point_coverage < mission.target_min_point_coverage:
        return (
            f"High-availability target not met: min_point_coverage={metrics.min_point_coverage:.6f} "
            f"< target {mission.target_min_point_coverage}."
        )
    cap = mission.target_max_worst_cell_gap_seconds
    if cap is not None and metrics.worst_cell_gap_seconds > cap:
        return (
            f"High-availability target not met: worst_cell_gap={metrics.worst_cell_gap_seconds:.1f}s "
            f"> cap {cap:.1f}s."
        )
    return None


def mission_objective_met(metrics: CoverageMetrics, mission: MissionSpec) -> bool:
    """
    Same predicate as ``mission_coverage_feasible`` for continuous missions; always True
    when continuous coverage is not required (metrics still describe simulated coverage).
    """
    if not mission.continuous_coverage_required:
        return True
    return mission_coverage_feasible(metrics, mission)
