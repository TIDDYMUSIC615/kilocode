"""Internal execution implementation placeholders."""

from decimal import Decimal
from typing import TypedDict


class Order(TypedDict):
    symbol: str
    qty: Decimal


async def route_order(order: Order) -> dict:
    """Placeholder: validate Decimal qty and return event dict."""
    return {"status": "queued"}
