from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class Point(BaseModel):
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")

class RegionInput(BaseModel):
    mode: Literal["point_radius", "polygon"]
    lat: float = 0.0
    lon: float = 0.0
    radius_km: float = 0.0
    geojson: Dict[str, Any] = {}

class MissionInput(BaseModel):
    type: Literal["EMERGENCY_COMMS", "EARTH_OBSERVATION", "BALANCED", "BROADCAST"]
    continuous_coverage_required: bool = True
    analysis_horizon_hours: int = Field(..., description="Zorunlu alan: analysis_horizon_hours kullanıcıdan gelmelidir.")
    validation_horizon_days: int = Field(..., description="Zorunlu alan: validation_horizon_days kullanıcıdan gelmelidir.")

class SensorModelInput(BaseModel):
    type: Literal["communications", "optical", "radar", "generic"]
    min_elevation_deg: float = Field(..., description="Zorunlu alan: Kullanıcı veya görev tanımı tarafından sağlanmalıdır.")
    sensor_half_angle_deg: float = Field(..., description="Zorunlu alan: Kullanıcı veya görev tanımı tarafından sağlanmalıdır.")
    max_off_nadir_deg: float = 45.0
    min_access_duration_s: int = 0

class OptimizationInput(BaseModel):
    primary_goal: str = "min_satellites"
    secondary_goals: List[str] = ["min_cost", "min_worst_gap"]
    allowed_orbit_families: List[str] = ["LEO", "MEO", "GEO", "SSO"]
    max_satellites: int = 64
    max_planes: int = 16

class DesignRequest(BaseModel):
    region: RegionInput
    mission: MissionInput
    sensor_model: SensorModelInput
    optimization: OptimizationInput

class Constraints(BaseModel):
    priority_points: Optional[List[Point]] = []
    degradation_zones: Optional[List[Point]] = []

class ScenarioRequest(BaseModel):
    region: RegionInput
    scenarioType: str
    activeSatellites: List[dict]  # Buralar detaylandırılabilir
    constraints: Optional[Constraints] = None

class CoverageAnalyzeRequest(BaseModel):
    region: RegionInput

class FailureRequest(BaseModel):
    constellation_id: str
    failed_satellite_id: str

class MinSatellitesRequest(BaseModel):
    region: RegionInput
    missionType: str
    satelliteProfile: SensorModelInput
