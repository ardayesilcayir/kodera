"""
ORBITA-R — Coverage Engine
============================
Computes satellite coverage over target regions using physically-grounded
footprint and ground track calculations.

Physical model (Mode A):
  - Circular orbit assumption
  - Spherical Earth for ground track projection
  - Earth rotation included for realistic longitude drift
  - Minimum elevation angle constraint for satellite-to-ground visibility
  - Haversine distance for ground coverage checks

Key equations:
  - Footprint half-angle: η = arccos(R/(R+h) · cos(ε)) - ε
  - Footprint radius: r_foot = R_earth · η
  - Sub-satellite latitude: lat_ss = arcsin(sin(i) · sin(u))
  - Sub-satellite longitude: lon_ss = Ω + atan2(cos(i)·sin(u), cos(u)) - ω_earth·t

  Where:
    R = Earth radius, h = altitude, ε = min elevation angle
    i = inclination, u = argument of latitude, Ω = RAAN
    ω_earth = Earth rotation rate, t = time since epoch
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .satellite_models import (
    OrbitalState, R_EARTH, MU_EARTH, DEG_TO_RAD, RAD_TO_DEG,
    EARTH_ROTATION_RAD_PER_SEC, orbital_period,
)
from .target_region import TargetRegion, haversine_distance, sample_region_points


# ──────────────────────────────────────────────
# Footprint Computation
# ──────────────────────────────────────────────

def compute_footprint_half_angle(altitude_km: float, min_elevation_deg: float) -> float:
    """
    Compute the Earth central angle subtended by the satellite footprint.

    The footprint is the area on Earth's surface visible to the satellite
    above a minimum elevation angle.

    η = arccos(R/(R+h) · cos(ε)) - ε

    Where:
      R = Earth radius
      h = satellite altitude
      ε = minimum elevation angle

    Args:
        altitude_km: Satellite altitude above Earth surface (km).
        min_elevation_deg: Minimum elevation angle (degrees).

    Returns:
        Footprint half-angle in radians.
    """
    r = R_EARTH + altitude_km
    eps = min_elevation_deg * DEG_TO_RAD

    cos_eta = (R_EARTH / r) * math.cos(eps)
    # Clamp to avoid domain errors
    cos_eta = max(-1.0, min(1.0, cos_eta))

    eta = math.acos(cos_eta) - eps
    return max(eta, 0.0)


def compute_footprint_radius_km(altitude_km: float, min_elevation_deg: float) -> float:
    """
    Compute the footprint radius on Earth's surface in km.

    r_footprint = R_earth · η

    Args:
        altitude_km: Satellite altitude (km).
        min_elevation_deg: Minimum elevation angle (degrees).

    Returns:
        Footprint radius in km.
    """
    eta = compute_footprint_half_angle(altitude_km, min_elevation_deg)
    return R_EARTH * eta


# ──────────────────────────────────────────────
# Ground Track Computation
# ──────────────────────────────────────────────

def compute_subsatellite_point(orbit: OrbitalState, time_offset_sec: float = 0.0) -> Tuple[float, float]:
    """
    Compute the sub-satellite point (ground projection) at a given time.

    For a circular orbit:
      - Argument of latitude: u = phase + (2π/T)·t
      - Latitude: φ = arcsin(sin(i) · sin(u))
      - Longitude: λ = Ω + atan2(cos(i)·sin(u), cos(u)) - ω_earth·t

    Args:
        orbit: Orbital state.
        time_offset_sec: Time offset from epoch (seconds).

    Returns:
        (latitude_deg, longitude_deg) of the sub-satellite point.
    """
    T = orbital_period(orbit.altitude_km)
    omega = 2.0 * math.pi / T  # Mean angular velocity (rad/s)

    i = orbit.inclination_deg * DEG_TO_RAD
    raan = orbit.raan_deg * DEG_TO_RAD
    phase0 = orbit.phase_deg * DEG_TO_RAD

    # Argument of latitude at time t
    u = phase0 + omega * time_offset_sec

    # Sub-satellite latitude
    sin_lat = math.sin(i) * math.sin(u)
    sin_lat = max(-1.0, min(1.0, sin_lat))
    lat = math.asin(sin_lat)

    # Sub-satellite longitude (accounting for Earth rotation)
    lon = raan + math.atan2(math.cos(i) * math.sin(u), math.cos(u))
    lon -= EARTH_ROTATION_RAD_PER_SEC * time_offset_sec

    # Normalize longitude to [-π, π]
    lon = ((lon + math.pi) % (2.0 * math.pi)) - math.pi

    return lat * RAD_TO_DEG, lon * RAD_TO_DEG


def compute_ground_track(
    orbit: OrbitalState,
    n_points: int = 360,
    n_periods: float = 1.0,
) -> List[Tuple[float, float]]:
    """
    Compute the ground track of a satellite over a specified number of orbital periods.

    Args:
        orbit: Orbital state.
        n_points: Number of sample points along the track.
        n_periods: Number of orbital periods to compute.

    Returns:
        List of (lat_deg, lon_deg) tuples along the ground track.
    """
    T = orbital_period(orbit.altitude_km)
    total_time = T * n_periods
    dt = total_time / n_points

    track = []
    for k in range(n_points):
        t = k * dt
        lat, lon = compute_subsatellite_point(orbit, t)
        track.append((lat, lon))

    return track


# ──────────────────────────────────────────────
# Coverage Analysis
# ──────────────────────────────────────────────

def compute_target_coverage(
    orbit: OrbitalState,
    region: TargetRegion,
    min_elevation_deg: float = 10.0,
    n_track_points: int = 720,
    n_region_samples: int = 50,
    n_periods: float = 1.0,
) -> float:
    """
    Compute the fraction of a target region covered by a satellite in one full orbit.

    Method:
      1. Sample ground points in the target region.
      2. Compute the satellite ground track over one (or more) orbital period(s).
      3. For each sample point, check if any ground track point is within footprint radius.
      4. Coverage = fraction of sample points that are covered.

    Args:
        orbit: Satellite orbital state.
        region: Target region.
        min_elevation_deg: Minimum elevation angle.
        n_track_points: Number of ground track sample points.
        n_region_samples: Number of region sample points.
        n_periods: Number of orbital periods.

    Returns:
        Coverage fraction [0.0, 1.0].
    """
    footprint_radius = compute_footprint_radius_km(orbit.altitude_km, min_elevation_deg)
    region_points = sample_region_points(region, n_region_samples)
    track = compute_ground_track(orbit, n_track_points, n_periods)

    if not region_points or not track:
        return 0.0

    covered_count = 0
    for rlat, rlon in region_points:
        for tlat, tlon in track:
            dist = haversine_distance(rlat, rlon, tlat, tlon)
            if dist <= footprint_radius:
                covered_count += 1
                break  # Point is covered, no need to check more track points

    return covered_count / len(region_points)


def compute_coverage_gain(
    current_orbit: OrbitalState,
    candidate_orbit: OrbitalState,
    region: TargetRegion,
    min_elevation_deg: float = 10.0,
) -> float:
    """
    Compute the coverage improvement from moving to a candidate orbit.

    coverage_gain = new_coverage - current_coverage

    Returns:
        Coverage gain in [-1.0, 1.0]. Positive means improvement.
    """
    current_cov = compute_target_coverage(current_orbit, region, min_elevation_deg)
    new_cov = compute_target_coverage(candidate_orbit, region, min_elevation_deg)
    return new_cov - current_cov


def compute_continuity_score(
    orbit: OrbitalState,
    region: TargetRegion,
    min_elevation_deg: float = 10.0,
    n_time_samples: int = 360,
) -> float:
    """
    Compute the fraction of the orbital period during which the satellite
    has continuous coverage of the target region center.

    This measures how long per orbit the satellite can maintain a link/view.

    Returns:
        Continuity score [0.0, 1.0].
    """
    T = orbital_period(orbit.altitude_km)
    footprint_radius = compute_footprint_radius_km(orbit.altitude_km, min_elevation_deg)

    visible_count = 0
    for k in range(n_time_samples):
        t = (k / n_time_samples) * T
        lat, lon = compute_subsatellite_point(orbit, t)
        dist = haversine_distance(lat, lon, region.center_lat, region.center_lon)
        if dist <= footprint_radius:
            visible_count += 1

    return visible_count / n_time_samples


def compute_revisit_score(
    orbit: OrbitalState,
    region: TargetRegion,
    min_elevation_deg: float = 10.0,
    mission_type: str = "balanced",
    n_time_samples: int = 1440,
    analysis_hours: float = 24.0,
) -> float:
    """
    Compute a normalized revisit score based on how many distinct passes
    the satellite makes over the target region in a 24-hour period.

    A "pass" is defined as a transition from not-visible to visible.

    The raw pass count is normalized against mission-type ideals:
      - observation: 8+ passes/day is ideal
      - communication: 4+ passes/day is ideal
      - emergency: 12+ passes/day is ideal
      - balanced: 6+ passes/day is ideal

    Returns:
        Revisit score [0.0, 1.0].
    """
    mission_ideal_passes = {
        "observation": 8.0,
        "communication": 4.0,
        "emergency": 12.0,
        "balanced": 6.0,
    }
    ideal = mission_ideal_passes.get(mission_type, 6.0)

    T = orbital_period(orbit.altitude_km)
    total_time = analysis_hours * 3600.0
    dt = total_time / n_time_samples
    footprint_radius = compute_footprint_radius_km(orbit.altitude_km, min_elevation_deg)

    passes = 0
    was_visible = False

    for k in range(n_time_samples):
        t = k * dt
        lat, lon = compute_subsatellite_point(orbit, t)
        dist = haversine_distance(lat, lon, region.center_lat, region.center_lon)
        is_visible = dist <= footprint_radius

        if is_visible and not was_visible:
            passes += 1
        was_visible = is_visible

    return min(passes / ideal, 1.0)


# ──────────────────────────────────────────────
# Aggregated Coverage Result
# ──────────────────────────────────────────────

@dataclass
class CoverageResult:
    """Complete coverage analysis result."""
    target_coverage: float       # [0, 1]
    coverage_gain: float         # [-1, 1]
    continuity_score: float      # [0, 1]
    revisit_score: float         # [0, 1]


def compute_full_coverage(
    current_orbit: OrbitalState,
    candidate_orbit: OrbitalState,
    region: TargetRegion,
    min_elevation_deg: float = 10.0,
    mission_type: str = "balanced",
) -> CoverageResult:
    """
    Compute all coverage metrics for a candidate orbit.

    This is the main entry point for coverage analysis.

    Args:
        current_orbit: Current satellite orbit.
        candidate_orbit: Proposed target orbit.
        region: Target region.
        min_elevation_deg: Minimum elevation angle.
        mission_type: Mission type for revisit normalization.

    Returns:
        CoverageResult with all metrics.
    """
    target_cov = compute_target_coverage(candidate_orbit, region, min_elevation_deg)
    cov_gain = compute_coverage_gain(current_orbit, candidate_orbit, region, min_elevation_deg)
    continuity = compute_continuity_score(candidate_orbit, region, min_elevation_deg)
    revisit = compute_revisit_score(candidate_orbit, region, min_elevation_deg, mission_type)

    return CoverageResult(
        target_coverage=target_cov,
        coverage_gain=cov_gain,
        continuity_score=continuity,
        revisit_score=revisit,
    )
