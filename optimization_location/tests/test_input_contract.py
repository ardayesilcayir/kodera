"""Designer and API inputs must not use silent operational defaults."""

from __future__ import annotations

import pytest

from optimizer_models import DesignerParams


def test_designer_params_rejects_packing_factor_not_greater_than_one() -> None:
    with pytest.raises(ValueError, match="footprint_solid_angle_packing_factor"):
        DesignerParams(
            grid_spacing_m=1000.0,
            simulation_time_step_seconds=60.0,
            region_circle_vertices=32,
            early_stop_on_first_feasible_minimum_t=False,
            footprint_solid_angle_packing_factor=1.0,
            top_candidates_limit=3,
            grid_include_boundary=False,
        )


def test_designer_params_rejects_low_circle_vertex_count() -> None:
    with pytest.raises(ValueError, match="region_circle_vertices"):
        DesignerParams(
            grid_spacing_m=1000.0,
            simulation_time_step_seconds=60.0,
            region_circle_vertices=4,
            early_stop_on_first_feasible_minimum_t=False,
            footprint_solid_angle_packing_factor=1.1,
            top_candidates_limit=3,
            grid_include_boundary=False,
        )
