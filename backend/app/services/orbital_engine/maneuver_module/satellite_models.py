"""
ORBITA-R — Satellite Models & Physical Constants
=================================================
Core data models for orbital states, satellite capabilities, mission constraints,
and repositioning plan results. All physical constants use SI-compatible units
with km/s/deg conventions standard in astrodynamics.

Physical basis:
  - Keplerian two-body orbital elements (circular orbit simplification for Mode A)
  - WGS84 Earth reference ellipsoid parameters
  - Standard gravitational parameter μ for Earth
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ──────────────────────────────────────────────
# Physical constants
# ──────────────────────────────────────────────

MU_EARTH: float = 398600.4418  # km^3/s^2 — Earth standard gravitational parameter
R_EARTH: float = 6371.0        # km — Mean Earth radius (spherical approx for Mode A)
R_EARTH_EQUATORIAL: float = 6378.137   # km — WGS84 semi-major axis
EARTH_FLATTENING: float = 1.0 / 298.257223563  # WGS84 flattening
EARTH_ROTATION_RAD_PER_SEC: float = 7.2921159e-5  # rad/s — Earth sidereal rotation rate
EARTH_ROTATION_DEG_PER_SEC: float = math.degrees(EARTH_ROTATION_RAD_PER_SEC)

# Conversion helpers
DEG_TO_RAD: float = math.pi / 180.0
RAD_TO_DEG: float = 180.0 / math.pi


# ──────────────────────────────────────────────
# Orbital mechanics helpers
# ──────────────────────────────────────────────

def orbital_velocity(altitude_km: float) -> float:
    """
    Circular orbital velocity at a given altitude above Earth's surface.

    v = sqrt(μ / r)  where  r = R_earth + altitude

    Returns:
        Velocity in km/s.
    """
    r = R_EARTH + altitude_km
    return math.sqrt(MU_EARTH / r)


def orbital_period(altitude_km: float) -> float:
    """
    Orbital period for a circular orbit at a given altitude.

    T = 2π * sqrt(r³ / μ)

    Returns:
        Period in seconds.
    """
    r = R_EARTH + altitude_km
    return 2.0 * math.pi * math.sqrt(r ** 3 / MU_EARTH)


def orbital_period_minutes(altitude_km: float) -> float:
    """Orbital period in minutes."""
    return orbital_period(altitude_km) / 60.0


def hohmann_delta_v(alt1_km: float, alt2_km: float) -> Tuple[float, float, float]:
    """
    Compute the two impulse burns and total Δv for a Hohmann transfer
    between two circular orbits.

    Uses the vis-viva equation:
        v² = μ(2/r - 1/a)

    Args:
        alt1_km: Initial circular orbit altitude (km).
        alt2_km: Final circular orbit altitude (km).

    Returns:
        (dv1, dv2, dv_total) in km/s.
    """
    r1 = R_EARTH + alt1_km
    r2 = R_EARTH + alt2_km
    a_transfer = (r1 + r2) / 2.0

    # Circular velocities
    v1 = math.sqrt(MU_EARTH / r1)
    v2 = math.sqrt(MU_EARTH / r2)

    # Transfer ellipse velocities at periapsis and apoapsis
    v_transfer_periapsis = math.sqrt(MU_EARTH * (2.0 / r1 - 1.0 / a_transfer))
    v_transfer_apoapsis = math.sqrt(MU_EARTH * (2.0 / r2 - 1.0 / a_transfer))

    dv1 = abs(v_transfer_periapsis - v1)
    dv2 = abs(v2 - v_transfer_apoapsis)

    return dv1, dv2, dv1 + dv2


def hohmann_transfer_time(alt1_km: float, alt2_km: float) -> float:
    """
    Time for a Hohmann transfer (half the period of the transfer ellipse).

    t = π * sqrt(a_transfer³ / μ)

    Returns:
        Transfer time in seconds.
    """
    r1 = R_EARTH + alt1_km
    r2 = R_EARTH + alt2_km
    a_transfer = (r1 + r2) / 2.0
    return math.pi * math.sqrt(a_transfer ** 3 / MU_EARTH)


def inclination_change_delta_v(altitude_km: float, delta_inc_deg: float) -> float:
    """
    Δv required for a pure inclination change at a given altitude.

    Δv = 2v·sin(Δi/2)

    This is the most expensive orbital maneuver type per degree.

    Args:
        altitude_km: Altitude where the maneuver is performed (km).
        delta_inc_deg: Inclination change in degrees.

    Returns:
        Δv in km/s.
    """
    v = orbital_velocity(altitude_km)
    delta_inc_rad = abs(delta_inc_deg) * DEG_TO_RAD
    return 2.0 * v * math.sin(delta_inc_rad / 2.0)


def combined_plane_change_delta_v(
    altitude_km: float,
    delta_inc_deg: float,
    delta_raan_deg: float,
) -> float:
    """
    Approximate Δv for a combined inclination + RAAN plane change.

    For Mode A, we treat the total plane change angle as the vector sum
    of the inclination and RAAN components projected onto the velocity sphere.

    This is an approximation — in reality, the optimal combined maneuver
    depends on the specific geometry. We use the spherical law of cosines
    to compute the total angular change between the two orbital planes.

    θ = arccos(cos(Δi)·cos(ΔΩ·sin(i_avg)) )
    Simplified: θ ≈ sqrt(Δi² + (ΔΩ·sin(i_avg))²) for small angles

    For Mode A we use a simpler conservative estimate.

    Returns:
        Δv in km/s.
    """
    if abs(delta_inc_deg) < 0.01 and abs(delta_raan_deg) < 0.01:
        return 0.0

    v = orbital_velocity(altitude_km)

    # Total plane change angle — simplified combination
    # RAAN change cost depends on inclination (RAAN changes are cheaper at high inc)
    # We weight RAAN contribution by sin(average_inclination)
    di_rad = abs(delta_inc_deg) * DEG_TO_RAD
    # For RAAN cost estimation, use a moderate inclination assumption
    # In Mode A, we use a simplified scaling factor
    draan_rad = abs(delta_raan_deg) * DEG_TO_RAD
    raan_effective = draan_rad * 0.5  # Conservative scaling for Mode A

    total_angle = math.sqrt(di_rad ** 2 + raan_effective ** 2)
    total_angle = min(total_angle, math.pi)  # Cap at 180°

    return 2.0 * v * math.sin(total_angle / 2.0)


# ──────────────────────────────────────────────
# Data Models
# ──────────────────────────────────────────────

@dataclass
class OrbitalState:
    """
    Keplerian orbital elements for a satellite.

    For Mode A (circular orbit approximation), eccentricity is ~0.
    Phase represents the satellite's current position along the orbit
    (analogous to true anomaly for circular orbits).
    """
    altitude_km: float          # Orbital altitude above Earth surface
    inclination_deg: float      # Orbital inclination [0, 180]
    raan_deg: float             # Right Ascension of Ascending Node [0, 360)
    phase_deg: float            # Current true anomaly / phase angle [0, 360)
    eccentricity: float = 0.0  # Default circular orbit

    def __post_init__(self):
        """Validate physical bounds."""
        if self.altitude_km < 0:
            raise ValueError(f"Altitude must be non-negative, got {self.altitude_km}")
        if not 0 <= self.inclination_deg <= 180:
            raise ValueError(f"Inclination must be in [0, 180], got {self.inclination_deg}")
        if not 0 <= self.eccentricity < 1:
            raise ValueError(f"Eccentricity must be in [0, 1), got {self.eccentricity}")
        # Normalize angles to [0, 360)
        self.raan_deg = self.raan_deg % 360.0
        self.phase_deg = self.phase_deg % 360.0

    @property
    def radius_km(self) -> float:
        """Orbital radius from Earth center (km)."""
        return R_EARTH + self.altitude_km

    @property
    def velocity_km_s(self) -> float:
        """Circular orbital velocity (km/s)."""
        return orbital_velocity(self.altitude_km)

    @property
    def period_seconds(self) -> float:
        """Orbital period (seconds)."""
        return orbital_period(self.altitude_km)

    @property
    def period_minutes(self) -> float:
        """Orbital period (minutes)."""
        return self.period_seconds / 60.0


@dataclass
class SatelliteCapabilities:
    """
    Operational capabilities of a satellite.
    All scores are normalized to [0.0, 1.0].
    """
    mission_type: str                # "communication" | "observation" | "emergency" | "balanced"
    coverage_radius_km: float        # Effective coverage footprint radius
    min_elevation_deg: float = 10.0  # Minimum elevation angle for usable link
    bandwidth: float = 0.5           # Normalized [0.0–1.0]
    reliability: float = 0.8         # Normalized [0.0–1.0]
    maneuver_capacity_score: float = 0.5  # Normalized [0.0–1.0]
    fuel_or_budget_score: float = 0.5     # Normalized [0.0–1.0]

    def __post_init__(self):
        valid_mission_types = {"communication", "observation", "emergency", "balanced"}
        if self.mission_type not in valid_mission_types:
            raise ValueError(
                f"mission_type must be one of {valid_mission_types}, got '{self.mission_type}'"
            )
        for attr_name in ["bandwidth", "reliability", "maneuver_capacity_score", "fuel_or_budget_score"]:
            val = getattr(self, attr_name)
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{attr_name} must be in [0.0, 1.0], got {val}")


@dataclass
class Satellite:
    """Full satellite definition with orbit state and capabilities."""
    id: str
    name: str
    current_orbit: OrbitalState
    capabilities: SatelliteCapabilities
    priority: float = 1.0  # Relative priority [0.0–1.0]


@dataclass
class MissionConstraints:
    """User-specified constraints on the repositioning operation."""
    max_transfer_time_hours: float = 48.0      # Maximum acceptable transfer time
    max_orbit_change_score: float = 0.8         # Cap on normalized transfer cost
    min_elevation_deg: float = 10.0             # Minimum elevation angle
    optimization_mode: str = "balanced"          # "efficiency" | "coverage" | "balanced" | "speed"

    def __post_init__(self):
        valid_modes = {"efficiency", "coverage", "balanced", "speed"}
        if self.optimization_mode not in valid_modes:
            raise ValueError(
                f"optimization_mode must be one of {valid_modes}, got '{self.optimization_mode}'"
            )


@dataclass
class TransferSummary:
    """Results of transfer cost analysis between two orbits."""
    delta_v_altitude_km_s: float     # Δv for altitude change (Hohmann)
    delta_v_inclination_km_s: float  # Δv for inclination change
    delta_v_total_km_s: float        # Total estimated Δv
    transfer_time_seconds: float     # Estimated transfer duration
    transfer_time_hours: float       # Transfer duration in hours
    transfer_cost_score: float       # Normalized cost score [0, 1]
    altitude_change_km: float        # Absolute altitude difference
    inclination_change_deg: float    # Absolute inclination difference
    raan_change_deg: float           # Absolute RAAN difference
    raan_cost_score: float           # RAAN change cost component [0, 1]


@dataclass
class CoverageMetrics:
    """All coverage-related scores for a repositioning plan."""
    target_region_coverage: float   # Fraction of target covered [0, 1]
    coverage_gain: float            # Improvement vs current orbit [-1, 1]
    continuity_score: float         # Fraction of orbit with coverage [0, 1]
    revisit_score: float            # Normalized passes/day [0, 1]


@dataclass
class SystemImpactAnalysis:
    """Constellation-level impact of the repositioning."""
    redundancy_score: float        # Other satellites covering region [0, 1]
    overlap_penalty: float         # Excess duplicate coverage [0, 1]
    gap_reduction: float           # Coverage gap filled [0, 1]
    strategic_fit_score: float     # Mission-type + constellation balance [0, 1]
    constellation_balance: float   # Geographic distribution metric [0, 1]


@dataclass
class RiskAnalysis:
    """Multi-factor risk assessment."""
    zone_risk: float               # Risk from degradation/risk zones [0, 1]
    proximity_risk: float          # Collision risk proxy [0, 1]
    satellite_risk: float          # From reliability/fuel/capacity [0, 1]
    transfer_risk: float           # Risk of the transfer itself [0, 1]
    total_risk_score: float        # Combined risk [0, 1]
    risk_factors: List[str] = field(default_factory=list)  # Human-readable risk factors


@dataclass
class RepositionPlan:
    """A complete repositioning plan for a single candidate orbit."""
    rank: int
    target_orbit: OrbitalState
    transfer_summary: TransferSummary
    coverage_metrics: CoverageMetrics
    system_impact: SystemImpactAnalysis
    risk_analysis: RiskAnalysis
    explanation: str
    confidence_score: float
    feasibility_score: float
    limitations: List[str]
    final_score: float
    score_breakdown: Dict[str, float]
    operational_status: str
    violated_constraints: List[str]


@dataclass
class RepositionResult:
    """Top-level result containing best and alternative plans."""
    best_plan: RepositionPlan
    alternative_plans: List[RepositionPlan]
    total_candidates_evaluated: int
    optimization_mode: str
    best_feasible_plan: Optional[RepositionPlan] = None
    model_mode: str = "MODE_A"  # "MODE_A" or "MODE_B" (future)
    summary: str = ""
