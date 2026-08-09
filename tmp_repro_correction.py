import asyncio
from decimal import Decimal
from arsenal.alpha.event_bus import EventBus
from arsenal.alpha.strategies.correction_continuation import correction_continuation

async def collect(payload, signals, event):
    print('COLLECT', payload)
    signals.append(payload)
    event.set()

async def main():
    bus = EventBus()
    signals = []
    event = asyncio.Event()
    bus.subscribe('signal', lambda payload: collect(payload, signals, event))
    task = asyncio.create_task(correction_continuation(bus, 'FOO', window=3, threshold=Decimal('0.01')))
    await asyncio.sleep(0)
    await bus.publish_and_wait('tick', {'symbol': 'FOO', 'price': Decimal('1.00')})
    await bus.publish_and_wait('tick', {'symbol': 'FOO', 'price': Decimal('1.01')})
    await bus.publish_and_wait('tick', {'symbol': 'FOO', 'price': Decimal('1.02')})
    try:
        await asyncio.wait_for(event.wait(), timeout=1.0)
        print('signal set, signals=', signals)
    except Exception as e:
        print('timeout', e, 'signals', signals)
    task.cancel()
    await asyncio.sleep(0.1)

asyncio.run(main())
