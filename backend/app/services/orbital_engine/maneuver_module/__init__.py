"""
ORBITA-R — Satellite Repositioning Optimization Module
=======================================================
A scientifically-grounded simulation and optimization engine for
determining optimal satellite repositioning strategies.

This module computes how an existing satellite can be moved to a new
target region or mission orbit with:
  - Minimal risk
  - Maximum efficiency
  - Awareness of other active satellites
  - Physically defensible assumptions

Model: Mode A (Fast Scientific Approximation)
  - Circular orbit assumption
  - Hohmann transfer for altitude changes
  - Impulsive burns for plane changes
  - Spherical Earth with WGS84 coordinates
  - Minimum elevation angle constraint

The architecture is designed to be extensible to Mode B
(J2, drag, third-body, SRP) in the future.

Usage:
    from optimization_to_move import optimize_reposition
    from optimization_to_move.satellite_models import Satellite, OrbitalState, ...
    from optimization_to_move.simulation_state import SimulationState, ...
    from optimization_to_move.target_region import TargetRegion

    result = optimize_reposition(satellite, target_region, mission_type, sim_state, constraints)
"""

from .reposition_optimizer import optimize_reposition
from .satellite_models import (
    OrbitalState,
    Satellite,
    SatelliteCapabilities,
    MissionConstraints,
    RepositionPlan,
    RepositionResult,
)
from .simulation_state import SimulationState
from .target_region import TargetRegion

__all__ = [
    "optimize_reposition",
    "OrbitalState",
    "Satellite",
    "SatelliteCapabilities",
    "MissionConstraints",
    "RepositionPlan",
    "RepositionResult",
    "SimulationState",
    "TargetRegion",
]

__version__ = "0.1.0"
__model_mode__ = "MODE_A"
