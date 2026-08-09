"""Prometheus metrics wrapper for Arsenal telemetry."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from prometheus_client import CollectorRegistry, Gauge, Histogram


class Metrics:
    def __init__(self, registry: Optional[CollectorRegistry] = None) -> None:
        self.registry = registry or CollectorRegistry()
        # execution latency in seconds
        self.execution_latency = Histogram(
            "execution_latency_seconds",
            "Execution latency in seconds",
            registry=self.registry,
        )
        # portfolio equity gauge
        self.portfolio_equity = Gauge(
            "portfolio_equity", "Portfolio total equity", registry=self.registry
        )

    def observe_execution(self, seconds: float) -> None:
        self.execution_latency.observe(seconds)

    def set_equity(self, value: Decimal) -> None:
        self.portfolio_equity.set(float(value))
