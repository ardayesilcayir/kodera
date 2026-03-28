"""
ORBITA-R -- Explanation Engine
==============================
Generates human-readable technical explanations for repositioning plans.

Critical rule:
  - NEVER claim certainty or guarantee correctness.
  - Always frame results as "highest-scoring under current model and state."
  - Always include model assumptions and limitations.
"""

from __future__ import annotations

from typing import List, Optional

from satellite_models import (
    OrbitalState, Satellite, RepositionPlan, TransferSummary,
    CoverageMetrics, SystemImpactAnalysis, RiskAnalysis,
)


# ──────────────────────────────────────────────
# Model Disclaimers
# ──────────────────────────────────────────────

MODE_A_ASSUMPTIONS = [
    "Circular orbit approximation (eccentricity ~ 0)",
    "Two-body dynamics only (no J2, drag, or third-body perturbations)",
    "Impulsive burns (instantaneous velocity changes)",
    "Spherical Earth for ground track projection",
    "No atmospheric drag during transfer",
    "No RAAN drift from J2 precession",
    "Simplified RAAN change cost model",
    "Constant satellite capabilities during transfer",
]

MODE_A_LIMITATIONS = [
    "Results are valid under Mode A (fast scientific approximation) assumptions only.",
    "Actual delta-v requirements may differ due to perturbations not modeled in Mode A.",
    "Transfer time estimates assume impulsive burns; low-thrust transfers will take longer.",
    "Coverage analysis uses discrete ground track sampling; continuous coverage may differ slightly.",
    "Risk assessment is a proxy -- detailed conjunction analysis requires higher-fidelity propagation.",
    "RAAN change costs are approximated; exact costs depend on the specific maneuver strategy.",
    "Confidence score reflects model-level uncertainty, not operational certainty.",
]


# ──────────────────────────────────────────────
# Plan Explanation
# ──────────────────────────────────────────────

def generate_plan_explanation(
    plan: RepositionPlan,
    satellite: Satellite,
    mission_type: str,
    other_satellite_count: int,
) -> str:
    """
    Generate a technical explanation for a repositioning plan.

    The explanation covers:
      - Why this orbit was selected
      - Transfer summary
      - Coverage impact
      - System-level impact
      - Risk assessment
      - Model caveats

    Args:
        plan: The repositioning plan to explain.
        satellite: The satellite being repositioned.
        mission_type: The mission type for context.
        other_satellite_count: Number of other active satellites.

    Returns:
        Human-readable explanation string.
    """
    t = plan.target_orbit
    ts = plan.transfer_summary
    cm = plan.coverage_metrics
    si = plan.system_impact
    ra = plan.risk_analysis

    lines = []

    # Header
    lines.append(f"=== Repositioning Plan (Rank #{plan.rank}) ===")
    lines.append("")

    # Recommendation framing (NEVER claim certainty)
    lines.append(
        "This recommendation is the highest-scoring plan under the current "
        "simulation state and physical model (Mode A). Results should be "
        "interpreted within the limits of the adopted model assumptions."
    )
    lines.append("")

    # Target orbit summary
    lines.append("--- Target Orbit ---")
    lines.append(f"  Altitude:     {t.altitude_km:.1f} km")
    lines.append(f"  Inclination:  {t.inclination_deg:.2f} deg")
    lines.append(f"  RAAN:         {t.raan_deg:.2f} deg")
    lines.append(f"  Phase:        {t.phase_deg:.2f} deg")
    lines.append(f"  Period:       {t.period_minutes:.1f} min")
    lines.append("")

    # Transfer summary
    lines.append("--- Transfer Summary ---")
    lines.append(f"  Altitude change:     {ts.altitude_change_km:.1f} km")
    lines.append(f"  Inclination change:  {ts.inclination_change_deg:.2f} deg")
    lines.append(f"  RAAN change:         {ts.raan_change_deg:.2f} deg")
    lines.append(f"  dv (altitude):       {ts.delta_v_altitude_km_s:.4f} km/s")
    lines.append(f"  dv (inclination):    {ts.delta_v_inclination_km_s:.4f} km/s")
    lines.append(f"  dv (total):          {ts.delta_v_total_km_s:.4f} km/s")
    lines.append(f"  Transfer time:       {ts.transfer_time_hours:.2f} hours")
    lines.append(f"  Transfer cost score: {ts.transfer_cost_score:.4f}")
    lines.append("")

    # Coverage impact
    lines.append("--- Coverage Impact ---")
    lines.append(f"  Target region coverage:  {cm.target_region_coverage:.2%}")
    lines.append(f"  Coverage gain:           {cm.coverage_gain:+.2%}")
    lines.append(f"  Continuity score:        {cm.continuity_score:.2%}")
    lines.append(f"  Revisit score:           {cm.revisit_score:.2%}")
    lines.append("")

    # System-level impact
    lines.append(f"--- System Impact (with {other_satellite_count} other active satellites) ---")
    lines.append(f"  Overlap penalty:         {si.overlap_penalty:.4f}")
    lines.append(f"  Redundancy score:        {si.redundancy_score:.4f}")
    lines.append(f"  Gap reduction:           {si.gap_reduction:.4f}")
    lines.append(f"  Strategic fit:           {si.strategic_fit_score:.4f}")
    lines.append(f"  Constellation balance:   {si.constellation_balance:.4f}")
    lines.append("")

    # Risk
    lines.append("--- Risk Assessment ---")
    lines.append(f"  Total risk score:  {ra.total_risk_score:.4f}")
    for factor in ra.risk_factors:
        lines.append(f"  - {factor}")
    lines.append("")

    # Scores
    lines.append("--- Scoring ---")
    lines.append(f"  Final score:       {plan.final_score:.4f}")
    lines.append(f"  Status:            {plan.operational_status}")
    lines.append(f"  Feasibility:       {plan.feasibility_score:.4f}")
    lines.append(f"  Confidence:        {plan.confidence_score:.4f}")
    lines.append("")

    # Score Breakdown
    lines.append("--- Score Breakdown ---")
    lines.append("  {")
    keys = list(plan.score_breakdown.keys())
    for i, key in enumerate(keys):
        val = plan.score_breakdown[key]
        comma = "," if i < len(keys) - 1 else ""
        lines.append(f"    \"{key}\": {val}{comma}")
    lines.append("  }")
    lines.append("")

    # Hard Constraint Violations
    if len(plan.violated_constraints) > 0:
        lines.append("--- Hard Constraint Violations ---")
        lines.append("  {")
        lines.append("    \"violated_constraints\": [")
        for i, v in enumerate(plan.violated_constraints):
            comma = "," if i < len(plan.violated_constraints) - 1 else ""
            lines.append(f"      \"{v}\"{comma}")
        lines.append("    ]")
        lines.append("  }")
        lines.append("")

    # Rationale
    lines.append("--- Rationale ---")
    rationale_parts = []

    if cm.coverage_gain > 0.1:
        rationale_parts.append(
            f"This orbit provides a {cm.coverage_gain:.1%} improvement in target coverage."
        )
    elif cm.coverage_gain > 0:
        rationale_parts.append("This orbit provides a modest coverage improvement.")
    else:
        rationale_parts.append(
            "This orbit does not significantly improve direct coverage, "
            "but may be selected for other strategic reasons."
        )

    if si.gap_reduction > 0.5:
        rationale_parts.append(
            f"Critically, it fills {si.gap_reduction:.0%} of currently uncovered areas."
        )

    if si.overlap_penalty > 0.5:
        rationale_parts.append(
            "Note: significant overlap with existing satellite coverage "
            "was detected, which reduces the efficiency of this repositioning."
        )

    if ts.delta_v_total_km_s < 0.1:
        rationale_parts.append(
            "The transfer delta-v is low, making this a fuel-efficient repositioning."
        )
    elif ts.delta_v_total_km_s > 1.0:
        rationale_parts.append(
            "Warning: the transfer requires a substantial delta-v budget. "
            "Verify fuel availability before execution."
        )

    if ts.raan_change_deg > 1.0:
        rationale_parts.append(
            f"Note: The required {ts.raan_change_deg:.1f} deg RAAN shift/plane alignment is NOT executed "
            f"via direct impulsive maneuvers. It relies on natural J2 nodal precession and drift phasing, "
            f"requiring approximately {ts.transfer_time_hours:.1f} hours of repositioning time under current constraints."
        )

    if ra.total_risk_score > 0.5:
        rationale_parts.append(
            "Elevated risk was identified -- review risk factors carefully."
        )

    for part in rationale_parts:
        lines.append(f"  {part}")
    lines.append("")

    # Model caveats
    lines.append("--- Model Caveats ---")
    lines.append("  Confidence score is computed based on model assumptions and state freshness.")
    lines.append("  This analysis uses Mode A (fast scientific approximation).")
    lines.append("  Key assumptions: " + "; ".join(MODE_A_ASSUMPTIONS[:3]) + ".")
    lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Comparison Explanation
# ──────────────────────────────────────────────

def generate_comparison_explanation(plans: List[RepositionPlan]) -> str:
    """
    Generate a comparative explanation across multiple plans.

    Args:
        plans: List of plans (sorted by rank).

    Returns:
        Comparison string.
    """
    if not plans:
        return "No plans to compare."

    lines = [
        "=== Plan Comparison ===",
        "",
        f"{'Rank':<6} {'Alt(km)':<10} {'Inc(deg)':<9} {'Score':<10} "
        f"{'Coverage':<10} {'Cost':<10} {'Risk':<10} {'Feasibility':<12}",
        "-" * 77,
    ]

    for plan in plans:
        lines.append(
            f"#{plan.rank:<5} {plan.target_orbit.altitude_km:<10.1f} "
            f"{plan.target_orbit.inclination_deg:<9.2f} {plan.final_score:<10.4f} "
            f"{plan.coverage_metrics.target_region_coverage:<10.2%} "
            f"{plan.transfer_summary.transfer_cost_score:<10.4f} "
            f"{plan.risk_analysis.total_risk_score:<10.4f} "
            f"{plan.feasibility_score:<12.4f}"
        )

    lines.append("")
    lines.append(
        "Note: Rankings reflect the weighted scoring under Mode A assumptions. "
        "Different optimization modes or weight profiles may yield different rankings."
    )

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Limitation Notes
# ──────────────────────────────────────────────

def generate_limitation_notes(model_mode: str = "MODE_A") -> List[str]:
    """
    Generate the list of limitations for the current model mode.

    Always returns at least one limitation — the system never claims perfection.

    Returns:
        List of limitation strings.
    """
    if model_mode == "MODE_A":
        return list(MODE_A_LIMITATIONS)

    # Future: MODE_B limitations
    return [
        "Results should be interpreted within the limits of the adopted model assumptions.",
        "Confidence score reflects statistical model-level uncertainty.",
    ]


def format_transfer_summary(ts: TransferSummary) -> str:
    """Format a TransferSummary as a human-readable string."""
    return (
        f"dv_total={ts.delta_v_total_km_s:.4f} km/s "
        f"(alt: {ts.delta_v_altitude_km_s:.4f}, inc: {ts.delta_v_inclination_km_s:.4f}), "
        f"time={ts.transfer_time_hours:.2f}h, "
        f"cost_score={ts.transfer_cost_score:.4f}"
    )


def format_coverage_summary(cm: CoverageMetrics) -> str:
    """Format CoverageMetrics as a human-readable string."""
    return (
        f"coverage={cm.target_region_coverage:.2%}, "
        f"gain={cm.coverage_gain:+.2%}, "
        f"continuity={cm.continuity_score:.2%}, "
        f"revisit={cm.revisit_score:.2%}"
    )
