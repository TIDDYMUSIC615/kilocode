from decimal import Decimal

import pytest

from arsenal.execution.adapters.base import BaseExecutionAdapter, ExecutionResult, Order
from arsenal.execution.router import OrderRouter


class FakeAdapter:
    async def execute(self, order: Order) -> ExecutionResult:
        return {"order_id": f"id-{order['symbol']}", "status": "filled"}


@pytest.mark.asyncio
async def test_router_dispatch_by_name() -> None:
    router = OrderRouter()
    adapter = FakeAdapter()
    router.register_adapter("test", adapter)

    order: Order = {"symbol": "FOO", "qty": Decimal("1"), "price": Decimal("1")}
    res = await router.route(order, adapter_name="test")
    assert res["status"] == "filled"
    assert res["order_id"] == "id-FOO"


@pytest.mark.asyncio
async def test_router_symbol_map() -> None:
    router = OrderRouter()
    adapter = FakeAdapter()
    router.register_adapter("equity", adapter)
    router.map_symbol("FO", "equity")

    order: Order = {"symbol": "FOO", "qty": Decimal("1"), "price": Decimal("1")}
    res = await router.route(order)
    assert res["status"] == "filled"
