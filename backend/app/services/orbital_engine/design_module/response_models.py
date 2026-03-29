"""API-facing validation outcomes for orbit design requests."""

from __future__ import annotations

from typing import List, Literal, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field

from request_models import OrbitDesignRequest


class ValidationErrorItem(BaseModel):
    """Single validation issue with JSON-pointer-friendly location."""

    model_config = ConfigDict(extra="forbid")

    loc: Tuple[Union[str, int], ...] = Field(
        description="Path to the invalid field (strings and integer indices)."
    )
    msg: str
    type: str = Field(description="Pydantic / internal error type identifier.")


class ValidationRejectedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid: Literal[False] = False
    errors: List[ValidationErrorItem]


class ValidationAcceptedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid: Literal[True] = True
    request: OrbitDesignRequest


ValidationOutcome = Union[ValidationAcceptedResponse, ValidationRejectedResponse]
