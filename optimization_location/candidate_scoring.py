"""Lightweight constellation cost / complexity proxies for ranking."""

from __future__ import annotations

from candidate_models import WalkerConstellationCandidate


def cost_score(candidate: WalkerConstellationCandidate) -> float:
    """Simple proxy: more satellites and higher altitude tend to cost more."""
    return float(candidate.total_satellites_T) * float(candidate.altitude_km)


def complexity_score(candidate: WalkerConstellationCandidate) -> float:
    """More satellites and more planes increase operations complexity."""
    return float(candidate.total_satellites_T * candidate.planes_P)
