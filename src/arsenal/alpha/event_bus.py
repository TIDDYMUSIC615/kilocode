"""Async EventBus for decoupled event-driven signal generation."""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Dict, List

Handler = Callable[[Dict[str, Any]], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[str, List[Handler]] = {}

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._subs.setdefault(event_type, []).append(handler)

    async def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        handlers = list(self._subs.get(event_type, []))
        # dispatch concurrently and do not wait by default
        for h in handlers:
            asyncio.create_task(h(payload))

    async def publish_and_wait(self, event_type: str, payload: Dict[str, Any]) -> None:
        handlers = list(self._subs.get(event_type, []))
        await asyncio.gather(*(h(payload) for h in handlers))
