"""Simple DXF exporter that writes multi-layer text output for tests."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


def export_dxf(layers: Dict[str, Iterable[Tuple[float, float]]]) -> str:
    lines: List[str] = ["0\nSECTION\n2\nENTITIES"]
    for layer, items in layers.items():
        lines.append(f"9\n$LAYER\n8\n{layer}")
        for x, y in items:
            lines.append(f"0\nPOINT\n10\n{x}\n20\n{y}")
    lines.append("0\nENDSEC\n0\nEOF")
    return "\n".join(lines)
