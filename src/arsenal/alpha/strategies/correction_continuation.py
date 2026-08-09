"""Correction-Continuation strategy: emits signals when price retraces then continues."""

from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Dict, Any


async def correction_continuation(bus, symbol: str, window: int = 3, threshold: Decimal = Decimal("0.005")):
    """Subscribe to tick events on bus and publish 'signal' events when strategy fires.

    Expected tick event: {'type': 'tick', 'symbol': symbol, 'price': Decimal}
    Signal: {'type': 'signal', 'symbol': symbol, 'action': 'buy'|'sell', 'size': Decimal}
    """
    history: list[Decimal] = []

    async def on_tick(event: Dict[str, Any]) -> None:
        price: Decimal = event["price"]
        history.append(price)
        if len(history) < window:
            return
        # look for small retracement: previous peak then pullback within threshold and continuation
        recent = history[-window:]
        # simple rule: if price recovered above max of previous then signal buy
        prev = recent[:-1]
        last = recent[-1]
        if max(prev) - last <= (max(prev) * threshold):
            # continuation up
            await bus.publish("signal", {"type": "signal", "symbol": symbol, "action": "buy", "size": Decimal("1")})

    bus.subscribe("tick", on_tick)
    # keep running until cancelled
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        return
