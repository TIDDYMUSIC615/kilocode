"""Minimal VoiceDispatcher used by tests."""
from typing import Any, Callable, Dict


class VoiceDispatcher:
    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    def register(self, name: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        self._handlers[name] = handler

    async def dispatch(self, name: str, payload: Dict[str, Any]) -> None:
        if name not in self._handlers:
            return
        h = self._handlers[name]
        # Allow both async and sync handlers
        res = h(payload)
        if hasattr(res, "__await__"):
            await res
