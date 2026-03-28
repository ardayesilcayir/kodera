"""
End-to-end regional constellation designer: validate request → enumerate → simulate → recommend.

Local-only; no HTTP or external APIs. Callers supply explicit candidate enumeration
(``CandidateGenerationInput``) alongside the validated API request.
"""

from __future__ import annotations

from candidate_models import CandidateGenerationInput
from optimizer_models import DesignResult, DesignerParams
from optimizer_service import optimize_regional_coverage
from request_models import OrbitDesignRequest
from response_models import ValidationRejectedResponse
from validation_service import validate_orbit_design_request


def run_design(
    request: OrbitDesignRequest,
    candidate_input: CandidateGenerationInput,
    designer_params: DesignerParams,
    *,
    validate_request: bool = True,
) -> DesignResult:
    """
    Run the full deterministic design pipeline.

    Raises
    ------
    ValueError
        If the request fails strict validation or optimization inputs are inconsistent.

    Parameters
    ----------
    validate_request
        If ``False``, skip ``validate_orbit_design_request`` (caller already validated).
    """
    if validate_request:
        outcome = validate_orbit_design_request(request.model_dump(mode="json"))
        if isinstance(outcome, ValidationRejectedResponse):
            msgs = "; ".join(f"{'/'.join(str(x) for x in e.loc)}: {e.msg}" for e in outcome.errors)
            raise ValueError(f"Orbit design request invalid: {msgs}")

    if candidate_input.max_satellites != request.optimization.max_satellites:
        raise ValueError(
            "candidate_input.max_satellites must match request.optimization.max_satellites."
        )
    if candidate_input.max_planes != request.optimization.max_planes:
        raise ValueError(
            "candidate_input.max_planes must match request.optimization.max_planes."
        )
    if set(candidate_input.allowed_families) != set(request.optimization.allowed_orbit_families):
        raise ValueError(
            "candidate_input.allowed_families must match request.optimization.allowed_orbit_families."
        )
    if candidate_input.mission_type != request.mission.type:
        raise ValueError("candidate_input.mission_type must match request.mission.type.")

    return optimize_regional_coverage(request, candidate_input, designer_params)
