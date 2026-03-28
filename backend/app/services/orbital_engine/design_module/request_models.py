"""
Strict request contract for orbital design / regional coverage optimization.

Operational inputs (region, mission, sensor, optimization, grids, enumeration, pruning
policy) must be supplied explicitly in the request or a declared scenario file — they are
never silently invented.

Internal constants are limited to Earth physical parameters, geodetic validity bounds,
angle/unit conversion, and numerical tolerances that do not alter mission meaning.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# --- Internal constants: physical / standard geodetic bounds only (not mission defaults) ---

WGS84_LAT_MIN = -90.0
WGS84_LAT_MAX = 90.0
WGS84_LON_MIN = -180.0
WGS84_LON_MAX = 180.0


class MissionType(str, Enum):
    EMERGENCY_COMMS = "EMERGENCY_COMMS"
    EARTH_OBSERVATION = "EARTH_OBSERVATION"
    BALANCED = "BALANCED"
    BROADCAST = "BROADCAST"


class SensorModelType(str, Enum):
    COMMUNICATIONS = "communications"
    OPTICAL = "optical"
    RADAR = "radar"
    GENERIC = "generic"


class PrimaryOptimizationGoal(str, Enum):
    """Explicit optimization objectives; caller must choose."""

    MINIMIZE_TOTAL_COST = "MINIMIZE_TOTAL_COST"
    MINIMIZE_SATELLITE_COUNT = "MINIMIZE_SATELLITE_COUNT"
    MAXIMIZE_COVERAGE_FRACTION = "MAXIMIZE_COVERAGE_FRACTION"
    MINIMIZE_MAX_GAP_DURATION = "MINIMIZE_MAX_GAP_DURATION"
    MINIMIZE_MEAN_RESPONSE_LATENCY = "MINIMIZE_MEAN_RESPONSE_LATENCY"


class SecondaryOptimizationGoal(str, Enum):
    MINIMIZE_LAUNCH_MASS = "MINIMIZE_LAUNCH_MASS"
    MINIMIZE_PROPULSION_BUDGET = "MINIMIZE_PROPULSION_BUDGET"
    MAXIMIZE_REDUNDANCY = "MAXIMIZE_REDUNDANCY"
    MINIMIZE_GROUND_SEGMENT_COMPLEXITY = "MINIMIZE_GROUND_SEGMENT_COMPLEXITY"


class OrbitFamily(str, Enum):
    LEO = "LEO"
    SSO = "SSO"
    MEO = "MEO"
    GEO = "GEO"
    HEO = "HEO"
    ELLIPTICAL = "ELLIPTICAL"


class ContinuousCoverageStrategy(str, Enum):
    """
    How continuous regional coverage is judged against the simulated visibility time series.

    ``strict_24_7`` requires every grid point visible at every time step (hard predicate).
    ``high_availability`` uses coverage-fraction and optional worst-gap ceilings (engineering targets).
    """

    STRICT_24_7 = "strict_24_7"
    HIGH_AVAILABILITY = "high_availability"


class GeoJSONPolygon(BaseModel):
    """
    GeoJSON Polygon geometry (RFC 7946).
    Coordinates are in WGS84 lon/lat; altitude not supported in this contract.
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal["Polygon"]
    coordinates: List[List[List[float]]]

    @field_validator("coordinates")
    @classmethod
    def _validate_polygon_coordinates(cls, v: List[List[List[float]]]) -> List[List[List[float]]]:
        if not v:
            raise ValueError("Polygon must have at least one linear ring (exterior).")
        exterior = v[0]
        if len(exterior) < 4:
            raise ValueError(
                "Exterior ring must have at least 4 positions (closed ring: 3 vertices + closing point)."
            )
        first = exterior[0]
        last = exterior[-1]
        if first[0] != last[0] or first[1] != last[1]:
            raise ValueError("Exterior ring must be closed (first position equals last position).")
        for ring_idx, ring in enumerate(v):
            if len(ring) < 4:
                raise ValueError(f"Ring {ring_idx} must have at least 4 positions.")
            rf, rl = ring[0], ring[-1]
            if rf[0] != rl[0] or rf[1] != rl[1]:
                raise ValueError(f"Ring {ring_idx} must be closed.")
            for pt_idx, pt in enumerate(ring):
                if len(pt) < 2:
                    raise ValueError(f"Ring {ring_idx}, position {pt_idx}: need [lon, lat].")
                lon, lat = pt[0], pt[1]
                if lon < WGS84_LON_MIN or lon > WGS84_LON_MAX:
                    raise ValueError(
                        f"Longitude {lon} out of WGS84 range [{WGS84_LON_MIN}, {WGS84_LON_MAX}]."
                    )
                if lat < WGS84_LAT_MIN or lat > WGS84_LAT_MAX:
                    raise ValueError(
                        f"Latitude {lat} out of WGS84 range [{WGS84_LAT_MIN}, {WGS84_LAT_MAX}]."
                    )
        return v


class RegionPointRadius(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: Literal["point_radius"]
    lat: Annotated[float, Field(ge=WGS84_LAT_MIN, le=WGS84_LAT_MAX)]
    lon: Annotated[float, Field(ge=WGS84_LON_MIN, le=WGS84_LON_MAX)]
    radius_km: Annotated[float, Field(gt=0.0)]


class RegionPolygon(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: Literal["polygon"]
    polygon: GeoJSONPolygon


class MissionSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: MissionType
    continuous_coverage_required: bool
    analysis_horizon_hours: Annotated[float, Field(gt=0.0)]
    validation_horizon_days: Annotated[float, Field(gt=0.0)]
    continuous_coverage_strategy: ContinuousCoverageStrategy = ContinuousCoverageStrategy.STRICT_24_7
    """
    Only meaningful when ``continuous_coverage_required`` is true.
    ``high_availability`` uses ``target_*`` thresholds below.
    """
    target_min_point_coverage: Annotated[float, Field(ge=0.0, le=1.0)] = 0.995
    """
    For ``high_availability``: minimum acceptable **per-point** time fraction with visibility
    (worst cell over the grid). Ignored for ``strict_24_7``.
    """
    target_max_worst_cell_gap_seconds: Optional[float] = None
    """
    Optional: for ``high_availability``, reject if any cell's longest outage exceeds this [s].
    """

    @model_validator(mode="after")
    def _coverage_strategy_consistent(self) -> MissionSpec:
        if self.continuous_coverage_strategy == ContinuousCoverageStrategy.HIGH_AVAILABILITY:
            if not self.continuous_coverage_required:
                raise ValueError(
                    "continuous_coverage_strategy=high_availability requires continuous_coverage_required=true."
                )
        return self


class SensorModelSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: SensorModelType
    min_elevation_deg: Annotated[float, Field(ge=0.0, le=90.0)]
    sensor_half_angle_deg: Annotated[float, Field(gt=0.0, le=90.0)]
    """Half-angle of the nadir-centered access cone (payload FOV / beam) used in simulation."""
    max_off_nadir_deg: Annotated[float, Field(ge=0.0, le=90.0)]
    """
    Additional steering cap from nadir. If **0**, only ``sensor_half_angle_deg`` limits the cone.
    If **> 0**, the simulator uses ``min(sensor_half_angle_deg, max_off_nadir_deg)``.
    """
    min_access_duration_s: Annotated[float, Field(gt=0.0)]
    """Minimum contiguous ``True`` dwell in the raw link mask before a timestep counts as service."""


class OptimizationSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_goal: PrimaryOptimizationGoal
    secondary_goals: List[SecondaryOptimizationGoal]
    allowed_orbit_families: Annotated[list[OrbitFamily], Field(min_length=1)]
    max_satellites: Annotated[int, Field(ge=1)]
    max_planes: Annotated[int, Field(ge=1)]

    @model_validator(mode="after")
    def planes_vs_satellites(self) -> OptimizationSpec:
        if self.max_planes > self.max_satellites:
            raise ValueError("max_planes cannot exceed max_satellites.")
        return self


class OrbitDesignRequest(BaseModel):
    """
    Full orbital design optimization request.
    All sub-fields are required; no implicit mission defaults.
    """

    model_config = ConfigDict(extra="forbid")

    region: Annotated[Union[RegionPointRadius, RegionPolygon], Field(discriminator="mode")]
    mission: MissionSpec
    sensor_model: SensorModelSpec
    optimization: OptimizationSpec
