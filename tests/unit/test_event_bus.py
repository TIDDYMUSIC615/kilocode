import asyncio

from arsenal.alpha.event_bus import EventBus


async def fake_handler(events: list, payload: dict) -> None:
    events.append(payload)


def test_event_bus_publish_and_wait():
    bus = EventBus()
    events: list[dict] = []

    async def run_test():
        bus.subscribe("t", lambda p: fake_handler(events, p))
        await bus.publish_and_wait("t", {"a": 1})

    asyncio.run(run_test())
    assert events and events[0]["a"] == 1
