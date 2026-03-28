"""
Coverage analytics from a discrete-time visibility matrix (time × ground grid point).

Definitions (no hidden weighting):
- **Per-point coverage**: fraction of time steps where that point is visible.
- **Overall coverage ratio**: mean of binary visibility over all (time, point) pairs.
- **System gap** (``max_gap_seconds``): longest contiguous interval where **not all**
  grid points are simultaneously visible (regional 24/7 failure mode).
- **Worst cell gap** (``worst_cell_gap_seconds``): over all cells, the longest time that
  **that** cell spends without visibility.
- **Revisit** (mean/median): over all cells, all **off** intervals (gaps); mean/median of
  gap durations in seconds. If there is no off interval, both are ``0.0``.

**Continuous 24/7 feasibility** (hard): ``True`` iff every grid point is visible at every
time step — no blind spots, no scoring blend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class CoverageMetrics:
    min_point_coverage: float
    mean_point_coverage: float
    overall_coverage_ratio: float
    max_gap_seconds: float
    """Longest contiguous period where simultaneous coverage of **all** points fails."""
    worst_cell_gap_seconds: float
    """Longest single-cell outage (max over cells of that cell's longest gap)."""
    revisit_mean_seconds: float
    revisit_median_seconds: float
    continuous_24_7_feasible: bool
    """``True`` iff ``visibility`` is all-``True`` (every time, every point)."""


def _longest_false_run(good: NDArray[np.bool_]) -> int:
    """Maximum length of consecutive ``False`` in ``good`` (``good`` = visibility OK)."""
    if good.size == 0:
        return 0
    longest = 0
    run = 0
    for g in good.flat:
        if not bool(g):
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return longest


def _all_gap_durations_seconds(good: NDArray[np.bool_], dt_s: float) -> List[float]:
    """Durations of every contiguous ``False`` run in ``good``."""
    if good.size == 0:
        return []
    durations: List[float] = []
    run = 0
    for g in good.flat:
        if not bool(g):
            run += 1
        else:
            if run > 0:
                durations.append(run * dt_s)
            run = 0
    if run > 0:
        durations.append(run * dt_s)
    return durations


def compute_coverage_metrics(
    visibility: NDArray[np.bool_],
    time_step_seconds: float,
) -> CoverageMetrics:
    """
    Parameters
    ----------
    visibility
        Shape ``(n_times, n_points)``. ``True`` = satellite visible at that time/point.
    time_step_seconds
        Uniform spacing between samples (used to convert run lengths to seconds).
    """
    if time_step_seconds <= 0.0:
        raise ValueError("time_step_seconds must be positive.")
    vis = np.asarray(visibility, dtype=np.bool_)
    if vis.ndim != 2:
        raise ValueError("visibility must be a 2-D array (time × points).")
    n_t, n_p = vis.shape
    if n_t == 0 or n_p == 0:
        return CoverageMetrics(
            min_point_coverage=0.0,
            mean_point_coverage=0.0,
            overall_coverage_ratio=0.0,
            max_gap_seconds=0.0,
            worst_cell_gap_seconds=0.0,
            revisit_mean_seconds=0.0,
            revisit_median_seconds=0.0,
            continuous_24_7_feasible=False,
        )

    continuous_ok = bool(np.all(vis))
    per_point = vis.mean(axis=0)
    min_point = float(np.min(per_point))
    mean_point = float(np.mean(per_point))
    overall = float(np.mean(vis))

    # Simultaneous regional coverage: all points visible at time t
    all_covered = np.all(vis, axis=1)
    max_gap_steps = _longest_false_run(all_covered)
    max_gap_s = float(max_gap_steps * time_step_seconds)

    worst_cell_s = 0.0
    for j in range(n_p):
        col = vis[:, j]
        worst_cell_s = max(worst_cell_s, float(_longest_false_run(col) * time_step_seconds))

    # Revisit / gap statistics: pool all per-cell outage intervals
    all_gaps: List[float] = []
    for j in range(n_p):
        all_gaps.extend(_all_gap_durations_seconds(vis[:, j], time_step_seconds))

    if not all_gaps:
        rev_mean = 0.0
        rev_med = 0.0
    else:
        arr = np.asarray(all_gaps, dtype=np.float64)
        rev_mean = float(np.mean(arr))
        rev_med = float(np.median(arr))

    return CoverageMetrics(
        min_point_coverage=min_point,
        mean_point_coverage=mean_point,
        overall_coverage_ratio=overall,
        max_gap_seconds=max_gap_s,
        worst_cell_gap_seconds=worst_cell_s,
        revisit_mean_seconds=rev_mean,
        revisit_median_seconds=rev_med,
        continuous_24_7_feasible=continuous_ok,
    )
