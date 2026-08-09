"""Minimal kinematic block helpers used by tests."""
from typing import Dict, Any


def apply_block_state(blocks: Dict[str, Dict[str, Any]], updates: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    ns = {k: dict(v) for k, v in blocks.items()}
    for k, state in updates.items():
        if k not in ns:
            ns[k] = {}
        ns[k]["state"] = state
    return ns
