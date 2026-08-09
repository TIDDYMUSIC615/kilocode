import asyncio
from decimal import Decimal

from arsenal.alpha.event_bus import EventBus
from arsenal.alpha.strategies.correction_continuation import correction_continuation


def test_correction_continuation_emits_signal():
    bus = EventBus()
    signals = []

    async def runner():
        signal_event = asyncio.Event()

        async def collect(payload):
            signals.append(payload)
            signal_event.set()

        # start strategy
        task = asyncio.create_task(correction_continuation(bus, "FOO", window=3, threshold=Decimal("0.01")))
        bus.subscribe("signal", collect)
        # allow the task to start and register its subscription handler
        await asyncio.sleep(0)
        # publish ticks aligned with the exact threshold behavior
        await bus.publish_and_wait("tick", {"symbol": "FOO", "price": Decimal("1.00")})
        await bus.publish_and_wait("tick", {"symbol": "FOO", "price": Decimal("1.02")})
        await bus.publish_and_wait("tick", {"symbol": "FOO", "price": Decimal("1.02")})
        await asyncio.wait_for(signal_event.wait(), timeout=1.0)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(runner())
    assert any(s["action"] == "buy" for s in signals)
