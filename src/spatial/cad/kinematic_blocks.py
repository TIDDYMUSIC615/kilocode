"""Manage dynamic CAD blocks representing STOWED/DEPLOYED states."""

from __future__ import annotations

from typing import Dict


def apply_block_state(blocks: Dict[str, Dict], state_map: Dict[str, str]) -> Dict[str, Dict]:
    """Return new blocks dict with applied states from state_map ('STOWED'|'DEPLOYED')."""
    out = {}
    for name, block in blocks.items():
        s = state_map.get(name, block.get("state", "STOWED"))
        new = dict(block)
        new["state"] = s
        out[name] = new
    return out
