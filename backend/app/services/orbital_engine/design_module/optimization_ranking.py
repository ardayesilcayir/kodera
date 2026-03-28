"""
Goal-aware deterministic ranking keys for evaluated constellation candidates.

Uses lexicographic-style tuples (primary objective first, then secondary tie-breakers).
"""

from __future__ import annotations

from typing import List, Tuple

from candidate_models import WalkerConstellationCandidate
from candidate_scoring import complexity_score, cost_score
from coverage_service import CoverageMetrics
from optimizer_models import CandidateEvaluation
from request_models import OptimizationSpec, PrimaryOptimizationGoal


def _base_ties(
    c: WalkerConstellationCandidate,
    m: CoverageMetrics,
) -> Tuple[float, float, float, float]:
    """Shared tie-breakers: satellite count, worst gap, cost, complexity."""
    return (
        float(c.total_satellites_T),
        float(m.worst_cell_gap_seconds),
        cost_score(c),
        complexity_score(c),
    )


def _sort_key_for_goal(
    e: CandidateEvaluation,
    primary: PrimaryOptimizationGoal,
) -> Tuple[float, ...]:
    c = e.candidate
    assert e.metrics is not None
    m = e.metrics

    if primary == PrimaryOptimizationGoal.MINIMIZE_SATELLITE_COUNT:
        return (
            float(c.total_satellites_T),
            float(m.worst_cell_gap_seconds),
            cost_score(c),
            complexity_score(c),
        )
    if primary == PrimaryOptimizationGoal.MINIMIZE_TOTAL_COST:
        return (
            cost_score(c),
            float(c.total_satellites_T),
            float(m.worst_cell_gap_seconds),
            complexity_score(c),
        )
    if primary == PrimaryOptimizationGoal.MAXIMIZE_COVERAGE_FRACTION:
        return (
            -float(m.min_point_coverage),
            -float(m.mean_point_coverage),
            float(m.worst_cell_gap_seconds),
            float(c.total_satellites_T),
        )
    if primary == PrimaryOptimizationGoal.MINIMIZE_MAX_GAP_DURATION:
        return (
            float(m.max_gap_seconds),
            float(m.worst_cell_gap_seconds),
            float(c.total_satellites_T),
            cost_score(c),
        )
    if primary == PrimaryOptimizationGoal.MINIMIZE_MEAN_RESPONSE_LATENCY:
        return (
            float(m.revisit_mean_seconds),
            float(m.revisit_median_seconds),
            float(m.worst_cell_gap_seconds),
            float(c.total_satellites_T),
        )
    return _base_ties(c, m)


def sort_evaluations_for_best(
    pool: List[CandidateEvaluation],
    optimization: OptimizationSpec,
) -> None:
    """Sort ``pool`` in-place: best first (lower tuple is better where applicable)."""
    primary = optimization.primary_goal
    pool.sort(key=lambda e: _sort_key_for_goal(e, primary))


