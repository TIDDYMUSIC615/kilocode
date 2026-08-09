"""Base execution adapter protocol and simple helper types."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol, TypedDict


class Order(TypedDict):
    symbol: str
    qty: Decimal
    price: Decimal


class ExecutionResult(TypedDict):
    order_id: str
    status: str


class BaseExecutionAdapter(Protocol):
    async def execute(self, order: Order) -> ExecutionResult:  # pragma: no cover - interface
        """Execute an order and return an `ExecutionResult`."""
        ...
