"""Async WebSocket client skeleton with reconnection and state management.

This module implements a transport-agnostic WebSocket client. The real
network connector (for example the `websockets` or `aiohttp` client) is
injected via the `connector` callable. This keeps the module stdlib-only for
testability and avoids forcing a third-party dependency into the core.

Key features:
- Async connect/disconnect lifecycle
- Exponential/backoff reconnection with jitter
- Send/receive queues and orderly shutdown
- Connection state introspection
"""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Awaitable, Callable, Optional, Protocol

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CLOSING = "closing"


class WebSocketTransport(Protocol):
    async def send(self, data: str) -> None:  # pragma: no cover - interface
        ...

    async def recv(self) -> str:  # pragma: no cover - interface
        ...

    async def close(self) -> None:  # pragma: no cover - interface
        ...


Connector = Callable[[str], Awaitable[WebSocketTransport]]


@dataclass
class _ReconnectPolicy:
    min_backoff: float = 1.0
    max_backoff: float = 10.0
    factor: float = 2.0


class BaseWebSocketClient:
    """A simple, transport-agnostic WebSocket client with reconnection.

    Args:
        url: Destination URL (passed to connector).
        connector: Async callable returning a transport implementing
            `send`, `recv`, and `close`.
        reconnect_policy: Backoff settings for reconnection attempts.
        max_retries: If set, limits the number of consecutive failed attempts.
    """

    def __init__(
        self,
        url: str,
        connector: Connector,
        reconnect_policy: Optional[_ReconnectPolicy] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        self.url = url
        self.connector = connector
        self.reconnect_policy = reconnect_policy or _ReconnectPolicy()
        self.max_retries = max_retries

        self._transport: Optional[WebSocketTransport] = None
        self._state = ConnectionState.DISCONNECTED
        self._recv_queue: asyncio.Queue[str] = asyncio.Queue()
        self._send_queue: asyncio.Queue[str] = asyncio.Queue()
        self._task: Optional[asyncio.Task[Any]] = None
        self._stop = asyncio.Event()
        self._lock = asyncio.Lock()

    @property
    def state(self) -> ConnectionState:
        return self._state

    async def connect(self) -> None:
        async with self._lock:
            if self._task and not self._task.done():
                return
            self._stop.clear()
            self._task = asyncio.create_task(self._lifecycle())

    async def _lifecycle(self) -> None:
        attempts = 0
        backoff = self.reconnect_policy.min_backoff
        while not self._stop.is_set():
            try:
                self._state = ConnectionState.CONNECTING
                transport = await self.connector(self.url)
                self._transport = transport
                self._state = ConnectionState.CONNECTED
                logger.info("Connected to %s", self.url)
                # run reader and writer until transport fails or stop requested
                await self._run_connection(transport)
                # if we get here, transport closed normally; reset counters
                attempts = 0
                backoff = self.reconnect_policy.min_backoff
                self._transport = None
                self._state = ConnectionState.DISCONNECTED
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # pragma: no cover - network path
                attempts += 1
                logger.exception("Connection attempt failed (%s)", exc)
                if self.max_retries is not None and attempts >= self.max_retries:
                    logger.error("Max retries reached; stopping reconnection")
                    break
                # backoff with jitter
                wait = min(backoff, self.reconnect_policy.max_backoff)
                wait = wait * (1 + random.uniform(-0.5, 0.5))
                await asyncio.sleep(max(0.1, wait))
                backoff *= self.reconnect_policy.factor

        # exiting lifecycle
        self._state = ConnectionState.DISCONNECTED

    async def _run_connection(self, transport: WebSocketTransport) -> None:
        receiver = asyncio.create_task(self._receiver(transport))
        sender = asyncio.create_task(self._sender(transport))
        stop_wait = asyncio.create_task(self._stop.wait())
        try:
            done, pending = await asyncio.wait(
                [receiver, sender, stop_wait],
                return_when=asyncio.FIRST_COMPLETED,
            )
        finally:
            # cancel any pending tasks
            for t in (receiver, sender, stop_wait):
                if not t.done():
                    t.cancel()
        try:
            await transport.close()
        except Exception:
            logger.exception("Error while closing transport")

    async def _receiver(self, transport: WebSocketTransport) -> None:
        while not self._stop.is_set():
            try:
                msg = await transport.recv()
            except Exception as exc:
                logger.exception("Receiver error: %s", exc)
                break
            await self._recv_queue.put(msg)

    async def _sender(self, transport: WebSocketTransport) -> None:
        while not self._stop.is_set():
            try:
                msg = await self._send_queue.get()
                await transport.send(msg)
            except Exception as exc:
                logger.exception("Sender error: %s", exc)
                break

    async def send(self, data: str) -> None:
        """Queue outgoing message; ensure connected first."""
        # optimistic check: if disconnected, try to connect
        if self._state != ConnectionState.CONNECTED:
            await self.connect()
            # small pause to let connect start
            await asyncio.sleep(0)
        await self._send_queue.put(data)

    async def get_message(self, timeout: Optional[float] = None) -> Optional[str]:
        try:
            return await asyncio.wait_for(self._recv_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def messages(self) -> AsyncIterator[str]:
        """Async iterator over incoming messages until closed."""
        while True:
            msg = await self.get_message()
            if msg is None:
                break
            yield msg

    async def close(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._transport:
            try:
                await self._transport.close()
            except Exception:
                logger.exception("Error closing transport during client shutdown")
        self._state = ConnectionState.DISCONNECTED


# --- Real websockets connector (optional dependency) ---------------------
def websockets_connector_factory(timeout: Optional[float] = None) -> Connector:
    """Return a Connector that uses the `websockets` library.

    The returned connector will create a small adapter implementing the
    `WebSocketTransport` protocol. Importing `websockets` is deferred so the
    core module remains usable without the dependency for unit tests.
    """

    async def connector(url: str) -> WebSocketTransport:
        try:
            import websockets
        except Exception as exc:  # pragma: no cover - environment dependent
            raise ImportError(
                "websockets library is required for websockets_connector_factory; install via 'pip install websockets'"
            ) from exc

        class _WSAdapter:
            def __init__(self, ws: websockets.WebSocketClientProtocol) -> None:
                self._ws = ws

            async def send(self, data: str) -> None:
                await self._ws.send(data)

            async def recv(self) -> str:
                msg = await self._ws.recv()
                return msg

            async def close(self) -> None:
                await self._ws.close()

        ws = await websockets.connect(url, close_timeout=timeout or 10)
        return _WSAdapter(ws)

    return connector


async def run_live_example(url: str) -> None:  # pragma: no cover - manual example
    """Simple live-run example showing reconnection behavior.

    Usage (in an async-capable runner):

        from arsenal.connection.base_ws import run_live_example
        import asyncio

        asyncio.run(run_live_example("wss://echo.websocket.org"))

    Note: ensure `websockets` is installed to use this helper.
    """
    connector = websockets_connector_factory()
    client = BaseWebSocketClient(url, connector)
    await client.connect()
    try:
        # send a ping and print one incoming message
        await client.send("ping")
        msg = await client.get_message(timeout=5.0)
        print("received:", msg)
    finally:
        await client.close()
