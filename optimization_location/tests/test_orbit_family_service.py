"""Candidate generation and mission ordering."""

from __future__ import annotations

import pytest

from candidate_models import (
    CandidateGenerationInput,
    OrbitFamilySearchParams,
    WalkerTopologyGrid,
    mission_family_search_order,
)
from orbit_family_service import generate_walker_candidates
from request_models import MissionType, OrbitFamily


def test_mission_order_emergency() -> None:
    assert mission_family_search_order(MissionType.EMERGENCY_COMMS) == (
        OrbitFamily.LEO,
        OrbitFamily.SSO,
        OrbitFamily.MEO,
        OrbitFamily.GEO,
    )


def test_mission_order_broadcast() -> None:
    assert mission_family_search_order(MissionType.BROADCAST) == (OrbitFamily.GEO,)


def test_generates_leo_before_geo_when_emergency() -> None:
    inp = CandidateGenerationInput(
        mission_type=MissionType.EMERGENCY_COMMS,
        allowed_families=(OrbitFamily.LEO, OrbitFamily.GEO),
        family_search=(
            OrbitFamilySearchParams(
                family=OrbitFamily.LEO,
                altitude_km_min=500.0,
                altitude_km_max=500.0,
                altitude_km_step=100.0,
                inclination_deg_min=51.6,
                inclination_deg_max=51.6,
                inclination_deg_step=1.0,
                eccentricity_max=0.0,
                sso_inclination_mode="none",
            ),
            OrbitFamilySearchParams(
                family=OrbitFamily.GEO,
                altitude_km_min=35786.0,
                altitude_km_max=35786.0,
                altitude_km_step=1.0,
                inclination_deg_min=0.0,
                inclination_deg_max=0.0,
                inclination_deg_step=1.0,
                eccentricity_max=0.0,
                sso_inclination_mode="none",
            ),
        ),
        walker_grid=WalkerTopologyGrid(
            total_satellites_T=[4],
            planes_P=[1],
            phase_F=[0],
        ),
        max_satellites=10,
        max_planes=4,
        epoch_seconds_tai=0.0,
    )
    cands = generate_walker_candidates(inp)
    assert len(cands) == 2
    assert cands[0].family == OrbitFamily.LEO
    assert cands[1].family == OrbitFamily.GEO
    assert cands[1].planes_P == 1 and cands[1].phase_F == 0


def test_geo_skips_multiplane_walker() -> None:
    inp = CandidateGenerationInput(
        mission_type=MissionType.BROADCAST,
        allowed_families=(OrbitFamily.GEO,),
        family_search=(
            OrbitFamilySearchParams(
                family=OrbitFamily.GEO,
                altitude_km_min=35786.0,
                altitude_km_max=35786.0,
                altitude_km_step=1.0,
                inclination_deg_min=0.0,
                inclination_deg_max=0.0,
                inclination_deg_step=1.0,
                eccentricity_max=0.0,
                sso_inclination_mode="none",
            ),
        ),
        walker_grid=WalkerTopologyGrid(
            total_satellites_T=[3],
            planes_P=[1, 3],
            phase_F=[0, 1],
        ),
        max_satellites=10,
        max_planes=10,
        epoch_seconds_tai=0.0,
    )
    cands = generate_walker_candidates(inp)
    # Only P=1, F=0 allowed for GEO MVP
    assert all(c.planes_P == 1 and c.phase_F == 0 for c in cands)
    assert len(cands) == 1


def test_duplicate_family_params_rejected() -> None:
    from orbit_family_service import _family_params_by_family

    with pytest.raises(ValueError, match="Duplicate"):
        _family_params_by_family(
            (
                OrbitFamilySearchParams(
                    family=OrbitFamily.LEO,
                    altitude_km_min=400.0,
                    altitude_km_max=400.0,
                    altitude_km_step=1.0,
                    inclination_deg_min=45.0,
                    inclination_deg_max=45.0,
                    inclination_deg_step=1.0,
                    eccentricity_max=0.0,
                    sso_inclination_mode="none",
                ),
                OrbitFamilySearchParams(
                    family=OrbitFamily.LEO,
                    altitude_km_min=500.0,
                    altitude_km_max=500.0,
                    altitude_km_step=1.0,
                    inclination_deg_min=45.0,
                    inclination_deg_max=45.0,
                    inclination_deg_step=1.0,
                    eccentricity_max=0.0,
                    sso_inclination_mode="none",
                ),
            )
        )
