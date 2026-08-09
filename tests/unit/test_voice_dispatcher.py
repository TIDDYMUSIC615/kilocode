import asyncio

from arsenal.voice.dispatcher import VoiceDispatcher


def test_voice_dispatcher_calls_handler():
    disp = VoiceDispatcher()
    called = {}

    async def handler(payload):
        called["ok"] = payload["value"]

    disp.register("do.something", handler)

    async def run():
        await disp.dispatch("do.something", {"value": 42})

    asyncio.run(run())
    assert called.get("ok") == 42
