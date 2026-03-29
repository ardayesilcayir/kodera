"""
ORBITA-R — Reposition Optimizer
=================================
Central orchestrator for the satellite repositioning optimization pipeline.

This is the main entry point. It:
  1. Generates candidate target orbits
  2. Computes transfer costs for each candidate
  3. Evaluates coverage metrics
  4. Analyzes system-level interactions
  5. Assesses risks
  6. Scores and ranks candidates
  7. Generates explanations with confidence and limitations
  8. Returns the top plans

Scoring formula:
  final_score =
      w1 * coverage_gain
    + w2 * continuity_score
    + w3 * gap_reduction
    + w4 * strategic_fit_score
    - w5 * transfer_cost_score
    - w6 * normalized_transfer_time
    - w7 * overlap_penalty
    - w8 * risk_score
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .satellite_models import (
    OrbitalState, Satellite, MissionConstraints, TransferSummary,
    CoverageMetrics, SystemImpactAnalysis, RiskAnalysis,
    RepositionPlan, RepositionResult,
    hohmann_delta_v, hohmann_transfer_time, inclination_change_delta_v,
    combined_plane_change_delta_v, orbital_velocity,
)
from .simulation_state import SimulationState
from .target_region import TargetRegion
from .orbit_candidate_generator import generate_candidates
from .coverage_engine import compute_full_coverage
from .system_interaction_analysis import compute_system_interaction
from .risk_engine import compute_total_risk
from .explanation_engine import (
    generate_plan_explanation, generate_comparison_explanation,
    generate_limitation_notes,
)
from .confidence_engine import (
    compute_feasibility_score, compute_confidence_score,
)


# ──────────────────────────────────────────────
# Weight Profiles
# ──────────────────────────────────────────────

WEIGHT_PROFILES: Dict[str, Dict[str, float]] = {
    "balanced": {
        "w1_coverage_gain": 0.20,
        "w2_continuity": 0.10,
        "w3_gap_reduction": 0.15,
        "w4_strategic_fit": 0.15,
        "w5_transfer_cost": 0.15,
        "w6_transfer_time": 0.05,
        "w7_overlap_penalty": 0.10,
        "w8_risk_score": 0.10,
    },
    "efficiency": {
        "w1_coverage_gain": 0.10,
        "w2_continuity": 0.10,
        "w3_gap_reduction": 0.10,
        "w4_strategic_fit": 0.10,
        "w5_transfer_cost": 0.25,
        "w6_transfer_time": 0.10,
        "w7_overlap_penalty": 0.15,
        "w8_risk_score": 0.10,
    },
    "coverage": {
        "w1_coverage_gain": 0.30,
        "w2_continuity": 0.15,
        "w3_gap_reduction": 0.20,
        "w4_strategic_fit": 0.15,
        "w5_transfer_cost": 0.05,
        "w6_transfer_time": 0.05,
        "w7_overlap_penalty": 0.05,
        "w8_risk_score": 0.05,
    },
    "speed": {
        "w1_coverage_gain": 0.15,
        "w2_continuity": 0.05,
        "w3_gap_reduction": 0.10,
        "w4_strategic_fit": 0.10,
        "w5_transfer_cost": 0.15,
        "w6_transfer_time": 0.25,
        "w7_overlap_penalty": 0.10,
        "w8_risk_score": 0.10,
    },
}


# ──────────────────────────────────────────────
# Transfer Cost Computation
# ──────────────────────────────────────────────

def compute_transfer_cost(
    current_orbit: OrbitalState,
    target_orbit: OrbitalState,
) -> TransferSummary:
    """
    Compute the transfer cost between two circular orbits.

    Components:
      1. Hohmann transfer Δv for altitude change
      2. Plane change Δv for inclination change
      3. RAAN change cost (modeled as a normalized penalty in Mode A)

    The total Δv is the vector sum approximation (not simple addition,
    since combined maneuvers can be more efficient).

    Returns:
        TransferSummary with all cost metrics.
    """
    alt_change = abs(target_orbit.altitude_km - current_orbit.altitude_km)
    inc_change = abs(target_orbit.inclination_deg - current_orbit.inclination_deg)
    raan_change = abs(target_orbit.raan_deg - current_orbit.raan_deg)
    if raan_change > 180:
        raan_change = 360 - raan_change

    # 1. Hohmann Δv for altitude change
    if alt_change > 0.1:
        _, _, dv_alt = hohmann_delta_v(
            current_orbit.altitude_km, target_orbit.altitude_km
        )
    else:
        dv_alt = 0.0

    # 2. Inclination change Δv
    # Perform at the higher altitude (more efficient)
    maneuver_alt = max(current_orbit.altitude_km, target_orbit.altitude_km)
    if inc_change > 0.01:
        dv_inc = inclination_change_delta_v(maneuver_alt, inc_change)
    else:
        dv_inc = 0.0

    # 3. Combined Δv estimation
    # If performing both altitude and plane changes, a combined maneuver
    # is more efficient. We model this as sqrt(dv_alt² + dv_inc²) for
    # the worst case, with a 10% efficiency bonus for combined execution.
    if dv_alt > 0 and dv_inc > 0:
        dv_total = math.sqrt(dv_alt ** 2 + dv_inc ** 2) * 0.9  # Combined efficiency
    else:
        dv_total = dv_alt + dv_inc

    # 4. RAAN cost score (Mode A: no direct thrust, penalize proportionally)
    raan_cost_score = raan_change / 180.0  # [0, 1]

    # 5. Transfer time
    if alt_change > 0.1:
        transfer_time_s = hohmann_transfer_time(
            current_orbit.altitude_km, target_orbit.altitude_km
        )
    else:
        # For pure plane changes, estimate time as a fraction of orbit period
        from .satellite_models import orbital_period
        transfer_time_s = orbital_period(current_orbit.altitude_km) * 0.5

    # Add time for RAAN drift (Mode A: very rough estimate)
    # In reality, J2 drift rate depends on altitude and inclination
    # Typical LEO RAAN drift: ~0.5-1.0 °/day
    if raan_change > 5.0:
        raan_drift_rate = 0.8  # deg/day (conservative LEO estimate)
        raan_drift_time_s = (raan_change / raan_drift_rate) * 86400.0
        transfer_time_s += raan_drift_time_s * 0.1  # Partial credit (we may thrust)

    transfer_time_h = transfer_time_s / 3600.0

    # 6. Normalized transfer cost score [0, 1]
    # Normalize Δv: 0.5 km/s = moderate, 2.0 km/s = very high for LEO
    dv_normalized = min(dv_total / 2.0, 1.0)
    # Include RAAN cost
    transfer_cost_score = 0.7 * dv_normalized + 0.3 * raan_cost_score
    transfer_cost_score = max(0.0, min(1.0, transfer_cost_score))

    return TransferSummary(
        delta_v_altitude_km_s=round(dv_alt, 6),
        delta_v_inclination_km_s=round(dv_inc, 6),
        delta_v_total_km_s=round(dv_total, 6),
        transfer_time_seconds=round(transfer_time_s, 2),
        transfer_time_hours=round(transfer_time_h, 4),
        transfer_cost_score=round(transfer_cost_score, 4),
        altitude_change_km=round(alt_change, 2),
        inclination_change_deg=round(inc_change, 4),
        raan_change_deg=round(raan_change, 4),
        raan_cost_score=round(raan_cost_score, 4),
    )


# ──────────────────────────────────────────────
# Scoring
# ──────────────────────────────────────────────

def normalize_transfer_time(hours: float, max_hours: float) -> float:
    """Normalize transfer time to [0, 1] based on maximum allowed."""
    if max_hours <= 0:
        return 1.0
    return min(hours / max_hours, 1.0)


def compute_final_score(
    coverage: CoverageMetrics,
    system_impact: SystemImpactAnalysis,
    risk: RiskAnalysis,
    transfer: TransferSummary,
    max_transfer_hours: float,
    weights: Dict[str, float],
) -> Tuple[float, Dict[str, float]]:
    """
    Compute the weighted final score for a candidate plan.

    final_score =
        + w1 * coverage_gain
        + w2 * continuity_score
        + w3 * gap_reduction
        + w4 * strategic_fit_score
        - w5 * transfer_cost_score
        - w6 * normalized_transfer_time
        - w7 * overlap_penalty
        - w8 * risk_score

    The score can range from approximately [-1, 1] but is typically
    clamped to [0, 1] for interpretability.

    Returns:
        Tuple of (Final score, Score breakdown dict). Higher score is better.
    """
    # Clamp coverage_gain from [-1, 1] to [0, 1] for scoring
    # Negative coverage gain still contributes negatively through the weight
    cov_gain = max(0.0, coverage.coverage_gain)

    norm_time = normalize_transfer_time(transfer.transfer_time_hours, max_transfer_hours)

    score = (
        weights["w1_coverage_gain"] * cov_gain
        + weights["w2_continuity"] * coverage.continuity_score
        + weights["w3_gap_reduction"] * system_impact.gap_reduction
        + weights["w4_strategic_fit"] * system_impact.strategic_fit_score
        - weights["w5_transfer_cost"] * transfer.transfer_cost_score
        - weights["w6_transfer_time"] * norm_time
        - weights["w7_overlap_penalty"] * system_impact.overlap_penalty
        - weights["w8_risk_score"] * risk.total_risk_score
    )

    # Normalize to [0, 1] range — shift and scale
    # Theoretical range is approximately [-sum(negative weights), +sum(positive weights)]
    # For balanced weights: [-0.40, +0.60]
    # We shift to make 0 = worst plausible, 1 = best plausible
    score_shifted = (score + 0.40) / 1.00  # Shift and normalize
    final = max(0.0, min(1.0, score_shifted))
    
    breakdown = {
        "coverage_score": round(cov_gain, 4),
        "transfer_cost_penalty": round(transfer.transfer_cost_score, 4),
        "time_penalty": round(norm_time, 4),
        "risk_penalty": round(risk.total_risk_score, 4)
    }
    
    return final, breakdown


# ──────────────────────────────────────────────
# Candidate Evaluation
# ──────────────────────────────────────────────

@dataclass
class ScoredCandidate:
    """Internal structure for a scored candidate orbit."""
    target_orbit: OrbitalState
    transfer_summary: TransferSummary
    coverage_metrics: CoverageMetrics
    system_impact: SystemImpactAnalysis
    risk_analysis: RiskAnalysis
    feasibility_score: float
    final_score: float
    score_breakdown: Dict[str, float]
    violated_constraints: List[str]


def evaluate_candidate(
    satellite: Satellite,
    candidate_orbit: OrbitalState,
    sim_state: SimulationState,
    region: TargetRegion,
    mission_type: str,
    constraints: MissionConstraints,
    weights: Dict[str, float],
) -> ScoredCandidate:
    """
    Evaluate a single candidate orbit: compute all metrics and score it.

    Args:
        satellite: The satellite being repositioned.
        candidate_orbit: The proposed target orbit.
        sim_state: Current simulation state.
        region: Target region.
        mission_type: Mission type.
        constraints: Mission constraints.
        weights: Weight profile for scoring.

    Returns:
        ScoredCandidate with all metrics and final score.
    """
    other_sats = sim_state.get_other_satellites(satellite.id)

    # 1. Transfer cost
    transfer = compute_transfer_cost(satellite.current_orbit, candidate_orbit)

    # 2. Coverage metrics
    coverage_result = compute_full_coverage(
        satellite.current_orbit,
        candidate_orbit,
        region,
        constraints.min_elevation_deg,
        mission_type,
    )
    coverage = CoverageMetrics(
        target_region_coverage=coverage_result.target_coverage,
        coverage_gain=coverage_result.coverage_gain,
        continuity_score=coverage_result.continuity_score,
        revisit_score=coverage_result.revisit_score,
    )

    # 3. System interaction
    sys_interaction = compute_system_interaction(
        candidate_orbit, other_sats, region, mission_type,
        constraints.min_elevation_deg,
    )
    system_impact = SystemImpactAnalysis(
        redundancy_score=sys_interaction.redundancy_score,
        overlap_penalty=sys_interaction.overlap_penalty,
        gap_reduction=sys_interaction.gap_reduction,
        strategic_fit_score=sys_interaction.strategic_fit_score,
        constellation_balance=sys_interaction.constellation_balance,
    )

    # 4. Risk analysis
    risk_dict = compute_total_risk(candidate_orbit, satellite, sim_state, transfer)
    risk = RiskAnalysis(
        zone_risk=risk_dict["zone_risk"],
        proximity_risk=risk_dict["proximity_risk"],
        satellite_risk=risk_dict["satellite_risk"],
        transfer_risk=risk_dict["transfer_risk"],
        total_risk_score=risk_dict["total_risk_score"],
        risk_factors=risk_dict["risk_factors"],
    )

    # 5. Feasibility
    feasibility = compute_feasibility_score(satellite, transfer, constraints)

    # Final score
    final_score, breakdown = compute_final_score(
        coverage, system_impact, risk, transfer,
        constraints.max_transfer_time_hours, weights,
    )

    # Violated constraints
    violations = []
    if transfer.transfer_time_hours > constraints.max_transfer_time_hours:
        violations.append("max_transfer_time_hours")
    if transfer.transfer_cost_score > constraints.max_orbit_change_score:
        violations.append("max_orbit_change_score")
    if satellite.capabilities.fuel_or_budget_score <= 0.4 and transfer.delta_v_total_km_s > 1.0:
        violations.append("fuel_budget_limit")

    return ScoredCandidate(
        target_orbit=candidate_orbit,
        transfer_summary=transfer,
        coverage_metrics=coverage,
        system_impact=system_impact,
        risk_analysis=risk,
        feasibility_score=feasibility,
        final_score=final_score,
        score_breakdown=breakdown,
        violated_constraints=violations,
    )


# ──────────────────────────────────────────────
# Main Optimization Entry Point
# ──────────────────────────────────────────────

def optimize_reposition(
    satellite: Satellite,
    target_region: TargetRegion,
    mission_type: str,
    sim_state: SimulationState,
    constraints: MissionConstraints,
    max_candidates: int = 75,
    top_n: int = 3,
) -> RepositionResult:
    """
    Main optimization entry point.

    Pipeline:
      1. Generate candidate target orbits
      2. Evaluate each candidate (coverage, system impact, risk, cost)
      3. Score and rank candidates
      4. Select top N plans
      5. Generate explanations with confidence and limitations
      6. Return structured result

    Args:
        satellite: The satellite to reposition.
        target_region: The target region to serve.
        mission_type: "communication" | "observation" | "emergency" | "balanced".
        sim_state: Current simulation state.
        constraints: Mission constraints.
        max_candidates: Maximum number of candidates to evaluate.
        top_n: Number of top plans to return.

    Returns:
        RepositionResult with best plan, alternatives, and metadata.
    """
    # Select weight profile
    weights = WEIGHT_PROFILES.get(constraints.optimization_mode, WEIGHT_PROFILES["balanced"])

    # Step 1: Generate candidates
    candidates = generate_candidates(
        target_region, mission_type, constraints,
        current_orbit=satellite.current_orbit,
        max_candidates=max_candidates,
    )

    if not candidates:
        # No candidates — return a failure result
        return _create_failure_result(satellite, constraints)

    # Step 2 & 3: Evaluate and score each candidate
    scored: List[ScoredCandidate] = []
    for candidate_orbit in candidates:
        sc = evaluate_candidate(
            satellite, candidate_orbit, sim_state,
            target_region, mission_type, constraints, weights,
        )
        scored.append(sc)

    # Step 4: Sort by final score (descending) and select top N
    scored.sort(key=lambda x: x.final_score, reverse=True)
    top_candidates = scored[:top_n]

    # Find best feasible candidate (feasibility >= 0.20)
    best_feasible_sc = None
    for sc in scored:
        if sc.feasibility_score >= 0.20:
            best_feasible_sc = sc
            break

    if best_feasible_sc is not None and best_feasible_sc not in top_candidates:
        top_candidates.append(best_feasible_sc)

    # Step 5: Build RepositionPlan for each top candidate
    limitations = generate_limitation_notes("MODE_A")
    other_sat_count = len(sim_state.get_other_satellites(satellite.id))

    plans: List[RepositionPlan] = []
    for rank_idx, sc in enumerate(top_candidates):
        status = "ACCEPTABLE"
        if sc.feasibility_score < 0.20:
            status = "NOT_RECOMMENDED"
        elif sc.feasibility_score < 0.50:
            status = "HIGH_RISK"

        plan = RepositionPlan(
            rank=rank_idx + 1,
            target_orbit=sc.target_orbit,
            transfer_summary=sc.transfer_summary,
            coverage_metrics=sc.coverage_metrics,
            system_impact=sc.system_impact,
            risk_analysis=sc.risk_analysis,
            explanation="",  # Will be filled below
            confidence_score=0.0,  # Will be computed below
            feasibility_score=sc.feasibility_score,
            limitations=limitations,
            final_score=sc.final_score,
            score_breakdown=sc.score_breakdown,
            operational_status=status,
            violated_constraints=sc.violated_constraints,
        )

        # Compute confidence FIRST (needs the plan object)
        plan.confidence_score = compute_confidence_score(plan, sim_state, "MODE_A")

        # Generate explanation using the computed confidence score
        plan.explanation = generate_plan_explanation(
            plan, satellite, mission_type, other_sat_count,
        )

        plans.append(plan)

    # Step 6: Build comparison summary
    comparison = generate_comparison_explanation(plans)

    best_plan = plans[0]
    alternatives = plans[1:] if len(plans) > 1 else []

    best_feasible_plan = None
    if best_feasible_sc is not None:
        for p in plans:
            if id(p.target_orbit) == id(best_feasible_sc.target_orbit):
                best_feasible_plan = p
                break

    summary = (
        f"Evaluated {len(candidates)} candidate orbits. "
        f"Selected top {len(plans)} plans. "
        f"Best plan: altitude {best_plan.target_orbit.altitude_km:.1f} km, "
        f"inclination {best_plan.target_orbit.inclination_deg:.1f} deg, "
        f"final score {best_plan.final_score:.4f}. "
        f"Optimization mode: {constraints.optimization_mode}."
    )

    return RepositionResult(
        best_plan=best_plan,
        alternative_plans=alternatives,
        total_candidates_evaluated=len(candidates),
        optimization_mode=constraints.optimization_mode,
        best_feasible_plan=best_feasible_plan,
        model_mode="MODE_A",
        summary=summary,
    )


def _create_failure_result(
    satellite: Satellite,
    constraints: MissionConstraints,
) -> RepositionResult:
    """Create a RepositionResult for the case where no candidates could be generated."""
    dummy_orbit = satellite.current_orbit
    dummy_transfer = TransferSummary(
        delta_v_altitude_km_s=0, delta_v_inclination_km_s=0,
        delta_v_total_km_s=0, transfer_time_seconds=0,
        transfer_time_hours=0, transfer_cost_score=0,
        altitude_change_km=0, inclination_change_deg=0,
        raan_change_deg=0, raan_cost_score=0,
    )
    dummy_coverage = CoverageMetrics(
        target_region_coverage=0, coverage_gain=0,
        continuity_score=0, revisit_score=0,
    )
    dummy_system = SystemImpactAnalysis(
        redundancy_score=0, overlap_penalty=0,
        gap_reduction=0, strategic_fit_score=0, constellation_balance=0,
    )
    dummy_risk = RiskAnalysis(
        zone_risk=0, proximity_risk=0, satellite_risk=0,
        transfer_risk=0, total_risk_score=1.0,
        risk_factors=["No feasible candidates could be generated."],
    )

    plan = RepositionPlan(
        rank=1,
        target_orbit=dummy_orbit,
        transfer_summary=dummy_transfer,
        coverage_metrics=dummy_coverage,
        system_impact=dummy_system,
        risk_analysis=dummy_risk,
        explanation=(
            "No feasible candidate orbits could be generated for the given "
            "target region, mission type, and constraints. Consider relaxing "
            "constraints or evaluating a different satellite."
        ),
        confidence_score=0.0,
        feasibility_score=0.0,
        limitations=generate_limitation_notes("MODE_A"),
        final_score=0.0,
    )

    return RepositionResult(
        best_plan=plan,
        alternative_plans=[],
        total_candidates_evaluated=0,
        optimization_mode=constraints.optimization_mode,
        model_mode="MODE_A",
        summary="No feasible candidates generated.",
    )
