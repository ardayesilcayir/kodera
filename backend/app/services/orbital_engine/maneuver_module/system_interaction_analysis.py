"""
ORBITA-R — System Interaction Analysis
========================================
Analyzes how a candidate orbit interacts with the rest of the satellite
constellation. Computes overlap penalties, redundancy scores, coverage
gap reduction, and strategic fit.

Key principle:
  - The optimizer must account for what other satellites are already doing.
  - Unnecessary overlap wastes resources → penalty.
  - Filling coverage gaps → reward.
  - Balanced geographic distribution → reward.
  - Failure resilience (redundancy) → reward, but with diminishing returns.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

from .satellite_models import OrbitalState, Satellite, R_EARTH, DEG_TO_RAD
from .target_region import TargetRegion, haversine_distance, sample_region_points
from .coverage_engine import (
    compute_footprint_radius_km,
    compute_target_coverage,
    compute_ground_track,
)


# ──────────────────────────────────────────────
# Overlap & Redundancy
# ──────────────────────────────────────────────

def compute_overlap_penalty(
    candidate_orbit: OrbitalState,
    other_satellites: List[Satellite],
    region: TargetRegion,
    min_elevation_deg: float = 10.0,
    n_region_samples: int = 50,
) -> float:
    """
    Compute how much the candidate orbit duplicates existing coverage over
    the target region.

    Method:
      1. Sample points in the target region.
      2. For each point, count how many OTHER satellites already cover it.
      3. For each point that the candidate would also cover AND is already
         covered by 2+ other satellites, accumulate a penalty.
      4. Normalize to [0, 1].

    A penalty of 0.0 means no problematic overlap.
    A penalty of 1.0 means the candidate entirely duplicates heavily-covered areas.

    Returns:
        Overlap penalty score [0.0, 1.0].
    """
    region_points = sample_region_points(region, n_region_samples)
    if not region_points:
        return 0.0

    # Compute candidate footprint
    cand_footprint = compute_footprint_radius_km(candidate_orbit.altitude_km, min_elevation_deg)
    cand_track = compute_ground_track(candidate_orbit, n_points=360, n_periods=1.0)

    # For each other satellite, compute their tracks
    other_tracks = []
    other_footprints = []
    for sat in other_satellites:
        track = compute_ground_track(sat.current_orbit, n_points=360, n_periods=1.0)
        fp = compute_footprint_radius_km(sat.current_orbit.altitude_km, min_elevation_deg)
        other_tracks.append(track)
        other_footprints.append(fp)

    overlap_score = 0.0
    total_candidate_coverage = 0

    for rlat, rlon in region_points:
        # Does the candidate cover this point?
        cand_covers = False
        for tlat, tlon in cand_track:
            if haversine_distance(rlat, rlon, tlat, tlon) <= cand_footprint:
                cand_covers = True
                break

        if not cand_covers:
            continue

        total_candidate_coverage += 1

        # How many others already cover this point?
        other_cover_count = 0
        for idx, track in enumerate(other_tracks):
            fp = other_footprints[idx]
            for tlat, tlon in track:
                if haversine_distance(rlat, rlon, tlat, tlon) <= fp:
                    other_cover_count += 1
                    break

        # Penalty increases with existing coverage count
        # 0 others → no penalty, 1 other → small, 2+ → increasing
        if other_cover_count >= 2:
            overlap_score += min(other_cover_count / 4.0, 1.0)

    if total_candidate_coverage == 0:
        return 0.0

    return min(overlap_score / total_candidate_coverage, 1.0)


def compute_redundancy_score(
    candidate_orbit: OrbitalState,
    other_satellites: List[Satellite],
    region: TargetRegion,
    min_elevation_deg: float = 10.0,
) -> float:
    """
    Compute the redundancy level: how many other satellites also cover
    the target region (as backup).

    Higher redundancy = better failure resilience, but with diminishing returns.

    Method:
      - Count how many other satellites have coverage > 0.1 over the region.
      - Normalize with diminishing returns: score = 1 - 1/(1 + count)

    Returns:
        Redundancy score [0.0, 1.0]. Higher = more backup available.
    """
    coverage_count = 0
    for sat in other_satellites:
        cov = compute_target_coverage(
            sat.current_orbit, region, min_elevation_deg,
            n_track_points=180, n_region_samples=20, n_periods=1.0,
        )
        if cov > 0.1:
            coverage_count += 1

    # Diminishing returns: 0→0.0, 1→0.5, 2→0.67, 3→0.75, etc.
    return 1.0 - 1.0 / (1.0 + coverage_count)


# ──────────────────────────────────────────────
# Gap Reduction
# ──────────────────────────────────────────────

def compute_gap_reduction(
    candidate_orbit: OrbitalState,
    other_satellites: List[Satellite],
    region: TargetRegion,
    min_elevation_deg: float = 10.0,
    n_region_samples: int = 50,
) -> float:
    """
    Compute how much the candidate orbit fills coverage gaps (points that
    no other satellite currently covers).

    Method:
      1. Sample points in the target region.
      2. Find which points are NOT covered by any existing satellite.
      3. Check how many of those uncovered points the candidate would cover.
      4. gap_reduction = fraction of currently-uncovered points that become covered.

    Returns:
        Gap reduction score [0.0, 1.0]. Higher = filling more gaps.
    """
    region_points = sample_region_points(region, n_region_samples)
    if not region_points:
        return 0.0

    # Pre-compute other satellite tracks
    other_tracks = []
    other_footprints = []
    for sat in other_satellites:
        track = compute_ground_track(sat.current_orbit, n_points=180, n_periods=1.0)
        fp = compute_footprint_radius_km(sat.current_orbit.altitude_km, min_elevation_deg)
        other_tracks.append(track)
        other_footprints.append(fp)

    # Candidate track
    cand_track = compute_ground_track(candidate_orbit, n_points=360, n_periods=1.0)
    cand_footprint = compute_footprint_radius_km(candidate_orbit.altitude_km, min_elevation_deg)

    uncovered_points = []
    for rlat, rlon in region_points:
        is_covered = False
        for idx, track in enumerate(other_tracks):
            fp = other_footprints[idx]
            for tlat, tlon in track:
                if haversine_distance(rlat, rlon, tlat, tlon) <= fp:
                    is_covered = True
                    break
            if is_covered:
                break
        if not is_covered:
            uncovered_points.append((rlat, rlon))

    if not uncovered_points:
        # Everything is already covered — no gap to fill
        return 0.0

    # How many uncovered points does the candidate cover?
    newly_covered = 0
    for rlat, rlon in uncovered_points:
        for tlat, tlon in cand_track:
            if haversine_distance(rlat, rlon, tlat, tlon) <= cand_footprint:
                newly_covered += 1
                break

    return newly_covered / len(uncovered_points)


# ──────────────────────────────────────────────
# Strategic Fit
# ──────────────────────────────────────────────

def compute_strategic_fit(
    candidate_orbit: OrbitalState,
    mission_type: str,
    other_satellites: List[Satellite],
    region: TargetRegion,
) -> float:
    """
    Compute how well the candidate orbit fits the mission strategically.

    Factors:
      1. Mission-type compatibility: is the candidate orbit's altitude/inclination
         appropriate for the mission type?
      2. Constellation balance: does the candidate improve the geographic
         distribution of the satellite constellation?
      3. Critical gap assessment: is this region critically underserved?

    Returns:
        Strategic fit score [0.0, 1.0].
    """
    # Factor 1: Mission-type altitude compatibility
    mission_ideal = {
        "observation": (300, 800, 500),
        "communication": (500, 2000, 1200),
        "emergency": (400, 1200, 600),
        "balanced": (400, 1200, 700),
    }
    alt_min, alt_max, alt_ideal = mission_ideal.get(mission_type, (400, 1200, 700))

    alt = candidate_orbit.altitude_km
    if alt_min <= alt <= alt_max:
        # Distance from ideal, normalized to [0, 1]
        alt_range = alt_max - alt_min
        alt_fit = 1.0 - abs(alt - alt_ideal) / (alt_range if alt_range > 0 else 1.0)
    else:
        alt_fit = max(0.0, 0.5 - abs(alt - alt_ideal) / 2000.0)

    # Factor 2: Constellation balance (inclination spread)
    balance = compute_constellation_balance(candidate_orbit, other_satellites)

    # Factor 3: Coverage uniqueness for this mission type
    mission_compatible_sats = [
        s for s in other_satellites
        if s.capabilities.mission_type == mission_type
        or s.capabilities.mission_type == "balanced"
    ]
    # Fewer mission-compatible sats covering this region → higher strategic need
    if mission_compatible_sats:
        avg_coverage = 0.0
        for sat in mission_compatible_sats:
            cov = compute_target_coverage(
                sat.current_orbit, region, 10.0,
                n_track_points=180, n_region_samples=20,
            )
            avg_coverage += cov
        avg_coverage /= len(mission_compatible_sats)
        need_factor = 1.0 - avg_coverage
    else:
        need_factor = 1.0  # No mission-compatible sats → high need

    # Weighted combination
    strategic_fit = 0.4 * alt_fit + 0.3 * balance + 0.3 * need_factor
    return max(0.0, min(1.0, strategic_fit))


def compute_constellation_balance(
    candidate_orbit: OrbitalState,
    other_satellites: List[Satellite],
) -> float:
    """
    Evaluate constellation geographic balance with the candidate included.

    Measures how well the satellites are spread across different orbital planes.
    A well-distributed constellation has satellites at varied inclinations and RAANs.

    Method:
      - Compute the standard deviation of inclinations and RAANs.
      - A higher spread → better balance.
      - Normalize to [0, 1].

    Returns:
        Balance score [0.0, 1.0].
    """
    if not other_satellites:
        return 0.5  # Neutral — can't assess balance with one satellite

    # Collect all inclinations and RAANs (including candidate)
    incs = [s.current_orbit.inclination_deg for s in other_satellites]
    incs.append(candidate_orbit.inclination_deg)

    raans = [s.current_orbit.raan_deg for s in other_satellites]
    raans.append(candidate_orbit.raan_deg)

    # Inclination spread (ideal: covers 0-90° well)
    inc_range = max(incs) - min(incs) if len(incs) > 1 else 0.0
    inc_balance = min(inc_range / 90.0, 1.0)

    # RAAN spread (ideal: evenly distributed around 360°)
    if len(raans) > 1:
        raans_sorted = sorted(raans)
        # Compute gaps between consecutive RAANs (circular)
        gaps = []
        for i in range(len(raans_sorted) - 1):
            gaps.append(raans_sorted[i + 1] - raans_sorted[i])
        gaps.append(360.0 - raans_sorted[-1] + raans_sorted[0])

        ideal_gap = 360.0 / len(raans_sorted)
        gap_variance = sum((g - ideal_gap) ** 2 for g in gaps) / len(gaps)
        max_variance = ideal_gap ** 2
        raan_balance = 1.0 - min(gap_variance / max(max_variance, 1.0), 1.0)
    else:
        raan_balance = 0.5

    return 0.5 * inc_balance + 0.5 * raan_balance


# ──────────────────────────────────────────────
# Aggregated Result
# ──────────────────────────────────────────────

@dataclass
class SystemInteractionResult:
    """Complete system interaction analysis result."""
    overlap_penalty: float       # [0, 1]
    redundancy_score: float      # [0, 1]
    gap_reduction: float         # [0, 1]
    strategic_fit_score: float   # [0, 1]
    constellation_balance: float # [0, 1]


def compute_system_interaction(
    candidate_orbit: OrbitalState,
    other_satellites: List[Satellite],
    region: TargetRegion,
    mission_type: str,
    min_elevation_deg: float = 10.0,
) -> SystemInteractionResult:
    """
    Compute all system interaction metrics for a candidate orbit.

    This is the main entry point for constellation-level analysis.

    Args:
        candidate_orbit: Proposed target orbit.
        other_satellites: All other active satellites.
        region: Target region.
        mission_type: Mission type.
        min_elevation_deg: Minimum elevation angle.

    Returns:
        SystemInteractionResult with all metrics.
    """
    overlap = compute_overlap_penalty(
        candidate_orbit, other_satellites, region, min_elevation_deg,
    )
    redundancy = compute_redundancy_score(
        candidate_orbit, other_satellites, region, min_elevation_deg,
    )
    gap_red = compute_gap_reduction(
        candidate_orbit, other_satellites, region, min_elevation_deg,
    )
    strategic = compute_strategic_fit(
        candidate_orbit, mission_type, other_satellites, region,
    )
    balance = compute_constellation_balance(candidate_orbit, other_satellites)

    return SystemInteractionResult(
        overlap_penalty=overlap,
        redundancy_score=redundancy,
        gap_reduction=gap_red,
        strategic_fit_score=strategic,
        constellation_balance=balance,
    )
