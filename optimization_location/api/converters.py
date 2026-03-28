"""Convert API payloads to internal frozen dataclasses."""

from __future__ import annotations

from candidate_models import (
    CandidateGenerationInput,
    OrbitFamilySearchParams,
    WalkerTopologyGrid,
)
from optimizer_models import DesignerParams

from api.schemas import CandidateGenerationPayload, DesignerParamsPayload


def candidate_generation_from_payload(p: CandidateGenerationPayload) -> CandidateGenerationInput:
    search = tuple(
        OrbitFamilySearchParams(
            family=x.family,
            altitude_km_min=x.altitude_km_min,
            altitude_km_max=x.altitude_km_max,
            altitude_km_step=x.altitude_km_step,
            inclination_deg_min=x.inclination_deg_min,
            inclination_deg_max=x.inclination_deg_max,
            inclination_deg_step=x.inclination_deg_step,
            eccentricity_max=x.eccentricity_max,
            sso_inclination_mode=x.sso_inclination_mode,
        )
        for x in p.family_search
    )
    wg = WalkerTopologyGrid(
        total_satellites_T=list(p.walker_grid.total_satellites_T),
        planes_P=list(p.walker_grid.planes_P),
        phase_F=list(p.walker_grid.phase_F),
    )
    return CandidateGenerationInput(
        mission_type=p.mission_type,
        allowed_families=tuple(p.allowed_families),
        family_search=search,
        walker_grid=wg,
        max_satellites=p.max_satellites,
        max_planes=p.max_planes,
        epoch_seconds_tai=p.epoch_seconds_tai,
    )


def designer_params_from_payload(p: DesignerParamsPayload) -> DesignerParams:
    return DesignerParams(
        grid_spacing_m=p.grid_spacing_m,
        simulation_time_step_seconds=p.simulation_time_step_seconds,
        region_circle_vertices=p.region_circle_vertices,
        early_stop_on_first_feasible_minimum_t=p.early_stop_on_first_feasible_minimum_t,
        footprint_solid_angle_packing_factor=p.footprint_solid_angle_packing_factor,
        top_candidates_limit=p.top_candidates_limit,
        grid_include_boundary=p.grid_include_boundary,
        propagation_model=p.propagation_model,
        earth_rotation_model=p.earth_rotation_model,
    )
