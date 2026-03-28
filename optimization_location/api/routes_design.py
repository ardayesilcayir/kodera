"""
POST /api/v1/design/orbit — deterministic orbit/constellation design.

Public body is a single ``OrbitDesignRequest`` (region, mission, sensor, optimization).
Candidate enumeration and designer parameters are supplied internally via ``api.default_pipeline``.
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from api.default_pipeline import default_candidate_generation, default_designer_params
from api.schemas import (
    CoverageMetricsResponse,
    DesignOrbitResponse,
    FeasibilitySummaryResponse,
    RecommendedArchitectureResponse,
    TopCandidateResponse,
)
from candidate_scoring import complexity_score, cost_score
from coverage_objectives import mission_objective_met
from designer_service import run_design
from optimizer_models import CandidateEvaluation, RankedRecommendation
from recommendation_service import list_top_candidate_evaluations
from request_models import OrbitDesignRequest
from response_models import ValidationRejectedResponse
from validation_service import validate_orbit_design_request

logger = logging.getLogger("kodera.design")

router = APIRouter(prefix="/api/v1/design", tags=["design"])


def _http422_validation_rejected(outcome: ValidationRejectedResponse) -> HTTPException:
    detail = [
        {"loc": list(e.loc), "msg": e.msg, "type": e.type}
        for e in outcome.errors
    ]
    return HTTPException(status_code=422, detail={"error": "validation_failed", "errors": detail})


def _evaluation_to_top_row(rank: int, e: CandidateEvaluation, mission) -> TopCandidateResponse:
    m = e.metrics
    assert m is not None
    c = e.candidate
    return TopCandidateResponse(
        rank=rank,
        orbit_family=c.family.value,
        altitude_km=c.altitude_km,
        inclination_deg=c.inclination_deg,
        total_satellites_T=c.total_satellites_T,
        planes_P=c.planes_P,
        phase_F=c.phase_F,
        feasible=e.feasible,
        mission_objective_met=mission_objective_met(m, mission),
        cost_score=cost_score(c),
        complexity_score=complexity_score(c),
        min_point_coverage=m.min_point_coverage,
        worst_cell_gap_seconds=m.worst_cell_gap_seconds,
    )


def _recommended_to_response(r: RankedRecommendation) -> RecommendedArchitectureResponse:
    return RecommendedArchitectureResponse(
        orbit_family=r.orbit_family.value,
        altitude_km=r.altitude_km,
        inclination_deg=r.inclination_deg,
        total_satellites_T=r.total_satellites_T,
        planes_P=r.planes_P,
        phase_F=r.phase_F,
    )


def _metrics_to_response(m, mission) -> CoverageMetricsResponse:
    return CoverageMetricsResponse(
        min_point_coverage=m.min_point_coverage,
        mean_point_coverage=m.mean_point_coverage,
        overall_coverage_ratio=m.overall_coverage_ratio,
        max_gap_seconds=m.max_gap_seconds,
        worst_cell_gap_seconds=m.worst_cell_gap_seconds,
        revisit_mean_seconds=m.revisit_mean_seconds,
        revisit_median_seconds=m.revisit_median_seconds,
        continuous_24_7_feasible=m.continuous_24_7_feasible,
        mission_objective_met=mission_objective_met(m, mission),
    )


@router.post(
    "/orbit",
    response_model=DesignOrbitResponse,
    summary="Run orbit/constellation design (single JSON body)",
)
def design_orbit(body: OrbitDesignRequest) -> DesignOrbitResponse:
    """
    Single public JSON: ``region``, ``mission``, ``sensor_model``, ``optimization``.

    Walker enumeration, altitude grids per orbit family, simulation grid spacing, and
    related parameters use **internal defaults** derived from the mission and optimization
    limits (no duplicated ``max_satellites`` fields).
    """
    logger.info("design.orbit: received job (mission=%s)", body.mission.type.value)

    first = validate_orbit_design_request(body.model_dump(mode="json"))
    if isinstance(first, ValidationRejectedResponse):
        logger.warning("design.orbit: orbit_design_request failed schema validation: %s", first.errors)
        raise _http422_validation_rejected(first)
    logger.info("design.orbit: orbit_design_request passed scientific validation")

    try:
        cgen = default_candidate_generation(body)
        dparams = default_designer_params(body)
    except ValueError as e:
        logger.warning("design.orbit: default pipeline invalid: %s", e)
        raise HTTPException(
            status_code=422,
            detail={"error": "invalid_pipeline_parameters", "message": str(e)},
        ) from e

    try:
        result = run_design(
            body,
            cgen,
            dparams,
            validate_request=False,
        )
    except ValueError as e:
        logger.warning("design.orbit: run_design rejected: %s", e)
        raise HTTPException(
            status_code=422,
            detail={"error": "design_input_inconsistent", "message": str(e)},
        ) from e

    logger.info(
        "design.orbit: optimization complete evaluations=%s recommended=%s",
        len(result.evaluations),
        result.recommended is not None,
    )

    pruned = sum(1 for e in result.evaluations if e.pruned)
    sim_bad = sum(
        1
        for e in result.evaluations
        if not e.pruned and e.metrics and result.continuous_coverage_required and not e.feasible
    )

    top_evals: List[CandidateEvaluation] = list_top_candidate_evaluations(
        result.evaluations,
        continuous_coverage_required=result.continuous_coverage_required,
        limit=dparams.top_candidates_limit,
        optimization=body.optimization,
    )
    top_rows = [_evaluation_to_top_row(i + 1, e, body.mission) for i, e in enumerate(top_evals)]

    rec_arch = None
    cov = None
    if result.recommended is not None:
        rec_arch = _recommended_to_response(result.recommended)
        cov = _metrics_to_response(result.recommended.metrics, body.mission)

    recommended_feasible = result.recommended is not None
    if result.continuous_coverage_required and result.recommended is not None:
        recommended_feasible = mission_objective_met(result.recommended.metrics, body.mission)

    return DesignOrbitResponse(
        recommended_architecture=rec_arch,
        top_candidates=top_rows,
        feasibility_summary=FeasibilitySummaryResponse(
            continuous_coverage_required=result.continuous_coverage_required,
            continuous_coverage_strategy=body.mission.continuous_coverage_strategy.value,
            recommended_feasible=recommended_feasible,
            total_candidates_evaluated=len(result.evaluations),
            pruned_by_footprint=pruned,
            simulated_continuous_infeasible=sim_bad,
        ),
        coverage_metrics=cov,
        explanation=list(result.explanations),
    )
