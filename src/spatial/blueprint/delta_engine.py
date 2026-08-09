"""Compare 2D blueprint points to 3D LiDAR projections to find deltas."""

from __future__ import annotations

from typing import List, Tuple


def reconcile(blueprint: List[Tuple[float, float]], lidar_xy: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    # return points in lidar not in blueprint (simple set-diff by rounding)
    bp_set = set((round(x, 2), round(y, 2)) for x, y in blueprint)
    deltas = [p for p in lidar_xy if (round(p[0], 2), round(p[1], 2)) not in bp_set]
    return deltas
