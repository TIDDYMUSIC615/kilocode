"""Minimal DXF exporter used by tests."""
from typing import Dict, List, Tuple


def export_dxf(layers: Dict[str, List[Tuple[float, float]]]) -> str:
    parts = ["SECTION", "ENTITIES"]
    for layer, pts in layers.items():
        for x, y in pts:
            parts.append(f"POINT {layer} {x} {y}")
    parts.append("ENDSEC")
    return "\n".join(parts)
