"""
Enumerate Walker-like constellation candidates from explicit search grids.

Mission types only affect **family ordering** (see ``mission_family_search_order``); altitude,
inclination, and Walker integers come from caller-supplied structures — no hidden mission
defaults.
"""

from __future__ import annotations

import math
from typing import Dict, Iterator, List, Tuple

from candidate_models import (
    CandidateGenerationInput,
    OrbitFamilySearchParams,
    SatelliteKeplerianECI,
    WalkerConstellationCandidate,
    mission_family_search_order,
)
from orbital_math import semi_major_axis_m_from_altitude_km, sun_synchronous_inclination_rad
from request_models import OrbitFamily
from walker_service import validate_walker_delta, walker_delta_slots


def _float_range_inclusive(lo: float, hi: float, step: float) -> Iterator[float]:
    if step <= 0.0:
        raise ValueError("step must be positive.")
    x = lo
    n = 0
    while x <= hi + 1e-9:
        yield x
        n += 1
        x = lo + n * step
        if n > 1_000_000:
            raise ValueError("Grid too large; reduce ranges or step.")


def _family_params_by_family(
    params: Tuple[OrbitFamilySearchParams, ...],
) -> Dict[OrbitFamily, OrbitFamilySearchParams]:
    out: Dict[OrbitFamily, OrbitFamilySearchParams] = {}
    for p in params:
        if p.family in out:
            raise ValueError(f"Duplicate OrbitFamilySearchParams for family {p.family}.")
        out[p.family] = p
    return out


def _geo_walker_allowed(planes_p: int, phase_f: int) -> bool:
    """MVP: GEO uses a single equatorial plane; multi-plane Walker is not generated for GEO."""
    return planes_p == 1 and phase_f == 0


def _build_satellites(
    altitude_km: float,
    inclination_deg: float,
    eccentricity: float,
    total_satellites_t: int,
    planes_p: int,
    phase_f: int,
) -> Tuple[SatelliteKeplerianECI, ...]:
    a_m = semi_major_axis_m_from_altitude_km(altitude_km)
    i_rad = math.radians(inclination_deg)
    validate_walker_delta(total_satellites_t, planes_p, phase_f)
    slots = walker_delta_slots(total_satellites_t, planes_p, phase_f)
    out: List[SatelliteKeplerianECI] = []
    for slot in slots:
        out.append(
            SatelliteKeplerianECI(
                semi_major_axis_m=a_m,
                eccentricity=eccentricity,
                inclination_rad=i_rad,
                raan_rad=slot.raan_rad,
                arg_of_perigee_rad=0.0,
                mean_anomaly_at_epoch_rad=slot.mean_anomaly_at_epoch_rad,
            )
        )
    return tuple(out)


def generate_walker_candidates(inp: CandidateGenerationInput) -> List[WalkerConstellationCandidate]:
    """
    Cartesian product of (mission-ordered families × altitude × inclination × Walker grid),
    subject to ``max_satellites``, ``max_planes``, and MVP GEO / SSO rules.
    """
    order = mission_family_search_order(inp.mission_type)
    allowed = set(inp.allowed_families)
    by_fam = _family_params_by_family(inp.family_search)

    candidates: List[WalkerConstellationCandidate] = []

    for fam in order:
        if fam not in allowed or fam not in by_fam:
            continue
        fp = by_fam[fam]

        for alt_km in _float_range_inclusive(fp.altitude_km_min, fp.altitude_km_max, fp.altitude_km_step):
            e = fp.eccentricity_max

            if fam == OrbitFamily.SSO and fp.sso_inclination_mode == "mean_sun_synchronous":
                a_m = semi_major_axis_m_from_altitude_km(alt_km)
                inc_list = [math.degrees(sun_synchronous_inclination_rad(a_m, e))]
            elif fam == OrbitFamily.GEO:
                inc_list = [0.0]
            else:
                inc_list = list(
                    _float_range_inclusive(
                        fp.inclination_deg_min,
                        fp.inclination_deg_max,
                        fp.inclination_deg_step,
                    )
                )

            for inc_deg in inc_list:
                for t in inp.walker_grid.total_satellites_T:
                    if t > inp.max_satellites:
                        continue
                    for p in inp.walker_grid.planes_P:
                        if p > inp.max_planes:
                            continue
                        for f in inp.walker_grid.phase_F:
                            if fam == OrbitFamily.GEO and not _geo_walker_allowed(p, f):
                                continue
                            try:
                                s = validate_walker_delta(t, p, f)
                            except ValueError:
                                continue

                            sats = _build_satellites(alt_km, inc_deg, e, t, p, f)
                            candidates.append(
                                WalkerConstellationCandidate(
                                    family=fam,
                                    altitude_km=alt_km,
                                    inclination_deg=inc_deg,
                                    eccentricity=e,
                                    total_satellites_T=t,
                                    planes_P=p,
                                    phase_F=f,
                                    satellites_per_plane_S=s,
                                    epoch_seconds_tai=inp.epoch_seconds_tai,
                                    satellites=sats,
                                )
                            )

    return candidates
