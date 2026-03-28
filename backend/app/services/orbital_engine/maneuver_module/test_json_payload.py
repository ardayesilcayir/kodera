import sys
from datetime import datetime

from satellite_models import Satellite, OrbitalState, SatelliteCapabilities, MissionConstraints
from simulation_state import SimulationState
from target_region import TargetRegion
from reposition_optimizer import optimize_reposition

def run():
    # 1. Parse current satellite
    current_satellite = Satellite(
        id="sat-iss-like-001",
        name="ISS_LIKE_TEST",
        current_orbit=OrbitalState(
            altitude_km=421.0, 
            inclination_deg=51.63, 
            raan_deg=118.0, 
            phase_deg=42.0
        ),
        capabilities=SatelliteCapabilities(
            mission_type="emergency",
            coverage_radius_km=1350.0,
            min_elevation_deg=20.0,
            bandwidth=0.84,
            reliability=0.93,
            maneuver_capacity_score=0.72,
            fuel_or_budget_score=0.68
        )
    )

    # 2. Parse target region
    target_region = TargetRegion(
        center_lat=41.07,
        center_lon=29.10,
        bbox=(40.80, 28.50, 41.35, 29.90)
    )

    # 3. Parse simulation state
    sim_state = SimulationState(
        current_time=datetime(2026, 3, 28, 12, 0, 0),
        active_satellites=[current_satellite], # It's the only one
        region_tasks=[],
        degradation_zones=[],
        risk_zones=[]
    )

    # 4. Parse constraints
    constraints = MissionConstraints(
        max_transfer_time_hours=36.0,
        min_elevation_deg=20.0,
        optimization_mode="balanced"
    )

    mission_type = "emergency"

    # Run optimizer
    print("Running optimization engine with supplied JSON payload equivalent...")
    result = optimize_reposition(
        satellite=current_satellite,
        target_region=target_region,
        mission_type=mission_type,
        sim_state=sim_state,
        constraints=constraints,
        max_candidates=50,
        top_n=3
    )

    print("\n================ OPTIMIZATION RESULT ================")
    print(f"Summary: {result.summary}")
    print("\n[ BEST PLAN ]")
    print(f"Target Orbit: alt={result.best_plan.target_orbit.altitude_km}km, inc={result.best_plan.target_orbit.inclination_deg}deg, raan={result.best_plan.target_orbit.raan_deg}deg")
    print(f"Final Score: {result.best_plan.final_score:.4f}")
    print(f"Feasibility Score: {result.best_plan.feasibility_score:.4f}")
    print(f"Confidence Score: {result.best_plan.confidence_score:.4f}")
    
    print("\n--- Transfer Summary ---")
    print(f"Total delta-v: {result.best_plan.transfer_summary.delta_v_total_km_s:.4f} km/s")
    print(f"Alt change: {result.best_plan.transfer_summary.altitude_change_km:.1f} km")
    print(f"Inc change: {result.best_plan.transfer_summary.inclination_change_deg:.2f} deg")
    print(f"RAAN change: {result.best_plan.transfer_summary.raan_change_deg:.2f} deg")
    print(f"Transfer time: {result.best_plan.transfer_summary.transfer_time_hours:.2f} hrs")
    
    print("\n--- Coverage Metrics ---")
    print(f"Target Coverage: {result.best_plan.coverage_metrics.target_region_coverage:.2%}")
    print(f"Coverage Gain: {result.best_plan.coverage_metrics.coverage_gain:+.2%}")
    
    print("\n--- Risk ---")
    print(f"Total Risk Score: {result.best_plan.risk_analysis.total_risk_score:.4f}")
    
    print("\n--- Engine Explanation ---")
    print(result.best_plan.explanation)

if __name__ == "__main__":
    run()
