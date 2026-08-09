"""Simple elevation segmenter: slice points into Z-bands and detect subterranean layers."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple


def segment_by_elevation(points: Iterable[Tuple[float, float, float]], slice_height: float) -> Dict[int, List[Tuple[float, float, float]]]:
    bands: Dict[int, List[Tuple[float, float, float]]] = defaultdict(list)
    for x, y, z in points:
        idx = int(z // slice_height)
        bands[idx].append((x, y, z))
    return bands


def detect_subterranean(bands: Dict[int, List[Tuple[float, float, float]]]) -> List[int]:
    # subterranean when negative band index exists
    return [idx for idx in bands.keys() if idx < 0]
