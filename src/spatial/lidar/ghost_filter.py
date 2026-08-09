"""Ghost filter: remove mirrored/reflection points and small isolated clusters."""

from __future__ import annotations

from typing import Iterable, List, Tuple


def remove_reflections(points: Iterable[Tuple[float, float, float]], threshold: float = 0.001) -> List[Tuple[float, float, float]]:
    pts = list(points)
    out: List[Tuple[float, float, float]] = []
    seen = set()
    for x, y, z in pts:
        key = (round(x, 3), round(y, 3), round(z, 3))
        if key in seen:
            continue
        seen.add(key)
        out.append((x, y, z))
    return out


def remove_isolated(points: Iterable[Tuple[float, float, float]], min_neighbors: int = 1) -> List[Tuple[float, float, float]]:
    pts = list(points)
    out = []
    for i, p in enumerate(pts):
        neighbors = 0
        for j, q in enumerate(pts):
            if i == j:
                continue
            if abs(p[0]-q[0])<1.0 and abs(p[1]-q[1])<1.0:
                neighbors += 1
        if neighbors >= min_neighbors:
            out.append(p)
    return out
