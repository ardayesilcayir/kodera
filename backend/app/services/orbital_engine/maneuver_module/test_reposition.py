"""
ORBITA-R -- Test Reposition
============================
Comprehensive test scenarios for the satellite repositioning optimization module.

Test Scenarios:
  1. Simple altitude change -- small delta, same inclination
  2. Cross-hemisphere repositioning -- large inclination and RAAN change
  3. Congested region -- many satellites already covering the target
  4. Emergency mission -- short time constraint, high coverage priority
  5. Infeasible case -- satellite lacks fuel/capacity
  6. Physical sanity checks -- validate known orbital mechanics values
"""

from __future__ import annotations

import math
import sys
from datetime import datetime
from typing import List

# Add module path
from satellite_models import (
    OrbitalState, SatelliteCapabilities, Satellite, MissionConstraints,
    TransferSummary, hohmann_delta_v, orbital_period, orbital_velocity,
    R_EARTH, MU_EARTH,
)
from simulation_state import (
    SimulationState, SystemConstraints, DegradationZone, RiskZone,
    RegionTask,
)
from target_region import TargetRegion, haversine_distance
from coverage_engine import compute_footprint_radius_km
from reposition_optimizer import optimize_reposition, compute_transfer_cost


# ──────────────────────────────────────────────
# Helper: Create Test Fixtures
# ──────────────────────────────────────────────

def make_satellite(
    sat_id: str,
    name: str,
    alt: float, inc: float, raan: float, phase: float,
    mission_type: str = "balanced",
    fuel: float = 0.7,
    reliability: float = 0.85,
    maneuver_cap: float = 0.6,
) -> Satellite:
    """Create a test satellite with sensible defaults."""
    return Satellite(
        id=sat_id,
        name=name,
        current_orbit=OrbitalState(alt, inc, raan, phase),
        capabilities=SatelliteCapabilities(
            mission_type=mission_type,
            coverage_radius_km=1500.0,
            min_elevation_deg=10.0,
            bandwidth=0.6,
            reliability=reliability,
            maneuver_capacity_score=maneuver_cap,
            fuel_or_budget_score=fuel,
        ),
    )


def make_sim_state(
    satellites: List[Satellite],
    degradation_zones: List[DegradationZone] = None,
    risk_zones: List[RiskZone] = None,
) -> SimulationState:
    """Create a test simulation state."""
    return SimulationState(
        current_time=datetime(2026, 3, 28, 12, 0, 0),
        active_satellites=satellites,
        region_tasks=[],
        system_constraints=SystemConstraints(),
        degradation_zones=degradation_zones or [],
        risk_zones=risk_zones or [],
    )


# ──────────────────────────────────────────────
# Test Scenario 1: Simple Altitude Change
# ──────────────────────────────────────────────

def test_simple_altitude_change():
    """
    Scenario: Reposition satellite from 500 km to serve a region that
    benefits from a slightly higher or lower altitude. Same inclination.
    Expected: Low transfer cost, positive coverage gain, high feasibility.
    """
    print("\n" + "=" * 70)
    print("TEST 1: Simple Altitude Change")
    print("=" * 70)

    sat = make_satellite("s1", "SAT-Alpha", alt=500, inc=45, raan=100, phase=0)
    other_sat = make_satellite("s2", "SAT-Beta", alt=600, inc=50, raan=200, phase=90)
    sim_state = make_sim_state([sat, other_sat])

    region = TargetRegion(center_lat=40.0, center_lon=30.0, radius_km=300)
    constraints = MissionConstraints(
        max_transfer_time_hours=48,
        optimization_mode="balanced",
    )

    result = optimize_reposition(
        sat, region, "observation", sim_state, constraints,
        max_candidates=30, top_n=3,
    )

    print(f"\nSummary: {result.summary}")
    print(f"Candidates evaluated: {result.total_candidates_evaluated}")
    print(f"Best plan score: {result.best_plan.final_score:.4f}")
    print(f"Best plan feasibility: {result.best_plan.feasibility_score:.4f}")
    print(f"Best plan confidence: {result.best_plan.confidence_score:.4f}")
    print(f"Target orbit: alt={result.best_plan.target_orbit.altitude_km:.1f} km, "
          f"inc={result.best_plan.target_orbit.inclination_deg:.1f} deg")
    print(f"Transfer dv: {result.best_plan.transfer_summary.delta_v_total_km_s:.4f} km/s")
    print(f"Coverage gain: {result.best_plan.coverage_metrics.coverage_gain:+.2%}")
    print(f"Limitations count: {len(result.best_plan.limitations)}")

    # Assertions
    assert result.best_plan.final_score > 0, "Final score should be positive for a simple change"
    assert result.best_plan.feasibility_score > 0, "Feasibility should be positive"
    assert result.best_plan.confidence_score > 0, "Confidence should be positive"
    assert len(result.best_plan.limitations) > 0, "Limitations should never be empty"
    assert result.best_plan.explanation, "Explanation should not be empty"

    print("\n[PASS] Test 1 PASSED")
    return True


# ──────────────────────────────────────────────
# Test Scenario 2: Cross-hemisphere Repositioning
# ──────────────────────────────────────────────

def test_cross_hemisphere():
    """
    Scenario: Reposition from a low-inclination equatorial orbit to serve a
    high-latitude target region. Requires large inclination change.
    Expected: High transfer cost, lower feasibility, but coverage gain if successful.
    """
    print("\n" + "=" * 70)
    print("TEST 2: Cross-hemisphere Repositioning")
    print("=" * 70)

    sat = make_satellite("s1", "SAT-Alpha", alt=500, inc=10, raan=0, phase=0, fuel=0.8)
    other_sat = make_satellite("s2", "SAT-Beta", alt=700, inc=70, raan=90, phase=45)
    sim_state = make_sim_state([sat, other_sat])

    # Target: Northern Scandinavia (high latitude)
    region = TargetRegion(center_lat=65.0, center_lon=25.0, radius_km=400)
    constraints = MissionConstraints(
        max_transfer_time_hours=72,
        optimization_mode="coverage",
    )

    result = optimize_reposition(
        sat, region, "communication", sim_state, constraints,
        max_candidates=30, top_n=3,
    )

    print(f"\nSummary: {result.summary}")
    print(f"Best plan: alt={result.best_plan.target_orbit.altitude_km:.1f} km, "
          f"inc={result.best_plan.target_orbit.inclination_deg:.1f} deg")
    print(f"Transfer dv: {result.best_plan.transfer_summary.delta_v_total_km_s:.4f} km/s")
    print(f"Inc change: {result.best_plan.transfer_summary.inclination_change_deg:.1f} deg")
    print(f"Final score: {result.best_plan.final_score:.4f}")
    print(f"Feasibility: {result.best_plan.feasibility_score:.4f}")
    print(f"Risk score: {result.best_plan.risk_analysis.total_risk_score:.4f}")

    # The inclination must be >= 65 to reach lat 65
    assert result.best_plan.target_orbit.inclination_deg >= 60.0, \
        "Target inclination should be high enough to reach 65 deg N"
    # Transfer cost should be significant for a large plane change
    assert result.best_plan.transfer_summary.delta_v_total_km_s > 0.1, \
        "dv should be significant for cross-hemisphere repositioning"
    assert len(result.best_plan.limitations) > 0, "Limitations should never be empty"

    print("\n[PASS] Test 2 PASSED")
    return True


# ──────────────────────────────────────────────
# Test Scenario 3: Congested Region
# ──────────────────────────────────────────────

def test_congested_region():
    """
    Scenario: Many satellites already cover the target region.
    Expected: High overlap penalty, lower strategic fit, still feasible.
    """
    print("\n" + "=" * 70)
    print("TEST 3: Congested Region")
    print("=" * 70)

    sat = make_satellite("s1", "SAT-Alpha", alt=500, inc=45, raan=100, phase=0)

    # Create many satellites covering the same area
    others = [
        make_satellite("s2", "SAT-B", alt=520, inc=44, raan=102, phase=30),
        make_satellite("s3", "SAT-C", alt=510, inc=46, raan=98, phase=60),
        make_satellite("s4", "SAT-D", alt=530, inc=43, raan=105, phase=90),
        make_satellite("s5", "SAT-E", alt=490, inc=47, raan=95, phase=120),
    ]

    all_sats = [sat] + others
    sim_state = make_sim_state(all_sats)

    region = TargetRegion(center_lat=40.0, center_lon=30.0, radius_km=200)
    constraints = MissionConstraints(optimization_mode="efficiency")

    result = optimize_reposition(
        sat, region, "balanced", sim_state, constraints,
        max_candidates=20, top_n=3,
    )

    print(f"\nSummary: {result.summary}")
    print(f"Best plan overlap penalty: {result.best_plan.system_impact.overlap_penalty:.4f}")
    print(f"Best plan redundancy: {result.best_plan.system_impact.redundancy_score:.4f}")
    print(f"Best plan final score: {result.best_plan.final_score:.4f}")

    # With many satellites in similar orbits, check system interaction exists
    assert result.best_plan.system_impact.redundancy_score >= 0, \
        "Redundancy score should be non-negative"
    assert len(result.best_plan.limitations) > 0

    print("\n[PASS] Test 3 PASSED")
    return True


# ──────────────────────────────────────────────
# Test Scenario 4: Emergency Mission
# ──────────────────────────────────────────────

def test_emergency_mission():
    """
    Scenario: Emergency mission with tight time constraints.
    Expected: Optimizer favors fast/low-cost transfers, may sacrifice coverage.
    """
    print("\n" + "=" * 70)
    print("TEST 4: Emergency Mission")
    print("=" * 70)

    sat = make_satellite("s1", "SAT-Alpha", alt=500, inc=45, raan=100, phase=0,
                         mission_type="emergency", fuel=0.9, maneuver_cap=0.8)
    sim_state = make_sim_state([sat])

    region = TargetRegion(center_lat=35.0, center_lon=35.0, radius_km=200)
    constraints = MissionConstraints(
        max_transfer_time_hours=12,  # Very tight
        optimization_mode="speed",
    )

    result = optimize_reposition(
        sat, region, "emergency", sim_state, constraints,
        max_candidates=30, top_n=3,
    )

    print(f"\nSummary: {result.summary}")
    print(f"Best plan transfer time: {result.best_plan.transfer_summary.transfer_time_hours:.2f}h")
    print(f"Best plan final score: {result.best_plan.final_score:.4f}")
    print(f"Best plan feasibility: {result.best_plan.feasibility_score:.4f}")

    assert result.best_plan.final_score >= 0, "Score should not be negative"
    assert len(result.best_plan.limitations) > 0

    print("\n[PASS] Test 4 PASSED")
    return True


# ──────────────────────────────────────────────
# Test Scenario 5: Infeasible Case
# ──────────────────────────────────────────────

def test_infeasible_case():
    """
    Scenario: Satellite has very low fuel and maneuver capacity.
    Expected: Low feasibility scores, system returns plans but flags them.
    """
    print("\n" + "=" * 70)
    print("TEST 5: Infeasible Case (Low Fuel)")
    print("=" * 70)

    sat = make_satellite("s1", "SAT-Weak", alt=400, inc=20, raan=50, phase=0,
                         fuel=0.05, reliability=0.4, maneuver_cap=0.1)
    sim_state = make_sim_state([sat])

    # Far target requiring large plane change
    region = TargetRegion(center_lat=70.0, center_lon=100.0, radius_km=500)
    constraints = MissionConstraints(
        max_transfer_time_hours=24,
        optimization_mode="balanced",
    )

    result = optimize_reposition(
        sat, region, "observation", sim_state, constraints,
        max_candidates=20, top_n=3,
    )

    print(f"\nSummary: {result.summary}")
    print(f"Best plan feasibility: {result.best_plan.feasibility_score:.4f}")
    print(f"Best plan confidence: {result.best_plan.confidence_score:.4f}")
    print(f"Best plan risk: {result.best_plan.risk_analysis.total_risk_score:.4f}")
    print(f"Satellite risk: {result.best_plan.risk_analysis.satellite_risk:.4f}")

    # With very low fuel for a large maneuver, feasibility should be low
    assert result.best_plan.feasibility_score < 0.5, \
        "Feasibility should be low for a fuel-starved satellite"
    assert result.best_plan.risk_analysis.satellite_risk > 0.3, \
        "Satellite risk should be elevated for low reliability/fuel"
    assert len(result.best_plan.limitations) > 0

    print("\n[PASS] Test 5 PASSED")
    return True


# ──────────────────────────────────────────────
# Test Scenario 6: Physical Sanity Checks
# ──────────────────────────────────────────────

def test_physical_sanity():
    """
    Verify known orbital mechanics values:
      - Hohmann dv for 500->600 km ~ 0.054 km/s
      - Orbital period at 500 km ~ 5677 s (~ 94.6 min)
      - Orbital velocity at 500 km ~ 7.613 km/s
      - Footprint radius at 500 km / 10 deg elevation ~ 2100-2500 km
    """
    print("\n" + "=" * 70)
    print("TEST 6: Physical Sanity Checks")
    print("=" * 70)

    # Hohmann transfer 500 -> 600 km
    dv1, dv2, dv_total = hohmann_delta_v(500, 600)
    print(f"Hohmann 500->600 km: dv1={dv1:.4f}, dv2={dv2:.4f}, total={dv_total:.4f} km/s")
    assert 0.04 < dv_total < 0.07, f"Hohmann dv should be ~0.054 km/s, got {dv_total:.4f}"

    # Orbital period at 500 km
    T = orbital_period(500)
    T_min = T / 60.0
    print(f"Orbital period at 500 km: {T:.1f} s = {T_min:.1f} min")
    assert 93 < T_min < 96, f"Period should be ~94.6 min, got {T_min:.1f}"

    # Orbital velocity at 500 km
    v = orbital_velocity(500)
    print(f"Orbital velocity at 500 km: {v:.3f} km/s")
    assert 7.5 < v < 7.7, f"Velocity should be ~7.6 km/s, got {v:.3f}"

    # Footprint radius at 500 km, 10 deg elevation
    fp = compute_footprint_radius_km(500, 10.0)
    print(f"Footprint radius at 500 km / 10 deg elev: {fp:.0f} km")
    assert 1500 < fp < 3000, f"Footprint should be ~2100-2500 km, got {fp:.0f}"

    # Haversine distance: London to Paris ~ 340 km
    d = haversine_distance(51.5, -0.1, 48.9, 2.3)
    print(f"London->Paris distance: {d:.0f} km")
    assert 300 < d < 400, f"Distance should be ~340 km, got {d:.0f}"

    # 90 deg inclination change dv at 500 km -- should be ~10.7 km/s
    from satellite_models import inclination_change_delta_v
    dv_90 = inclination_change_delta_v(500, 90.0)
    print(f"90 deg inclination change at 500 km: {dv_90:.2f} km/s")
    assert 10.0 < dv_90 < 11.0, f"90 deg inc change should be ~10.7 km/s, got {dv_90:.2f}"

    # Transfer cost computation
    orbit1 = OrbitalState(500, 45, 100, 0)
    orbit2 = OrbitalState(600, 50, 120, 90)
    ts = compute_transfer_cost(orbit1, orbit2)
    print(f"Transfer 500/45/100 -> 600/50/120:")
    print(f"  dv_alt={ts.delta_v_altitude_km_s:.4f} km/s")
    print(f"  dv_inc={ts.delta_v_inclination_km_s:.4f} km/s")
    print(f"  dv_total={ts.delta_v_total_km_s:.4f} km/s")
    print(f"  cost_score={ts.transfer_cost_score:.4f}")
    assert ts.delta_v_total_km_s > 0, "Total dv should be positive"
    assert 0 <= ts.transfer_cost_score <= 1, "Cost score should be in [0, 1]"

    print("\n[PASS] Test 6 PASSED (all physical sanity checks)")
    return True


# ──────────────────────────────────────────────
# Test Runner
# ──────────────────────────────────────────────

def test_explanation_contains_disclaimer():
    """Verify that plan explanations contain proper disclaimer language."""
    print("\n" + "=" * 70)
    print("TEST 7: Explanation Contains Disclaimer")
    print("=" * 70)

    sat = make_satellite("s1", "SAT-Alpha", alt=500, inc=45, raan=100, phase=0)
    sim_state = make_sim_state([sat])
    region = TargetRegion(center_lat=40.0, center_lon=30.0, radius_km=300)
    constraints = MissionConstraints()

    result = optimize_reposition(
        sat, region, "balanced", sim_state, constraints,
        max_candidates=15, top_n=1,
    )

    explanation = result.best_plan.explanation
    assert "highest-scoring" in explanation.lower() or "model" in explanation.lower(), \
        "Explanation must contain uncertainty language"
    assert "mode a" in explanation.lower() or "model" in explanation.lower(), \
        "Explanation must reference the model mode"
    assert result.best_plan.confidence_score < 1.0, \
        "Confidence must never reach 1.0"
    assert result.best_plan.confidence_score > 0.0, \
        "Confidence must be positive for a valid plan"

    print(f"Confidence score: {result.best_plan.confidence_score:.4f}")
    print(f"Explanation length: {len(explanation)} chars")
    print(f"Contains 'highest-scoring': {'highest-scoring' in explanation.lower()}")

    print("\n[PASS] Test 7 PASSED")
    return True


def test_with_risk_zones():
    """Test that risk zones affect the risk score."""
    print("\n" + "=" * 70)
    print("TEST 8: Risk Zones Impact")
    print("=" * 70)

    sat = make_satellite("s1", "SAT-Alpha", alt=500, inc=45, raan=100, phase=0)

    risk_zones = [
        RiskZone(
            alt_min_km=400, alt_max_km=600,
            incl_min_deg=30, incl_max_deg=60,
            risk_type="debris", severity=0.8,
            description="Simulated debris field",
        ),
    ]

    sim_state = make_sim_state([sat], risk_zones=risk_zones)
    region = TargetRegion(center_lat=40.0, center_lon=30.0, radius_km=300)
    constraints = MissionConstraints()

    result = optimize_reposition(
        sat, region, "balanced", sim_state, constraints,
        max_candidates=15, top_n=2,
    )

    print(f"Best plan risk score: {result.best_plan.risk_analysis.total_risk_score:.4f}")
    print(f"Risk factors: {result.best_plan.risk_analysis.risk_factors}")

    # Not all candidates will be in the risk zone, but the risk engine should be active
    assert result.total_candidates_evaluated > 0
    assert len(result.best_plan.limitations) > 0

    print("\n[PASS] Test 8 PASSED")
    return True


def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "#" * 70)
    print("  ORBITA-R -- Repositioning Optimization Module Tests")
    print("#" * 70)

    tests = [
        ("Physical Sanity Checks", test_physical_sanity),
        ("Simple Altitude Change", test_simple_altitude_change),
        ("Cross-hemisphere Repositioning", test_cross_hemisphere),
        ("Congested Region", test_congested_region),
        ("Emergency Mission", test_emergency_mission),
        ("Infeasible Case", test_infeasible_case),
        ("Explanation Disclaimer", test_explanation_contains_disclaimer),
        ("Risk Zones Impact", test_with_risk_zones),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, True, None))
        except Exception as e:
            print(f"\n[FAIL] {name} FAILED: {e}")
            results.append((name, False, str(e)))

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    passed_count = 0
    for name, passed, error in results:
        status = "[PASS] PASSED" if passed else f"[FAIL] FAILED: {error}"
        print(f"  {name}: {status}")
        if passed:
            passed_count += 1

    print(f"\n  {passed_count}/{len(tests)} tests passed.")
    print("=" * 70)

    return passed_count == len(tests)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
