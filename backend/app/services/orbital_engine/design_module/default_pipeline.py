"""
Build CandidateGenerationInput / DesignerParams from a validated OrbitDesignRequest.

HTTP layer uses this so enumeration grids stay explicit while callers only supply mission JSON.
"""

from __future__ import annotations

import time
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

from candidate_models import (
    CandidateGenerationInput,
    OrbitFamilySearchParams,
    WalkerTopologyGrid,
)
from optimizer_models import DesignResult, DesignerParams
from request_models import OrbitDesignRequest, OrbitFamily


def _walker_topology_grid(max_satellites: int, max_planes: int) -> WalkerTopologyGrid:
    """Discrete Walker (T, P, F) lists; invalid combos are skipped inside enumeration."""
    ms = max(1, int(max_satellites))
    mp = max(1, int(max_planes))
    t_vals = list(range(6, ms + 1, 6))
    if not t_vals or t_vals[-1] != ms:
        if ms not in t_vals:
            t_vals.append(ms)
    t_vals = sorted({t for t in t_vals if t <= ms})
    if not t_vals:
        t_vals = [min(6, ms)]
    p_vals = list(range(1, mp + 1))
    f_vals = list(range(0, mp))
    return WalkerTopologyGrid(
        total_satellites_T=t_vals,
        planes_P=p_vals,
        phase_F=f_vals,
    )


def _family_search_for(family: OrbitFamily) -> OrbitFamilySearchParams:
    """Explicit altitude / inclination sampling per family (engine contract)."""
    if family == OrbitFamily.LEO:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=400.0,
            altitude_km_max=1200.0,
            altitude_km_step=200.0,
            inclination_deg_min=45.0,
            inclination_deg_max=98.0,
            inclination_deg_step=10.0,
            eccentricity_max=0.0,
            sso_inclination_mode="none",
        )
    if family == OrbitFamily.SSO:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=500.0,
            altitude_km_max=900.0,
            altitude_km_step=100.0,
            inclination_deg_min=96.0,
            inclination_deg_max=100.0,
            inclination_deg_step=1.0,
            eccentricity_max=0.0,
            sso_inclination_mode="mean_sun_synchronous",
        )
    if family == OrbitFamily.MEO:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=5000.0,
            altitude_km_max=12000.0,
            altitude_km_step=1000.0,
            inclination_deg_min=0.0,
            inclination_deg_max=60.0,
            inclination_deg_step=15.0,
            eccentricity_max=0.0,
            sso_inclination_mode="none",
        )
    if family == OrbitFamily.GEO:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=35786.0,
            altitude_km_max=35786.0,
            altitude_km_step=1.0,
            inclination_deg_min=0.0,
            inclination_deg_max=0.0,
            inclination_deg_step=1.0,
            eccentricity_max=0.0,
            sso_inclination_mode="none",
        )
    if family == OrbitFamily.HEO:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=20000.0,
            altitude_km_max=40000.0,
            altitude_km_step=2000.0,
            inclination_deg_min=55.0,
            inclination_deg_max=65.0,
            inclination_deg_step=5.0,
            eccentricity_max=0.15,
            sso_inclination_mode="none",
        )
    if family == OrbitFamily.ELLIPTICAL:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=500.0,
            altitude_km_max=800.0,
            altitude_km_step=100.0,
            inclination_deg_min=63.0,
            inclination_deg_max=65.0,
            inclination_deg_step=2.0,
            eccentricity_max=0.1,
            sso_inclination_mode="none",
        )
    raise ValueError(f"Unsupported orbit family for enumeration: {family}")


def candidate_input_from_request(request: OrbitDesignRequest) -> CandidateGenerationInput:
    fams = tuple(request.optimization.allowed_orbit_families)
    family_search = tuple(_family_search_for(f) for f in fams)
    walker = _walker_topology_grid(
        request.optimization.max_satellites,
        request.optimization.max_planes,
    )
    return CandidateGenerationInput(
        mission_type=request.mission.type,
        allowed_families=fams,
        family_search=family_search,
        walker_grid=walker,
        max_satellites=request.optimization.max_satellites,
        max_planes=request.optimization.max_planes,
        epoch_seconds_tai=time.time(),
    )


def default_designer_params() -> DesignerParams:
    """Operational simulation grid / pruning defaults (deterministic design loop)."""
    return DesignerParams(
        grid_spacing_m=150_000.0,
        simulation_time_step_seconds=120.0,
        region_circle_vertices=36,
        early_stop_on_first_feasible_minimum_t=True,
        footprint_solid_angle_packing_factor=1.12,
        top_candidates_limit=8,
        grid_include_boundary=True,
    )


def _sanitize_for_json(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj):
        return _sanitize_for_json(asdict(obj))
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(x) for x in obj]
    return obj


def design_result_to_dict(result: DesignResult) -> dict:
    """JSON-serializable dict for encryption / API responses."""
    return _sanitize_for_json(asdict(result))
