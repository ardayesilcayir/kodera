"""
Deterministic ranking and human-readable explanations for constellation design results.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from candidate_scoring import complexity_score, cost_score
from optimization_ranking import sort_evaluations_for_best
from optimizer_models import CandidateEvaluation, RankedRecommendation
from request_models import MissionSpec, OptimizationSpec


def rank_and_select_best(
    evaluations: Tuple[CandidateEvaluation, ...],
    *,
    optimization: OptimizationSpec,
) -> Optional[RankedRecommendation]:
    """
    Rank feasible (non-pruned) candidates using ``optimization.primary_goal`` tie-break
    lexicography (see ``optimization_ranking``).

    Eligibility uses ``e.feasible`` only (set by the optimizer from mission coverage rules).
    """
    pool: List[CandidateEvaluation] = []
    for e in evaluations:
        if e.pruned or e.metrics is None:
            continue
        if not e.feasible:
            continue
        pool.append(e)

    if not pool:
        return None

    sort_evaluations_for_best(pool, optimization)
    best = pool[0]
    m = best.metrics
    assert m is not None
    c = best.candidate
    return RankedRecommendation(
        orbit_family=c.family,
        altitude_km=c.altitude_km,
        inclination_deg=c.inclination_deg,
        total_satellites_T=c.total_satellites_T,
        planes_P=c.planes_P,
        phase_F=c.phase_F,
        metrics=m,
        cost_score=cost_score(c),
        complexity_score=complexity_score(c),
        candidate=c,
    )


def list_top_candidate_evaluations(
    evaluations: Tuple[CandidateEvaluation, ...],
    *,
    continuous_coverage_required: bool,
    limit: int,
    optimization: OptimizationSpec,
) -> List[CandidateEvaluation]:
    """
    Top ``limit`` candidates for API display: feasible pool first (same sort as
    ``rank_and_select_best``). If none and continuous coverage was required, fall back to
    best simulated by mean point coverage (all rows ``feasible: false``).
    """
    feasible: List[CandidateEvaluation] = []
    for e in evaluations:
        if e.pruned or e.metrics is None:
            continue
        if not e.feasible:
            continue
        feasible.append(e)

    if feasible:
        sort_evaluations_for_best(feasible, optimization)
        return feasible[:limit]

    if not continuous_coverage_required:
        return []

    pool = [e for e in evaluations if not e.pruned and e.metrics is not None]
    pool.sort(key=lambda e: e.metrics.mean_point_coverage, reverse=True)
    return pool[:limit]


def build_explanations(
    recommended: Optional[RankedRecommendation],
    evaluations: Tuple[CandidateEvaluation, ...],
    *,
    continuous_coverage_required: bool,
    mission: MissionSpec | None = None,
) -> Tuple[str, ...]:
    """Narrative trace: pruning, infeasibility, and winner rationale."""
    lines: List[str] = []

    pruned = [e for e in evaluations if e.pruned]
    sim_infeasible = [
        e
        for e in evaluations
        if not e.pruned and e.metrics is not None and continuous_coverage_required and not e.feasible
    ]

    cov_line = (
        f"Coverage objective: strategy={mission.continuous_coverage_strategy.value}, "
        f"target_min_point_coverage={mission.target_min_point_coverage}."
        if mission is not None and continuous_coverage_required
        else ""
    )
    if cov_line:
        lines.append(cov_line)

    lines.append(
        f"Evaluated {len(evaluations)} constellation candidates "
        f"({len(pruned)} footprint-pruned before simulation, "
        f"{len(sim_infeasible)} failed mission coverage rules after simulation)."
    )

    if pruned:
        lines.append("Footprint pruning removed candidates that cannot cover the region solid angle with T satellites (conservative cap packing bound).")
        for e in pruned[:12]:
            lines.append(
                f"Pruned: family={e.candidate.family.value} T={e.candidate.total_satellites_T} "
                f"P={e.candidate.planes_P} F={e.candidate.phase_F} alt={e.candidate.altitude_km:.1f} km — {e.prune_reason}"
            )
        if len(pruned) > 12:
            lines.append(f"... {len(pruned) - 12} additional pruned candidates omitted.")

    for e in sim_infeasible[:12]:
        lines.append(
            f"Rejected (continuous coverage): family={e.candidate.family.value} T={e.candidate.total_satellites_T} "
            f"min_point_coverage={e.metrics.min_point_coverage:.4f} worst_cell_gap_s={e.metrics.worst_cell_gap_seconds:.1f}"
        )
    if len(sim_infeasible) > 12:
        lines.append(f"... {len(sim_infeasible) - 12} additional rejected candidates omitted.")

    if recommended is None:
        lines.append(
            "No recommendation: no candidate satisfied the feasibility rules for this run."
        )
        return tuple(lines)

    r = recommended
    lines.append(
        f"Selected: {r.orbit_family.value} at {r.altitude_km:.1f} km, i={r.inclination_deg:.2f}°, "
        f"Walker T={r.total_satellites_T} P={r.planes_P} F={r.phase_F}."
    )
    lines.append(
        f"Ranking keys: T={r.total_satellites_T}, worst_cell_gap={r.metrics.worst_cell_gap_seconds:.3f} s, "
        f"cost_score={r.cost_score:.4f}, complexity_score={r.complexity_score:.4f}."
    )
    lines.append(
        f"Coverage: min_point={r.metrics.min_point_coverage:.6f}, mean_point={r.metrics.mean_point_coverage:.6f}, "
        f"overall={r.metrics.overall_coverage_ratio:.6f}, continuous_24_7_feasible={r.metrics.continuous_24_7_feasible}."
    )
    return tuple(lines)
