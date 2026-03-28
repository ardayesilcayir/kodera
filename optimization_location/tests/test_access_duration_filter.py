"""Minimum access duration filtering."""

from __future__ import annotations

import numpy as np

from access_duration_filter import apply_min_access_duration_mask


def test_short_runs_removed() -> None:
    raw = np.zeros((10, 1), dtype=np.bool_)
    raw[2:4, 0] = True
    raw[5:9, 0] = True
    out = apply_min_access_duration_mask(raw, time_step_seconds=10.0, min_access_duration_s=35.0)
    assert not out[2:4, 0].any()
    assert out[5:9, 0].all()
