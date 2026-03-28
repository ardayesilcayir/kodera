"""
Internal defaults for POST /api/v1/design/orbit (single public JSON body).

The optimization engine still receives explicit ``CandidateGenerationInput`` and
``DesignerParams``; they are built here from ``OrbitDesignRequest`` plus fixed
reference configuration (no duplicated max_satellites in the public contract).
"""

from __future__ import annotations

from typing import List, Tuple

from candidate_models import (
    CandidateGenerationInput,
    OrbitFamilySearchParams,
    WalkerTopologyGrid,
    mission_family_search_order,
)
from optimizer_models import DesignerParams
from request_models import OrbitDesignRequest, OrbitFamily

# Fixed reference epoch for reproducible Kepler propagation (POSIX seconds, 2024-06-01T12:00:00Z).
DEFAULT_REFERENCE_EPOCH_TAI_SECONDS = 1717243200.0


def _default_family_search_params(family: OrbitFamily) -> OrbitFamilySearchParams:
    """One altitude sample per family; circular orbits (eccentricity 0)."""
    if family == OrbitFamily.LEO:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=550.0,
            altitude_km_max=550.0,
            altitude_km_step=1.0,
            inclination_deg_min=51.6,
            inclination_deg_max=51.6,
            inclination_deg_step=1.0,
            eccentricity_max=0.0,
            sso_inclination_mode="none",
        )
    if family == OrbitFamily.SSO:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=705.0,
            altitude_km_max=705.0,
            altitude_km_step=1.0,
            inclination_deg_min=98.0,
            inclination_deg_max=98.0,
            inclination_deg_step=1.0,
            eccentricity_max=0.0,
            sso_inclination_mode="mean_sun_synchronous",
        )
    if family == OrbitFamily.MEO:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=8000.0,
            altitude_km_max=8000.0,
            altitude_km_step=1.0,
            inclination_deg_min=55.0,
            inclination_deg_max=55.0,
            inclination_deg_step=1.0,
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
            altitude_km_min=12000.0,
            altitude_km_max=12000.0,
            altitude_km_step=1.0,
            inclination_deg_min=63.4,
            inclination_deg_max=63.4,
            inclination_deg_step=1.0,
            eccentricity_max=0.0,
            sso_inclination_mode="none",
        )
    if family == OrbitFamily.ELLIPTICAL:
        return OrbitFamilySearchParams(
            family=family,
            altitude_km_min=500.0,
            altitude_km_max=500.0,
            altitude_km_step=1.0,
            inclination_deg_min=51.6,
            inclination_deg_max=51.6,
            inclination_deg_step=1.0,
            eccentricity_max=0.1,
            sso_inclination_mode="none",
        )
    raise ValueError(f"Unsupported orbit family for defaults: {family}")


def _ordered_allowed_families(req: OrbitDesignRequest) -> Tuple[OrbitFamily, ...]:
    """Mission search order, restricted to allowed families; extras appended in request order."""
    order = mission_family_search_order(req.mission.type)
    allowed_list = list(req.optimization.allowed_orbit_families)
    allowed_set = set(allowed_list)
    out: List[OrbitFamily] = []
    for f in order:
        if f in allowed_set and f not in out:
            out.append(f)
    for f in allowed_list:
        if f not in out:
            out.append(f)
    return tuple(out)


def default_candidate_generation(req: OrbitDesignRequest) -> CandidateGenerationInput:
    """Walker grid and per-family altitude bounds (internal defaults)."""
    families = _ordered_allowed_families(req)
    if not families:
        raise ValueError("optimization.allowed_orbit_families must not be empty.")
    search = tuple(_default_family_search_params(f) for f in families)
    opt = req.optimization
    max_t = opt.max_satellites
    max_p = opt.max_planes
    t_list = [t for t in (6, 12, 18, 24) if t <= max_t]
    if not t_list:
        t_list = [min(max_t, 6)]
    p_list = [p for p in (1, 2, 3, 6) if p <= max_p]
    if not p_list:
        p_list = [1]
    wg = WalkerTopologyGrid(
        total_satellites_T=t_list,
        planes_P=p_list,
        phase_F=[0],
    )
    return CandidateGenerationInput(
        mission_type=req.mission.type,
        allowed_families=tuple(families),
        family_search=search,
        walker_grid=wg,
        max_satellites=opt.max_satellites,
        max_planes=opt.max_planes,
        epoch_seconds_tai=DEFAULT_REFERENCE_EPOCH_TAI_SECONDS,
    )


def default_designer_params(req: OrbitDesignRequest) -> DesignerParams:
    """Simulation / grid / pruning defaults derived from mission (single source of truth)."""
    continuous = req.mission.continuous_coverage_required
    return DesignerParams(
        grid_spacing_m=80_000.0,
        simulation_time_step_seconds=300.0 if continuous else 120.0,
        region_circle_vertices=24,
        early_stop_on_first_feasible_minimum_t=continuous,
        footprint_solid_angle_packing_factor=1.15,
        top_candidates_limit=10,
        grid_include_boundary=False,
        propagation_model="j2_mean_secular",
        earth_rotation_model="vallado_gmst",
    )
