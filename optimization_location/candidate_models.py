"""
Constellation candidate specifications for downstream coverage evaluation.

Numeric sampling ranges are **not** defaulted in this module; HTTP callers use
``api.default_pipeline`` to build ``CandidateGenerationInput`` from ``OrbitDesignRequest``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Tuple

from request_models import MissionType, OrbitFamily


@dataclass(frozen=True)
class OrbitFamilySearchParams:
    """
    Explicit sampling bounds for one orbit family (caller-defined; no implicit mission defaults).
    """

    family: OrbitFamily
    altitude_km_min: float
    altitude_km_max: float
    altitude_km_step: float
    inclination_deg_min: float
    inclination_deg_max: float
    inclination_deg_step: float
    eccentricity_max: float
    sso_inclination_mode: Literal["none", "mean_sun_synchronous"]
    """
    For ``SSO``: ``mean_sun_synchronous`` uses J2-based mean sun-sync inclination from altitude.
    For other families must be ``none`` (inclination grid is used).
    """

    def __post_init__(self) -> None:
        if self.altitude_km_min <= 0.0 or self.altitude_km_max < self.altitude_km_min:
            raise ValueError("Invalid altitude bounds.")
        if self.altitude_km_step <= 0.0:
            raise ValueError("altitude_km_step must be positive.")
        if self.inclination_deg_step <= 0.0:
            raise ValueError("inclination_deg_step must be positive.")
        if not (0.0 <= self.eccentricity_max < 0.2):
            raise ValueError("MVP supports eccentricity_max in [0, 0.2).")
        if self.family != OrbitFamily.SSO and self.sso_inclination_mode != "none":
            raise ValueError("sso_inclination_mode is only valid for SSO.")


@dataclass(frozen=True)
class WalkerTopologyGrid:
    """
    Discrete Walker topologies to enumerate (T, P, F).

    ``F`` values must be in ``[0, P-1]`` for Walker Delta; enforced in ``walker_service``.
    """

    total_satellites_T: List[int]
    planes_P: List[int]
    phase_F: List[int]


@dataclass(frozen=True)
class CandidateGenerationInput:
    """Everything needed to expand Walker candidates (no implicit numeric defaults)."""

    mission_type: MissionType
    allowed_families: Tuple[OrbitFamily, ...]
    family_search: Tuple[OrbitFamilySearchParams, ...]
    walker_grid: WalkerTopologyGrid
    max_satellites: int
    max_planes: int
    epoch_seconds_tai: float
    """Common epoch for all Keplerian elements (seconds, TAI-like absolute scale)."""


@dataclass(frozen=True)
class SatelliteKeplerianECI:
    """Circular / near-circular Keplerian elements in Earth-centered inertial frame."""

    semi_major_axis_m: float
    eccentricity: float
    inclination_rad: float
    raan_rad: float
    arg_of_perigee_rad: float
    mean_anomaly_at_epoch_rad: float


@dataclass(frozen=True)
class WalkerConstellationCandidate:
    """
    One physically plausible Walker-like constellation (uniform RAAN, consistent phasing).
    """

    family: OrbitFamily
    altitude_km: float
    inclination_deg: float
    eccentricity: float
    total_satellites_T: int
    planes_P: int
    phase_F: int
    satellites_per_plane_S: int
    epoch_seconds_tai: float
    satellites: Tuple[SatelliteKeplerianECI, ...] = field(repr=False)


def mission_family_search_order(mission_type: MissionType) -> Tuple[OrbitFamily, ...]:
    """
    Mission-aware **ordering** of orbit families for enumeration (search priority only).

    Does not supply numeric altitude/inclination defaults.
    """
    if mission_type == MissionType.EMERGENCY_COMMS:
        return (OrbitFamily.LEO, OrbitFamily.SSO, OrbitFamily.MEO, OrbitFamily.GEO)
    if mission_type == MissionType.EARTH_OBSERVATION:
        return (OrbitFamily.SSO, OrbitFamily.LEO)
    if mission_type == MissionType.BROADCAST:
        return (OrbitFamily.GEO,)
    if mission_type == MissionType.BALANCED:
        return (OrbitFamily.LEO, OrbitFamily.MEO, OrbitFamily.GEO)
    raise ValueError(f"Unsupported mission type: {mission_type}")
