"""Master System Bootstrap: initialize and wire core trading modules."""

from __future__ import annotations

import asyncio
import logging
import signal
from typing import Optional

try:
    from aiohttp import web
except Exception:  # pragma: no cover - optional dependency
    web = None

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from arsenal.alpha.event_bus import EventBus
from arsenal.backtest.kill_switch import KillSwitch
from arsenal.backtest.engine import BacktestEngine
from arsenal.telemetry.logger import get_logger
from arsenal.telemetry.metrics import Metrics


class Master:
    def __init__(self) -> None:
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.stop_event = asyncio.Event()
        self.bus = EventBus()
        self.kill_switch = KillSwitch()
        self.metrics = Metrics()
        self.logger = get_logger("arsenal.master")
        self.engine = BacktestEngine(self.bus, self.kill_switch)
        self._task: Optional[asyncio.Task] = None
        self._runner: Optional[web.AppRunner] = None

    async def start(self) -> None:
        self.logger.info("bootstrap.start")
        # wire signal handlers
        try:
            self.loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                try:
                    self.loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
                except NotImplementedError:
                    # Windows may not support add_signal_handler in some environments
                    pass
        except Exception:
            pass

        # start metrics HTTP endpoint for Prometheus scraping
        from arsenal.config import settings

        if web is None:
            self.logger.warning("aiohttp not available; metrics endpoint disabled")
        else:
            try:
                app = web.Application()

                async def metrics_handler(_: web.Request) -> web.Response:
                    data = generate_latest(self.metrics.registry)
                    return web.Response(body=data, content_type=CONTENT_TYPE_LATEST)

                app.router.add_get("/metrics", metrics_handler)
                self._runner = web.AppRunner(app)
                await self._runner.setup()
                site = web.TCPSite(self._runner, "0.0.0.0", settings.prometheus_port)
                await site.start()
                self.logger.info("metrics endpoint listening on 0.0.0.0:%s", settings.prometheus_port)
            except Exception as exc:
                self.logger.exception("failed to start metrics endpoint: %s", exc)

        self._task = asyncio.create_task(self.run())
        await self.stop_event.wait()

    async def run(self) -> None:
        # placeholder: would start subsystems here
        self.logger.info("bootstrap.running")
        # wait until stop requested
        await self.stop_event.wait()

    async def stop(self) -> None:
        self.logger.info("bootstrap.stopping")
        self.stop_event.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        # cleanup metrics HTTP runner
        if self._runner:
            try:
                await self._runner.cleanup()
            except Exception:
                self.logger.exception("error cleaning up aiohttp runner")
        

def main() -> None:
    m = Master()
    try:
        asyncio.run(m.start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
