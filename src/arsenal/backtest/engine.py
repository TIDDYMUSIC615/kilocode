"""Simple historical replay backtest engine with kill-switch integration."""

from __future__ import annotations

import asyncio
import time
from decimal import Decimal
from typing import Any, Dict, Iterable, List

from arsenal.alpha.event_bus import EventBus
from .kill_switch import KillSwitch, KillSwitchTripped


class BacktestEngine:
    def __init__(self, bus: EventBus, kill_switch: KillSwitch) -> None:
        self.bus = bus
        self.kill_switch = kill_switch
        self.stopped = False

    async def run(self, events: Iterable[Dict[str, Any]]) -> None:
        """Replay events into the bus. Reacts to kill switch quickly.

        Events are dicts with keys like {'type': 'tick', 'symbol': ..., 'price': Decimal}
        """
        start = time.perf_counter()
        for ev in events:
            if self.kill_switch.is_tripped():
                self.stopped = True
                raise KillSwitchTripped("Kill switch tripped during backtest")
            # publish and wait handlers to finish
            await self.bus.publish_and_wait(ev.get("type", ""), ev)
            # tight loop; yield to event loop but do not sleep long to keep latency low
            await asyncio.sleep(0)
        end = time.perf_counter()
        self.duration = end - start
