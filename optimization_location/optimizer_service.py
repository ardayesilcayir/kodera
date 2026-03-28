"""
Structured enumeration + pruning + coverage simulation for regional constellation design.

Deterministic: candidates are sorted (T ascending, mission family order, then P, F, altitude)
and evaluated sequentially. No random or evolutionary search in v1.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from candidate_models import (
    CandidateGenerationInput,
    WalkerConstellationCandidate,
    mission_family_search_order,
)
from coverage_objectives import mission_coverage_feasible, mission_infeasibility_reason
from coverage_service import compute_coverage_metrics
from geo_utils import llh_to_ecef
from orbit_family_service import generate_walker_candidates
from optimizer_models import CandidateEvaluation, DesignResult, DesignerParams
from propagator_service import propagate_keplerian_ecef_m
from region_service import RegionGeometry, resolve_region
from request_models import OrbitDesignRequest, RegionPointRadius, RegionPolygon
from visibility_service import effective_nadir_limit_deg, is_link_accessible

from access_duration_filter import apply_min_access_duration_mask
from footprint_prefilter import prune_candidate_by_footprint
from grid_service import GridConfig, generate_grid
from recommendation_service import build_explanations, rank_and_select_best

logger = logging.getLogger("kodera.design.optimizer")


def _walker_tpf_counts(candidates: Tuple[WalkerConstellationCandidate, ...]) -> Dict[str, int]:
    """Counts keyed as ``T|P|F`` strings for logging."""
    c = Counter(
        f"{c.total_satellites_T}|{c.planes_P}|{c.phase_F}" for c in candidates
    )
    return dict(sorted(c.items(), key=lambda kv: (kv[0],)))


def _log_candidate_enumeration(
    candidates: Tuple[WalkerConstellationCandidate, ...],
) -> None:
    n = len(candidates)
    by_family = Counter(c.family.value for c in candidates)
    by_alt = Counter(round(c.altitude_km, 3) for c in candidates)
    by_inc = Counter(round(c.inclination_deg, 4) for c in candidates)
    tpf = _walker_tpf_counts(candidates)
    logger.info(
        "design.optimizer: candidate_enumeration total=%s by_family=%s by_altitude_km=%s "
        "by_inclination_deg=%s walker_tpf_combos=%s",
        n,
        dict(sorted(by_family.items())),
        dict(sorted(by_alt.items())),
        dict(sorted(by_inc.items())),
        tpf,
    )
    if n < 5:
        logger.warning(
            "design.optimizer: small candidate_enumeration (n=%s); expand family_search "
            "altitude/inclination grids or walker_grid unless a tiny search space is intentional.",
            n,
        )


def _sort_candidates(
    candidates: Tuple[WalkerConstellationCandidate, ...],
    mission_type,
) -> List[WalkerConstellationCandidate]:
    order = mission_family_search_order(mission_type)
    fam_idx = {f: i for i, f in enumerate(order)}
    return sorted(
        candidates,
        key=lambda c: (
            c.total_satellites_T,
            fam_idx.get(c.family, 999),
            c.planes_P,
            c.phase_F,
            c.altitude_km,
            c.inclination_deg,
        ),
    )


def _resolve_region_geometry(
    region: RegionPointRadius | RegionPolygon,
    circle_vertices: int,
) -> RegionGeometry:
    return resolve_region(region, circle_vertices=circle_vertices)


def _simulate_visibility_matrix(
    candidate: WalkerConstellationCandidate,
    grid_lon_lat: NDArray[np.float64],
    horizon_seconds: float,
    time_step_seconds: float,
    min_elevation_deg: float,
    max_nadir_angle_deg: float,
    min_access_duration_s: float,
    designer_params: DesignerParams,
) -> NDArray[np.bool_]:
    """Shape (n_times, n_points). True if any satellite satisfies link geometry (el + cone)."""
    if grid_lon_lat.size == 0:
        return np.zeros((0, 0), dtype=np.bool_)

    n_pts = grid_lon_lat.shape[0]
    times = np.arange(0.0, horizon_seconds + 0.5 * time_step_seconds, time_step_seconds)
    n_t = len(times)
    out = np.zeros((n_t, n_pts), dtype=np.bool_)

    ground_ecef = np.empty((n_pts, 3), dtype=np.float64)
    for j in range(n_pts):
        lon, lat = float(grid_lon_lat[j, 0]), float(grid_lon_lat[j, 1])
        ground_ecef[j, :] = llh_to_ecef(lat, lon, 0.0)

    epoch = candidate.epoch_seconds_tai
    sats = candidate.satellites

    for ti, t in enumerate(times):
        for si, sat in enumerate(sats):
            r_sat = propagate_keplerian_ecef_m(
                sat,
                epoch,
                float(t),
                propagation_model=designer_params.propagation_model,
                earth_rotation_model=designer_params.earth_rotation_model,
            )
            for j in range(n_pts):
                if out[ti, j]:
                    continue
                if is_link_accessible(
                    r_sat,
                    ground_ecef[j],
                    min_elevation_deg,
                    max_nadir_angle_deg,
                ):
                    out[ti, j] = True
    return apply_min_access_duration_mask(out, time_step_seconds, min_access_duration_s)


def optimize_regional_coverage(
    request: OrbitDesignRequest,
    candidate_input: CandidateGenerationInput,
    designer_params: DesignerParams,
) -> DesignResult:
    """
    Enumerate Walker candidates, prune by footprint, simulate visibility, rank feasible.

    ``request`` must already satisfy the strict API contract (call ``validate_orbit_design_request`` first).
    """
    continuous_required = request.mission.continuous_coverage_required
    min_el = float(request.sensor_model.min_elevation_deg)
    max_nadir = effective_nadir_limit_deg(
        request.sensor_model.sensor_half_angle_deg,
        request.sensor_model.max_off_nadir_deg,
    )
    min_access_s = float(request.sensor_model.min_access_duration_s)
    horizon_s = float(request.mission.analysis_horizon_hours) * 3600.0
    dt = float(designer_params.simulation_time_step_seconds)

    region_geom = _resolve_region_geometry(request.region, designer_params.region_circle_vertices)
    grid = generate_grid(
        region_geom,
        GridConfig(spacing_m=designer_params.grid_spacing_m),
        include_boundary=designer_params.grid_include_boundary,
    )

    raw = generate_walker_candidates(candidate_input)
    ordered = _sort_candidates(tuple(raw), request.mission.type)
    _log_candidate_enumeration(tuple(ordered))

    evaluations: List[CandidateEvaluation] = []
    pruned_count = 0
    simulated_count = 0

    for cand in ordered:
        pr, reason = prune_candidate_by_footprint(
            cand.total_satellites_T,
            cand.altitude_km,
            min_el,
            region_geom,
            solid_angle_packing_factor=designer_params.footprint_solid_angle_packing_factor,
        )
        if pr:
            pruned_count += 1
            evaluations.append(
                CandidateEvaluation(
                    candidate=cand,
                    pruned=True,
                    prune_reason=reason,
                    metrics=None,
                    feasible=False,
                    infeasibility_reason=reason,
                )
            )
            continue

        simulated_count += 1
        vis = _simulate_visibility_matrix(
            cand,
            grid,
            horizon_s,
            dt,
            min_el,
            max_nadir,
            min_access_s,
            designer_params,
        )
        metrics = compute_coverage_metrics(vis, dt)

        if continuous_required:
            feasible = mission_coverage_feasible(metrics, request.mission)
            inf = mission_infeasibility_reason(metrics, request.mission) if not feasible else None
        else:
            feasible = True
            inf = None

        evaluations.append(
            CandidateEvaluation(
                candidate=cand,
                pruned=False,
                prune_reason=None,
                metrics=metrics,
                feasible=feasible,
                infeasibility_reason=inf,
            )
        )

        if (
            continuous_required
            and feasible
            and designer_params.early_stop_on_first_feasible_minimum_t
        ):
            break

    logger.info(
        "design.optimizer: evaluation pruned_by_footprint=%s simulated=%s total_evaluations=%s",
        pruned_count,
        simulated_count,
        len(evaluations),
    )

    ranked = rank_and_select_best(
        tuple(evaluations),
        optimization=request.optimization,
    )
    explanations = build_explanations(
        ranked,
        tuple(evaluations),
        continuous_coverage_required=continuous_required,
        mission=request.mission,
    )

    return DesignResult(
        continuous_coverage_required=continuous_required,
        recommended=ranked,
        evaluations=tuple(evaluations),
        explanations=tuple(explanations),
    )
