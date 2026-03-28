"""
ORBITA-R — Orbit Candidate Generator
======================================
Generates candidate target orbits based on mission type, target region,
and physical constraints.

Strategy:
  1. Determine minimum inclination required to reach the target latitude.
  2. Select altitude range based on mission type.
  3. Compute RAAN options that place the ground track over/near the target.
  4. Compute optimal phase for fastest first pass over the target.
  5. Generate a grid of (altitude × inclination × RAAN) combinations.
  6. Filter by constraints.

Physical basis:
  - Inclination ≥ |target_latitude| for the ground track to reach that latitude.
  - Lower altitudes → better resolution but smaller footprint.
  - Higher altitudes → larger footprint but lower resolution.
  - RAAN determines when the orbital plane crosses the equator in local time,
    which controls the longitude window where the satellite passes overhead.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from satellite_models import (
    OrbitalState, MissionConstraints, R_EARTH, DEG_TO_RAD, RAD_TO_DEG,
    EARTH_ROTATION_DEG_PER_SEC, orbital_period,
)
from target_region import TargetRegion


# ──────────────────────────────────────────────
# Mission Profiles
# ──────────────────────────────────────────────

@dataclass
class MissionProfile:
    """Defines orbital parameter ranges for a given mission type."""
    alt_min_km: float
    alt_max_km: float
    alt_steps: int
    incl_offsets_deg: List[float]  # Offsets above minimum inclination
    raan_steps: int
    preferred_altitude_km: float   # Ideal altitude for this mission


MISSION_PROFILES: Dict[str, MissionProfile] = {
    "observation": MissionProfile(
        alt_min_km=300.0,
        alt_max_km=800.0,
        alt_steps=5,
        incl_offsets_deg=[0.0, 5.0, 10.0],
        raan_steps=5,
        preferred_altitude_km=500.0,
    ),
    "communication": MissionProfile(
        alt_min_km=500.0,
        alt_max_km=2000.0,
        alt_steps=5,
        incl_offsets_deg=[0.0, 5.0, 15.0],
        raan_steps=5,
        preferred_altitude_km=1200.0,
    ),
    "emergency": MissionProfile(
        alt_min_km=400.0,
        alt_max_km=1200.0,
        alt_steps=4,
        incl_offsets_deg=[0.0, 5.0, 10.0],
        raan_steps=6,
        preferred_altitude_km=600.0,
    ),
    "balanced": MissionProfile(
        alt_min_km=400.0,
        alt_max_km=1200.0,
        alt_steps=4,
        incl_offsets_deg=[0.0, 5.0, 10.0],
        raan_steps=5,
        preferred_altitude_km=700.0,
    ),
}


# ──────────────────────────────────────────────
# Inclination Computation
# ──────────────────────────────────────────────

def compute_minimum_inclination(target_lat: float) -> float:
    """
    Compute the minimum orbital inclination required to reach a target latitude.

    For a circular orbit, the maximum latitude reached equals the inclination.
    Therefore: i_min = |target_lat|

    For retrograde orbits (i > 90°), the maximum latitude is 180° - i.
    We use the prograde solution here.

    Args:
        target_lat: Target latitude in degrees.

    Returns:
        Minimum inclination in degrees.
    """
    return abs(target_lat)


# ──────────────────────────────────────────────
# RAAN Computation
# ──────────────────────────────────────────────

def compute_raan_options(
    target_lon: float,
    target_lat: float,
    altitude_km: float,
    n_options: int = 5,
) -> List[float]:
    """
    Compute RAAN options that place the satellite ground track near the target longitude.

    The RAAN determines where the ascending node crosses the equator.
    Combined with Earth's rotation and the orbital period, this determines
    the longitudes where the satellite passes.

    For a simplified estimate:
      - The sub-satellite point crosses the equator at longitude ≈ RAAN (at epoch)
      - As the orbit progresses, Earth rotates, shifting the equator crossing
      - We compute an initial RAAN that places the first ascending node near
        the target longitude, then fan out options

    Args:
        target_lon: Target longitude in degrees.
        target_lat: Target latitude in degrees.
        altitude_km: Orbital altitude.
        n_options: Number of RAAN options to generate.

    Returns:
        List of RAAN values in degrees [0, 360).
    """
    # Base RAAN: place ascending node near target longitude
    # Offset for latitude: the satellite crosses the target latitude at some
    # longitude offset from the ascending node, depending on inclination
    base_raan = target_lon % 360.0

    # For latitudes away from equator, the satellite reaches target lat
    # at an argument of latitude u where sin(u) = sin(lat)/sin(i)
    # The corresponding longitude shift is approximately:
    # Δlon ≈ atan2(cos(i)*sin(u), cos(u))
    # For simplicity in Mode A, we spread RAAN options around the base
    T = orbital_period(altitude_km)
    lon_drift_per_orbit = EARTH_ROTATION_DEG_PER_SEC * T  # ~22.5° for LEO

    # Generate RAAN options spread around base, spaced by fraction of drift
    step = lon_drift_per_orbit / max(n_options - 1, 1)
    options = []
    half_span = (n_options - 1) / 2.0

    for k in range(n_options):
        offset = (k - half_span) * step
        raan = (base_raan + offset) % 360.0
        options.append(raan)

    return options


# ──────────────────────────────────────────────
# Phase Computation
# ──────────────────────────────────────────────

def compute_optimal_phase(
    target_region: TargetRegion,
    altitude_km: float,
    inclination_deg: float,
    raan_deg: float,
) -> float:
    """
    Compute the orbital phase that would place the satellite closest to
    the target region at epoch (t=0).

    For a circular orbit, the sub-satellite latitude is:
      lat = arcsin(sin(i) · sin(u))
    where u = phase (argument of latitude at epoch).

    We want lat ≈ target_lat, so:
      u = arcsin(sin(target_lat) / sin(i))

    Args:
        target_region: Target region.
        altitude_km: Candidate altitude.
        inclination_deg: Candidate inclination.
        raan_deg: Candidate RAAN.

    Returns:
        Optimal phase in degrees [0, 360).
    """
    i = inclination_deg * DEG_TO_RAD
    target_lat_rad = target_region.center_lat * DEG_TO_RAD

    if abs(math.sin(i)) < 1e-10:
        # Near-equatorial orbit, phase doesn't strongly affect lat coverage
        return 0.0

    sin_u = math.sin(target_lat_rad) / math.sin(i)
    sin_u = max(-1.0, min(1.0, sin_u))  # Clamp for safety
    u = math.asin(sin_u)

    return (u * RAD_TO_DEG) % 360.0


# ──────────────────────────────────────────────
# Candidate Generation
# ──────────────────────────────────────────────

def generate_candidates(
    target_region: TargetRegion,
    mission_type: str,
    constraints: MissionConstraints,
    current_orbit: Optional[OrbitalState] = None,
    max_candidates: int = 100,
) -> List[OrbitalState]:
    """
    Generate a set of candidate target orbits based on mission type and region.

    Strategy:
      1. Look up mission profile for altitude/inclination ranges.
      2. Compute minimum inclination for the target latitude.
      3. Generate altitude steps within the profile range.
      4. Generate inclination options (minimum + offsets).
      5. Generate RAAN options for each altitude.
      6. Compute optimal phase for each combination.
      7. Filter out obviously infeasible candidates.

    Args:
        target_region: Target region to serve.
        mission_type: "communication" | "observation" | "emergency" | "balanced".
        constraints: Mission constraints.
        current_orbit: Current satellite orbit (for constraint checking).
        max_candidates: Maximum number of candidates to return.

    Returns:
        List of candidate OrbitalState objects.
    """
    profile = MISSION_PROFILES.get(mission_type)
    if profile is None:
        profile = MISSION_PROFILES["balanced"]

    min_inc = compute_minimum_inclination(target_region.center_lat)

    # Altitude grid
    if profile.alt_steps <= 1:
        altitudes = [profile.preferred_altitude_km]
    else:
        alt_step = (profile.alt_max_km - profile.alt_min_km) / (profile.alt_steps - 1)
        altitudes = [profile.alt_min_km + i * alt_step for i in range(profile.alt_steps)]

    # Inclination options
    inclinations = []
    for offset in profile.incl_offsets_deg:
        inc = min_inc + offset
        if 0.0 <= inc <= 180.0:
            inclinations.append(inc)

    # Also add sun-synchronous inclination if in range (approximately)
    # SSO inclination for LEO: i ≈ 96-98° (common for observation missions)
    if mission_type == "observation" and min_inc < 98.0:
        inclinations.append(97.5)

    # Remove duplicates and sort
    inclinations = sorted(set(round(x, 2) for x in inclinations))

    candidates: List[OrbitalState] = []

    for alt in altitudes:
        raan_options = compute_raan_options(
            target_region.center_lon,
            target_region.center_lat,
            alt,
            profile.raan_steps,
        )

        for inc in inclinations:
            # Skip if inclination is less than what's needed to reach the lat
            if inc < min_inc - 0.1:
                continue

            for raan in raan_options:
                phase = compute_optimal_phase(target_region, alt, inc, raan)

                try:
                    orbit = OrbitalState(
                        altitude_km=round(alt, 1),
                        inclination_deg=round(inc, 2),
                        raan_deg=round(raan, 2),
                        phase_deg=round(phase, 2),
                        eccentricity=0.0,
                    )
                    candidates.append(orbit)
                except ValueError:
                    # Skip invalid orbital states
                    continue

                if len(candidates) >= max_candidates:
                    return candidates

    return candidates
