"""Simple blueprint parser: extract 2D text-defined shapes from ASCII input."""

from __future__ import annotations

from typing import List, Tuple


def parse_ascii_blueprint(text: str) -> List[Tuple[float, float]]:
    # A toy parser: find lines with coordinates like 'x,y'
    pts: List[Tuple[float, float]] = []
    for line in text.splitlines():
        if "," in line:
            try:
                x, y = line.strip().split(",")
                pts.append((float(x), float(y)))
            except Exception:
                continue
    return pts
