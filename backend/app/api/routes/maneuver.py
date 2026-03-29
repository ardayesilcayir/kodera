from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Literal

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app.services.orbital_engine.maneuver_module import optimize_reposition
from app.services.orbital_engine.maneuver_module.satellite_models import (
    Satellite, SatelliteCapabilities, MissionConstraints, OrbitalState,
)
from app.services.orbital_engine.maneuver_module.simulation_state import SimulationState
from app.services.orbital_engine.maneuver_module.target_region import TargetRegion
from app.services.nlp_service import NLPService

router = APIRouter()


class ManeuverRequest(BaseModel):
    satellite_id: str
    satellite_name: str
    current_altitude_km: float
    current_inclination_deg: float
    current_raan_deg: float
    current_phase_deg: float = 0.0
    satellite_mission_type: Literal["communication", "observation", "emergency", "balanced"] = "communication"
    mission_type: Literal["communication", "observation", "emergency", "balanced"] = "communication"
    target_lat: float
    target_lon: float
    target_radius_km: float = 200.0
    optimization_mode: str = "balanced"
    max_transfer_time_hours: float = 48.0


def _build_objects(req: ManeuverRequest):
    """Convert the flat Pydantic request into maneuver-module dataclass objects."""
    orbit = OrbitalState(
        altitude_km=req.current_altitude_km,
        inclination_deg=req.current_inclination_deg,
        raan_deg=req.current_raan_deg,
        phase_deg=req.current_phase_deg,
    )
    caps = SatelliteCapabilities(
        mission_type=req.satellite_mission_type,
        coverage_radius_km=1500.0,
        min_elevation_deg=10.0,
    )
    satellite = Satellite(
        id=req.satellite_id,
        name=req.satellite_name,
        current_orbit=orbit,
        capabilities=caps,
    )
    region = TargetRegion(
        center_lat=req.target_lat,
        center_lon=req.target_lon,
        radius_km=req.target_radius_km,
    )
    constraints = MissionConstraints(
        max_transfer_time_hours=req.max_transfer_time_hours,
        optimization_mode=req.optimization_mode,
    )
    sim_state = SimulationState(
        current_time=datetime.utcnow(),
        active_satellites=[satellite],
    )
    return satellite, region, constraints, sim_state


@router.post("/optimize")
async def optimize_maneuver(request: ManeuverRequest):
    """
    Mevcut bir uyduyu hedef bölgeye en verimli yörünge ile yeniden konumlandırır.
    CPU-Bound: threadpool üzerinde çalışır.
    """
    try:
        satellite, region, constraints, sim_state = _build_objects(request)

        result = await run_in_threadpool(
            optimize_reposition,
            satellite=satellite,
            target_region=region,
            mission_type=request.mission_type,
            sim_state=sim_state,
            constraints=constraints,
            max_candidates=50,
            top_n=3,
        )

        result_dict = asdict(result)

        ai_summary = NLPService.generate_engineering_summary(
            result_dict,
            "Satellite Reposition (Hohmann Transfer & Plane Change)",
        )
        result_dict["ai_engineering_summary"] = ai_summary

        return {
            "status": "success",
            "feature": "satellite_maneuver",
            "data": result_dict,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
