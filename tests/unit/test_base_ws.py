import asyncio

import pytest

from arsenal.connection.base_ws import (
    BaseWebSocketClient,
    ConnectionState,
    WebSocketTransport,
)


class FakeTransport:
    def __init__(self, messages: list[str]) -> None:
        self._messages = messages[:]
        self._closed = False

    async def send(self, data: str) -> None:
        # echo back for testing
        self._messages.append(f"echo:{data}")

    async def recv(self) -> str:
        await asyncio.sleep(0.01)
        if not self._messages:
            # simulate connection closed by raising
            raise ConnectionError("closed")
        return self._messages.pop(0)

    async def close(self) -> None:
        self._closed = True


@pytest.mark.asyncio
async def test_reconnect_and_receive(monkeypatch: pytest.MonkeyPatch) -> None:
    # connector that fails the first time, returns a FakeTransport the second
    attempts = {"count": 0}

    async def connector(url: str) -> WebSocketTransport:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise OSError("connect fail")
        return FakeTransport(["hello"])

    client = BaseWebSocketClient("ws://example", connector, max_retries=3)
    await client.connect()

    async def wait_connected() -> None:
        while client.state != ConnectionState.CONNECTED:
            await asyncio.sleep(0)

    await asyncio.wait_for(wait_connected(), timeout=1.0)

    # once connected, we should be able to read message
    msg = await asyncio.wait_for(client.get_message(), timeout=1.0)
    assert msg == "hello"

    # send a message, which will be echoed
    await client.send("hi")
    echo = await asyncio.wait_for(client.get_message(), timeout=1.0)
    assert echo == "echo:hi"

    await client.close()
    assert client.state == ConnectionState.DISCONNECTED
