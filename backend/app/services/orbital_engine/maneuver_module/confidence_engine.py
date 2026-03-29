"""
ORBITA-R — Confidence Engine
==============================
Computes feasibility and confidence scores for repositioning plans.

Feasibility: Can the satellite physically perform this transfer?
Confidence:  How reliable is our estimate given model assumptions and data quality?

Neither score should ever reach 1.0 — the system never claims perfection.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import List, Optional

from .satellite_models import (
    OrbitalState, Satellite, TransferSummary, MissionConstraints,
    RepositionPlan,
)
from .simulation_state import SimulationState


# ──────────────────────────────────────────────
# Feasibility Score
# ──────────────────────────────────────────────

def compute_feasibility_score(
    satellite: Satellite,
    transfer_summary: TransferSummary,
    constraints: MissionConstraints,
) -> float:
    """
    Compute whether the satellite can physically perform the proposed transfer.

    Checks:
      1. Fuel/budget: is Δv within the satellite's fuel capacity?
      2. Maneuver capacity: can the satellite execute this type of maneuver?
      3. Transfer time: is it within the allowed time window?
      4. Orbit change magnitude: is it within the max_orbit_change_score constraint?

    Each check produces a sub-score; the overall feasibility is the minimum
    (weakest link determines feasibility).

    Returns:
        Feasibility score [0.0, ~0.95]. Never reaches 1.0.
    """
    caps = satellite.capabilities

    # 1. Fuel check — compare transfer cost to fuel budget
    #    If cost > budget, feasibility drops sharply
    fuel_ratio = transfer_summary.transfer_cost_score / max(caps.fuel_or_budget_score, 0.01)
    if fuel_ratio <= 0.7:
        fuel_feasibility = 0.95
    elif fuel_ratio <= 1.0:
        fuel_feasibility = 0.95 - 0.5 * (fuel_ratio - 0.7) / 0.3
    elif fuel_ratio <= 1.5:
        fuel_feasibility = 0.45 - 0.35 * (fuel_ratio - 1.0) / 0.5
    else:
        fuel_feasibility = max(0.05, 0.1 - 0.05 * (fuel_ratio - 1.5))

    # 2. Maneuver capacity check
    #    Complex maneuvers (large plane changes) need higher capacity
    if transfer_summary.inclination_change_deg > 10.0:
        required_capacity = 0.7
    elif transfer_summary.inclination_change_deg > 5.0:
        required_capacity = 0.5
    else:
        required_capacity = 0.3

    if caps.maneuver_capacity_score >= required_capacity:
        maneuver_feasibility = 0.9
    else:
        maneuver_feasibility = max(0.1,
            0.9 * (caps.maneuver_capacity_score / required_capacity))

    # 3. Time check — is transfer within the allowed window?
    if transfer_summary.transfer_time_hours <= constraints.max_transfer_time_hours:
        time_ratio = transfer_summary.transfer_time_hours / constraints.max_transfer_time_hours
        time_feasibility = 0.95 - 0.3 * time_ratio ** 2
    else:
        # Over budget — feasibility drops
        overshoot = (transfer_summary.transfer_time_hours / constraints.max_transfer_time_hours) - 1.0
        time_feasibility = max(0.05, 0.65 - 0.6 * overshoot)

    # 4. Orbit change constraint check
    if transfer_summary.transfer_cost_score <= constraints.max_orbit_change_score:
        change_feasibility = 0.9
    else:
        overshoot = (
            transfer_summary.transfer_cost_score / constraints.max_orbit_change_score
        ) - 1.0
        change_feasibility = max(0.05, 0.9 - 0.8 * overshoot)

    # Overall: weakest link
    feasibility = min(
        fuel_feasibility,
        maneuver_feasibility,
        time_feasibility,
        change_feasibility,
    )

    # Cap at 0.95 — never claim perfect feasibility
    return max(0.0, min(0.95, feasibility))


# ──────────────────────────────────────────────
# Confidence Score
# ──────────────────────────────────────────────

def compute_confidence_score(
    plan: RepositionPlan,
    sim_state: SimulationState,
    model_mode: str = "MODE_A",
) -> float:
    """
    Compute confidence in the plan's predicted outcomes.

    Factors:
      1. Model fidelity: Mode A is less confident than Mode B
      2. Data freshness: is the simulation state recent?
      3. Data completeness: how many satellites are in the state?
      4. Plan feasibility: infeasible plans have lower confidence
      5. Score robustness: how sensitive is the score to small changes?

    Returns:
        Confidence score [0.0, ~0.90]. Never reaches 1.0 — the system
        never claims perfect confidence.
    """
    # 1. Model fidelity factor
    model_factor = {
        "MODE_A": 0.70,   # Fast approximation — moderate confidence
        "MODE_B": 0.85,   # Higher fidelity — higher confidence
    }.get(model_mode, 0.60)

    # 2. Data freshness factor
    data_freshness = compute_data_quality_factor(sim_state)

    # 3. Data completeness factor
    n_sats = len(sim_state.active_satellites)
    if n_sats >= 5:
        completeness_factor = 0.95
    elif n_sats >= 2:
        completeness_factor = 0.75 + 0.05 * n_sats
    else:
        completeness_factor = 0.60

    # 4. Feasibility-linked confidence
    # If the plan is barely feasible, we're less confident in predictions
    feas_factor = 0.5 + 0.5 * plan.feasibility_score

    # 5. Score stability proxy — if final_score is near 0 or near extremes,
    #    the model may be less confident
    score = plan.final_score
    if score < 0.1 or score > 0.95:
        stability_factor = 0.70
    elif 0.3 <= score <= 0.8:
        stability_factor = 0.90
    else:
        stability_factor = 0.80

    # Weighted combination
    confidence = (
        0.30 * model_factor +
        0.20 * data_freshness +
        0.15 * completeness_factor +
        0.20 * feas_factor +
        0.15 * stability_factor
    )

    # Hard cap at 0.90 — the system NEVER claims high confidence
    return max(0.05, min(0.90, confidence))


# ──────────────────────────────────────────────
# Data Quality
# ──────────────────────────────────────────────

def compute_data_quality_factor(sim_state: SimulationState) -> float:
    """
    Assess the quality and freshness of the simulation state data.

    Factors:
      - Historical state availability
      - Number of active satellites (more data = more reliable interactions)
      - Presence of region tasks (richer context)

    Returns:
        Data quality factor [0.0, 1.0].
    """
    score = 0.5  # Base score

    # Historical data availability
    if sim_state.historical_state_cache and len(sim_state.historical_state_cache) > 0:
        n_history = len(sim_state.historical_state_cache)
        score += min(0.2, 0.05 * n_history)  # Up to +0.20

    # Satellite count contribution
    n_sats = len(sim_state.active_satellites)
    score += min(0.15, 0.03 * n_sats)

    # Region task data
    if sim_state.region_tasks:
        score += 0.10

    # Risk zone data (having defined risk zones means better risk assessment)
    if sim_state.risk_zones or sim_state.degradation_zones:
        score += 0.05

    return min(score, 1.0)


# ──────────────────────────────────────────────
# Assumption Tracking
# ──────────────────────────────────────────────

def list_active_assumptions(model_mode: str = "MODE_A") -> List[str]:
    """
    List all active physical assumptions for the current model mode.

    This is used for transparency — the user should know exactly
    what assumptions underlie the results.

    Returns:
        List of assumption descriptions.
    """
    if model_mode == "MODE_A":
        return [
            "Circular orbit approximation (eccentricity ≈ 0 for all orbits)",
            "Two-body dynamics only (Earth gravity, no perturbations)",
            "Impulsive burn model (instantaneous velocity changes)",
            "Spherical Earth model for ground track projection (R = 6371 km)",
            "WGS84 geodetic coordinates for latitude/longitude",
            "Minimum elevation angle as a geometric line-of-sight constraint",
            "Earth sidereal rotation rate included for longitude drift",
            "No atmospheric drag during transfer or at final orbit",
            "No J2 oblateness precession of RAAN or argument of perigee",
            "RAAN change cost uses simplified scaling (not full 3D plane change)",
            "Satellite capabilities assumed constant during and after transfer",
            "Coverage computed via discrete ground track sampling",
        ]

    if model_mode == "MODE_B":
        return [
            "J2 oblateness perturbation included",
            "Atmospheric drag model (Harris-Priester or exponential)",
            "Third-body perturbations (Sun, Moon) — simplified",
            "Solar radiation pressure — cannonball model",
            "Finite burn model for electric propulsion",
            "WGS84 ellipsoidal Earth for precise coordinates",
        ]

    return ["Unknown model mode — default assumptions apply."]
