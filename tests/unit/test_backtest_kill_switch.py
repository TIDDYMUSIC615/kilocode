import asyncio
import time

from decimal import Decimal

import pytest

from arsenal.alpha.event_bus import EventBus
from arsenal.backtest.engine import BacktestEngine
from arsenal.backtest.kill_switch import KillSwitch, KillSwitchTripped


@pytest.mark.asyncio
async def test_backtest_stops_on_kill_switch() -> None:
    bus = EventBus()
    ks = KillSwitch()
    engine = BacktestEngine(bus, ks)

    # create many events to ensure engine would take time
    events = [{"type": "tick", "symbol": "X", "price": Decimal(i)} for i in range(1000)]

    async def trip_later():
        # wait briefly then trip
        await asyncio.sleep(0)
        ks.trip()

    t = asyncio.create_task(trip_later())
    start = time.perf_counter()
    with pytest.raises(KillSwitchTripped):
        await engine.run(events)
    elapsed = (time.perf_counter() - start)
    # ensure engine reacted quickly (should be within tens of ms)
    assert elapsed < 0.05
    await t
