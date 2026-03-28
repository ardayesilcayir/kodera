"""
Filter raw visibility time series so that only dwell intervals meeting a minimum duration count.

Used for ``SensorModelSpec.min_access_duration_s``: a timestep is "in service" only if it lies
in a contiguous run of raw ``True`` whose duration is at least ``min_access_duration_s``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def apply_min_access_duration_mask(
    raw: NDArray[np.bool_],
    time_step_seconds: float,
    min_access_duration_s: float,
) -> NDArray[np.bool_]:
    """
    Parameters
    ----------
    raw
        Shape ``(n_times, n_points)`` raw line-of-sight / link availability.
    time_step_seconds
        Uniform sample spacing.
    min_access_duration_s
        Minimum contiguous ``True`` duration [s] for any timestep in that run to count.

    Returns
    -------
    Filtered boolean array of the same shape: ``True`` only for timesteps that belong to a
    raw run whose length (in time) is at least ``min_access_duration_s``.
    """
    if time_step_seconds <= 0.0:
        raise ValueError("time_step_seconds must be positive.")
    vis = np.asarray(raw, dtype=np.bool_)
    if vis.ndim != 2:
        raise ValueError("raw must be 2-D (time × points).")
    if min_access_duration_s <= 0.0:
        return vis.copy()
    min_steps = max(1, int(np.ceil(min_access_duration_s / time_step_seconds)))
    if min_steps <= 1:
        return vis.copy()

    n_t, n_p = vis.shape
    out = np.zeros_like(vis, dtype=np.bool_)
    for j in range(n_p):
        col = vis[:, j]
        t = 0
        while t < n_t:
            if not col[t]:
                t += 1
                continue
            run_end = t
            while run_end + 1 < n_t and col[run_end + 1]:
                run_end += 1
            run_len = run_end - t + 1
            if run_len >= min_steps:
                out[t : run_end + 1, j] = True
            t = run_end + 1
    return out
