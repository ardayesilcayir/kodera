"""
Strict validation entrypoint for orbit design requests.

Rejects incomplete or physically inconsistent inputs with structured errors.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Union

from pydantic import ValidationError

from request_models import OrbitDesignRequest
from response_models import (
    ValidationAcceptedResponse,
    ValidationErrorItem,
    ValidationRejectedResponse,
)


def _payload_to_dict(payload: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}") from e
        if not isinstance(parsed, dict):
            raise ValueError("Top-level JSON value must be an object.")
        return parsed
    return payload


def _pydantic_errors_to_items(exc: ValidationError) -> List[ValidationErrorItem]:
    items: List[ValidationErrorItem] = []
    for err in exc.errors():
        loc_raw = err.get("loc") or ()
        loc = tuple(loc_raw)
        items.append(
            ValidationErrorItem(
                loc=loc,
                msg=err.get("msg", "Validation error"),
                type=str(err.get("type", "value_error")),
            )
        )
    return items


def validate_orbit_design_request(
    payload: Union[Dict[str, Any], str],
) -> Union[ValidationAcceptedResponse, ValidationRejectedResponse]:
    """
    Parse and validate an orbit design request.

    Returns a structured acceptance or rejection. No silent defaults are applied
    beyond Pydantic coercions where types are unambiguous (e.g. int fields);
    required fields must be present explicitly.
    """
    try:
        data = _payload_to_dict(payload)
    except ValueError as e:
        return ValidationRejectedResponse(
            errors=[
                ValidationErrorItem(loc=(), msg=str(e), type="parse_error"),
            ],
        )

    try:
        request = OrbitDesignRequest.model_validate(data)
    except ValidationError as e:
        return ValidationRejectedResponse(errors=_pydantic_errors_to_items(e))

    return ValidationAcceptedResponse(request=request)


def request_json_schema() -> Dict[str, Any]:
    """JSON Schema for ``OrbitDesignRequest`` (validation mode)."""
    return OrbitDesignRequest.model_json_schema()


def validation_accepted_json_schema() -> Dict[str, Any]:
    return ValidationAcceptedResponse.model_json_schema()


def validation_rejected_json_schema() -> Dict[str, Any]:
    return ValidationRejectedResponse.model_json_schema()
