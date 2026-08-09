import asyncio

from src.main import Master


def test_master_start_stop():
    m = Master()

    async def run_then_stop():
        task = asyncio.create_task(m.start())
        await asyncio.sleep(0.01)
        await m.stop()
        await task

    asyncio.run(run_then_stop())
    assert m.stop_event.is_set()
