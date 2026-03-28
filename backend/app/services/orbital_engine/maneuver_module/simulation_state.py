"""
ORBITA-R — Simulation State
============================
Defines the internal simulation state structure that serves as the
"live data source" for the repositioning optimizer. This replaces
external APIs — all satellite states, tasks, constraints, and risk
zones come from this internal simulation environment.

Design:
  - SimulationState is the top-level container
  - All sub-structures are pure data (dataclasses)
  - validate_state() checks consistency and returns warnings
  - The state is a snapshot — it represents a single moment in simulation time
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from satellite_models import Satellite, OrbitalState


# ──────────────────────────────────────────────
# Supporting Structures
# ──────────────────────────────────────────────

@dataclass
class RegionTask:
    """
    An active coverage task assigned to a region.
    Tracks which satellites are currently assigned and the mission priority.
    """
    region_id: str
    center_lat: float
    center_lon: float
    radius_km: float
    mission_type: str                    # "communication" | "observation" | "emergency" | "balanced"
    priority: float = 1.0               # Task priority [0.0–1.0]
    assigned_satellite_ids: List[str] = field(default_factory=list)


@dataclass
class DegradationZone:
    """
    An orbital region where satellite performance is degraded.
    Examples: South Atlantic Anomaly (radiation), high-drag regions.

    Defined by altitude and inclination ranges.
    Severity 0.0 = no degradation, 1.0 = complete degradation.
    """
    alt_min_km: float
    alt_max_km: float
    incl_min_deg: float
    incl_max_deg: float
    raan_min_deg: float = 0.0
    raan_max_deg: float = 360.0
    severity: float = 0.5               # [0.0–1.0]
    description: str = ""


@dataclass
class RiskZone:
    """
    A no-fly or high-risk orbital region within the simulation.
    Examples: debris fields, conjunction-dense regions, restricted zones.

    Defined by orbital element ranges.
    """
    alt_min_km: float
    alt_max_km: float
    incl_min_deg: float
    incl_max_deg: float
    raan_min_deg: float = 0.0
    raan_max_deg: float = 360.0
    risk_type: str = "general"           # "debris" | "conjunction" | "restricted" | "general"
    severity: float = 0.5               # [0.0–1.0]
    description: str = ""


@dataclass
class PriorityPoint:
    """
    A geographic point with elevated priority for coverage.
    Examples: critical infrastructure, disaster zones, VIP targets.
    """
    lat: float
    lon: float
    priority_weight: float = 1.0        # Higher = more important
    description: str = ""


@dataclass
class HistoricalSnapshot:
    """
    A past simulation state snapshot for trend analysis.
    Stores satellite positions at a specific time for computing
    state freshness and trend-based confidence adjustments.
    """
    timestamp: datetime
    satellite_states: List[Tuple[str, OrbitalState]]  # (satellite_id, orbit_state)


@dataclass
class SystemConstraints:
    """
    Global system-level constraints that apply to the entire constellation.
    These limit what the optimizer can propose.
    """
    max_simultaneous_maneuvers: int = 1          # How many sats can maneuver at once
    min_constellation_coverage: float = 0.6       # Minimum global coverage to maintain
    max_total_risk_budget: float = 0.7            # System-wide risk tolerance
    min_satellite_separation_km: float = 50.0     # Minimum distance between satellites
    reserved_fuel_fraction: float = 0.1           # Fuel reserved for station-keeping


# ──────────────────────────────────────────────
# Simulation State
# ──────────────────────────────────────────────

@dataclass
class SimulationState:
    """
    Top-level simulation state container.

    This is the digital twin's snapshot at a given moment.
    All data the optimizer needs comes from here — no external APIs.
    """
    current_time: datetime
    active_satellites: List[Satellite]
    region_tasks: List[RegionTask] = field(default_factory=list)
    system_constraints: SystemConstraints = field(default_factory=SystemConstraints)
    degradation_zones: List[DegradationZone] = field(default_factory=list)
    risk_zones: List[RiskZone] = field(default_factory=list)
    priority_points: Optional[List[PriorityPoint]] = None
    historical_state_cache: Optional[List[HistoricalSnapshot]] = None

    def get_satellite_by_id(self, satellite_id: str) -> Optional[Satellite]:
        """Look up a satellite by its ID."""
        for sat in self.active_satellites:
            if sat.id == satellite_id:
                return sat
        return None

    def get_other_satellites(self, exclude_id: str) -> List[Satellite]:
        """Get all satellites except the specified one."""
        return [s for s in self.active_satellites if s.id != exclude_id]

    def get_tasks_for_region(self, center_lat: float, center_lon: float,
                              radius_km: float = 500.0) -> List[RegionTask]:
        """Find tasks near a geographic point."""
        from target_region import haversine_distance
        result = []
        for task in self.region_tasks:
            dist = haversine_distance(center_lat, center_lon, task.center_lat, task.center_lon)
            if dist <= radius_km + task.radius_km:
                result.append(task)
        return result


def validate_state(state: SimulationState) -> List[str]:
    """
    Validate the simulation state for consistency.

    Returns:
        List of warning messages. Empty list means the state is valid.
    """
    warnings: List[str] = []

    # Check for duplicate satellite IDs
    ids = [s.id for s in state.active_satellites]
    if len(ids) != len(set(ids)):
        warnings.append("Duplicate satellite IDs detected in active_satellites.")

    # Check satellite orbits are physically plausible
    for sat in state.active_satellites:
        orbit = sat.current_orbit
        if orbit.altitude_km < 160:
            warnings.append(
                f"Satellite '{sat.name}' altitude {orbit.altitude_km} km is below "
                f"sustainable orbit threshold (160 km). Orbit will decay rapidly."
            )
        if orbit.altitude_km > 40000:
            warnings.append(
                f"Satellite '{sat.name}' altitude {orbit.altitude_km} km is above GEO. "
                f"Mode A assumptions may not apply."
            )

    # Check degradation zones
    for zone in state.degradation_zones:
        if zone.alt_min_km >= zone.alt_max_km:
            warnings.append(
                f"DegradationZone has invalid altitude range: "
                f"[{zone.alt_min_km}, {zone.alt_max_km}]"
            )

    # Check risk zones
    for zone in state.risk_zones:
        if zone.alt_min_km >= zone.alt_max_km:
            warnings.append(
                f"RiskZone has invalid altitude range: "
                f"[{zone.alt_min_km}, {zone.alt_max_km}]"
            )

    # Check system constraints
    sc = state.system_constraints
    if sc.min_constellation_coverage > 1.0 or sc.min_constellation_coverage < 0.0:
        warnings.append("min_constellation_coverage should be in [0.0, 1.0].")

    return warnings
