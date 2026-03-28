"""Coverage matrix metrics."""

from __future__ import annotations

import numpy as np
import pytest

from coverage_service import compute_coverage_metrics


def test_continuous_all_true_feasible() -> None:
    vis = np.ones((100, 5), dtype=bool)
    m = compute_coverage_metrics(vis, time_step_seconds=60.0)
    assert m.continuous_24_7_feasible is True
    assert m.min_point_coverage == 1.0
    assert m.mean_point_coverage == 1.0
    assert m.overall_coverage_ratio == 1.0
    assert m.max_gap_seconds == 0.0
    assert m.worst_cell_gap_seconds == 0.0
    assert m.revisit_mean_seconds == 0.0
    assert m.revisit_median_seconds == 0.0


def test_system_gap_when_not_all_points_covered() -> None:
    """One timestep drops one cell → regional simultaneous coverage fails for that step."""
    vis = np.ones((4, 3), dtype=bool)
    vis[2, 1] = False
    m = compute_coverage_metrics(vis, time_step_seconds=10.0)
    assert m.continuous_24_7_feasible is False
    assert m.max_gap_seconds == 10.0
    assert m.min_point_coverage < 1.0


def test_worst_cell_gap_longer_than_system() -> None:
    """Cell 0 dark for two steps; system still 'ok' at some times if other cells vary."""
    vis = np.ones((5, 2), dtype=bool)
    vis[1:3, 0] = False
    vis[2, 1] = False
    m = compute_coverage_metrics(vis, time_step_seconds=1.0)
    assert m.worst_cell_gap_seconds == 2.0
    assert m.max_gap_seconds >= 1.0


def test_revisit_mean_median_from_gaps() -> None:
    vis = np.ones((10, 1), dtype=bool)
    vis[2:5, 0] = False
    vis[7:9, 0] = False
    m = compute_coverage_metrics(vis, time_step_seconds=30.0)
    assert m.revisit_mean_seconds == pytest.approx(75.0)
    assert m.revisit_median_seconds == pytest.approx(75.0)


def test_empty_matrix() -> None:
    m = compute_coverage_metrics(np.zeros((0, 3), dtype=bool), 1.0)
    assert m.continuous_24_7_feasible is False
    assert m.overall_coverage_ratio == 0.0


def test_invalid_dt_raises() -> None:
    with pytest.raises(ValueError):
        compute_coverage_metrics(np.ones((2, 2), dtype=bool), 0.0)
