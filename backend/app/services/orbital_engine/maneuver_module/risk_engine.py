"""
ORBITA-R — Risk Engine
=======================
Multi-factor risk assessment for satellite repositioning plans.

Risk sources:
  1. Zone risk — intersection with degradation zones and risk zones
  2. Proximity risk — closeness to other satellites (collision proxy)
  3. Satellite risk — low reliability, fuel, or maneuver capacity
  4. Transfer risk — difficulty and danger of the actual orbital transfer

All risk scores are normalized to [0.0, 1.0].
"""

from __future__ import annotations

import math
from typing import List, Optional

from .satellite_models import (
    OrbitalState, Satellite, TransferSummary, R_EARTH, DEG_TO_RAD,
)
from .simulation_state import (
    SimulationState, DegradationZone, RiskZone,
)


# ──────────────────────────────────────────────
# Zone Risk
# ──────────────────────────────────────────────

def _orbit_in_zone(orbit: OrbitalState, zone_alt_min: float, zone_alt_max: float,
                    zone_incl_min: float, zone_incl_max: float,
                    zone_raan_min: float, zone_raan_max: float) -> bool:
    """Check if an orbit's parameters overlap with a zone's parameter ranges."""
    # Altitude check
    if orbit.altitude_km < zone_alt_min or orbit.altitude_km > zone_alt_max:
        return False

    # Inclination check
    if orbit.inclination_deg < zone_incl_min or orbit.inclination_deg > zone_incl_max:
        return False

    # RAAN check (handle wrap-around)
    if zone_raan_min <= zone_raan_max:
        if orbit.raan_deg < zone_raan_min or orbit.raan_deg > zone_raan_max:
            return False
    else:
        # Zone wraps around 360°
        if orbit.raan_deg < zone_raan_min and orbit.raan_deg > zone_raan_max:
            return False

    return True


def compute_zone_risk(
    orbit: OrbitalState,
    degradation_zones: List[DegradationZone],
    risk_zones: List[RiskZone],
) -> float:
    """
    Compute risk from intersection with degradation and risk zones.

    Method:
      - Check each zone for overlap with the candidate orbit.
      - Accumulate weighted severity scores.
      - Risk zones are weighted more heavily than degradation zones.
      - Normalize with diminishing returns.

    Returns:
        Zone risk score [0.0, 1.0].
    """
    risk_accumulator = 0.0

    # Degradation zones (lower weight)
    for zone in degradation_zones:
        if _orbit_in_zone(orbit, zone.alt_min_km, zone.alt_max_km,
                          zone.incl_min_deg, zone.incl_max_deg,
                          zone.raan_min_deg, zone.raan_max_deg):
            risk_accumulator += 0.6 * zone.severity

    # Risk zones (higher weight)
    for zone in risk_zones:
        if _orbit_in_zone(orbit, zone.alt_min_km, zone.alt_max_km,
                          zone.incl_min_deg, zone.incl_max_deg,
                          zone.raan_min_deg, zone.raan_max_deg):
            weight = 1.0
            if zone.risk_type == "debris":
                weight = 1.2
            elif zone.risk_type == "restricted":
                weight = 1.5
            elif zone.risk_type == "conjunction":
                weight = 1.0
            risk_accumulator += weight * zone.severity

    # Normalize with diminishing returns: 1 - e^(-k*x)
    return 1.0 - math.exp(-1.5 * risk_accumulator)


# ──────────────────────────────────────────────
# Proximity Risk
# ──────────────────────────────────────────────

def _orbital_distance_proxy(orbit1: OrbitalState, orbit2: OrbitalState) -> float:
    """
    Compute a proxy for the minimum distance between two orbits.

    For circular orbits, the minimum distance depends on:
      - Altitude difference
      - Inclination difference
      - RAAN difference

    This is NOT the true minimum distance (which requires full 3D analysis),
    but a computationally cheap proxy that captures the main factors.

    Returns:
        Distance proxy in km. Lower = closer orbits.
    """
    # Altitude contribution
    alt_diff = abs(orbit1.altitude_km - orbit2.altitude_km)

    # Angular separation (simplified)
    # In reality, this depends on the exact geometry of the two orbital planes
    inc_diff = abs(orbit1.inclination_deg - orbit2.inclination_deg) * DEG_TO_RAD
    raan_diff = abs(orbit1.raan_deg - orbit2.raan_deg)
    if raan_diff > 180:
        raan_diff = 360 - raan_diff
    raan_diff_rad = raan_diff * DEG_TO_RAD

    # Effective angular separation between orbital planes
    # Approximate: total plane angle from inclination and RAAN differences
    plane_angle = math.sqrt(inc_diff ** 2 + (raan_diff_rad * 0.5) ** 2)

    # Convert to approximate physical separation at orbital altitude
    avg_alt = (orbit1.altitude_km + orbit2.altitude_km) / 2.0
    r_avg = R_EARTH + avg_alt
    angular_separation_km = r_avg * plane_angle

    # Total distance proxy
    return math.sqrt(alt_diff ** 2 + angular_separation_km ** 2)


def compute_proximity_risk(
    orbit: OrbitalState,
    other_satellites: List[Satellite],
    min_safe_distance_km: float = 50.0,
) -> float:
    """
    Compute collision risk proxy based on orbital proximity to other satellites.

    Method:
      - Compute distance proxy to each other satellite.
      - If distance < min_safe_distance → high risk.
      - Risk decays exponentially with distance.
      - Maximum risk from the closest satellite is used.

    Returns:
        Proximity risk score [0.0, 1.0].
    """
    if not other_satellites:
        return 0.0

    max_risk = 0.0
    for sat in other_satellites:
        dist = _orbital_distance_proxy(orbit, sat.current_orbit)

        if dist < min_safe_distance_km:
            risk = 1.0
        else:
            # Exponential decay from safe distance
            risk = math.exp(-0.005 * (dist - min_safe_distance_km))

        max_risk = max(max_risk, risk)

    return max_risk


# ──────────────────────────────────────────────
# Satellite Intrinsic Risk
# ──────────────────────────────────────────────

def compute_satellite_risk(satellite: Satellite) -> float:
    """
    Compute risk based on intrinsic satellite properties.

    Factors:
      - Low reliability → higher risk
      - Low fuel/budget → higher risk (may not complete transfer)
      - Low maneuver capacity → higher risk (less margin for error)

    Returns:
        Satellite risk score [0.0, 1.0].
    """
    caps = satellite.capabilities

    reliability_risk = 1.0 - caps.reliability
    fuel_risk = 1.0 - caps.fuel_or_budget_score
    maneuver_risk = 1.0 - caps.maneuver_capacity_score

    # Weighted combination — fuel and reliability are most critical
    risk = 0.4 * reliability_risk + 0.35 * fuel_risk + 0.25 * maneuver_risk

    return max(0.0, min(1.0, risk))


# ──────────────────────────────────────────────
# Transfer Risk
# ──────────────────────────────────────────────

def compute_transfer_risk(
    transfer_summary: TransferSummary,
    satellite: Satellite,
) -> float:
    """
    Compute risk associated with the actual orbital transfer.

    Factors:
      - High Δv → more fuel consumption, higher risk of failure
      - Long transfer time → more exposure to perturbations
      - High transfer cost relative to satellite budget → risk

    Returns:
        Transfer risk score [0.0, 1.0].
    """
    # Δv risk: higher Δv = higher risk. 1.0 km/s is very significant for LEO.
    dv_risk = min(transfer_summary.delta_v_total_km_s / 2.0, 1.0)

    # Time risk: longer transfers have more uncertainty
    # 48 hours is moderate, 200+ hours is very risky
    time_risk = min(transfer_summary.transfer_time_hours / 200.0, 1.0)

    # Budget risk: can the satellite afford this transfer?
    fuel_score = satellite.capabilities.fuel_or_budget_score
    budget_risk = max(0.0, transfer_summary.transfer_cost_score - fuel_score)

    # Combined
    risk = 0.4 * dv_risk + 0.3 * time_risk + 0.3 * budget_risk

    return max(0.0, min(1.0, risk))


# ──────────────────────────────────────────────
# Total Risk
# ──────────────────────────────────────────────

def compute_total_risk(
    candidate_orbit: OrbitalState,
    satellite: Satellite,
    sim_state: SimulationState,
    transfer_summary: TransferSummary,
) -> dict:
    """
    Compute the complete risk analysis for a repositioning plan.

    Combines zone risk, proximity risk, satellite risk, and transfer risk
    into a total risk score.

    Returns:
        Dictionary with individual risk components and total score.
    """
    other_sats = sim_state.get_other_satellites(satellite.id)

    zone_risk = compute_zone_risk(
        candidate_orbit,
        sim_state.degradation_zones,
        sim_state.risk_zones,
    )
    prox_risk = compute_proximity_risk(
        candidate_orbit, other_sats,
        sim_state.system_constraints.min_satellite_separation_km,
    )
    sat_risk = compute_satellite_risk(satellite)
    trans_risk = compute_transfer_risk(transfer_summary, satellite)

    # Weighted combination
    # Zone and proximity are environmental, satellite and transfer are operational
    total = (
        0.25 * zone_risk +
        0.25 * prox_risk +
        0.20 * sat_risk +
        0.30 * trans_risk
    )
    total = max(0.0, min(1.0, total))

    # Compile risk factors (human-readable)
    risk_factors = []
    if zone_risk > 0.3:
        risk_factors.append(f"Candidate orbit intersects risk/degradation zones (zone_risk={zone_risk:.2f}).")
    if prox_risk > 0.3:
        risk_factors.append(f"Close proximity to other satellites detected (proximity_risk={prox_risk:.2f}).")
    if sat_risk > 0.3:
        risk_factors.append(f"Satellite has reduced operational margins (satellite_risk={sat_risk:.2f}).")
    if trans_risk > 0.3:
        risk_factors.append(f"Transfer operation carries significant risk (transfer_risk={trans_risk:.2f}).")
    if not risk_factors:
        risk_factors.append("No significant risk factors identified for this plan.")

    return {
        "zone_risk": round(zone_risk, 4),
        "proximity_risk": round(prox_risk, 4),
        "satellite_risk": round(sat_risk, 4),
        "transfer_risk": round(trans_risk, 4),
        "total_risk_score": round(total, 4),
        "risk_factors": risk_factors,
    }
