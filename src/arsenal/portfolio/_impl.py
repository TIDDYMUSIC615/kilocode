"""Internal portfolio implementation."""

from decimal import Decimal
from typing import TypedDict


class Holding(TypedDict):
    symbol: str
    qty: Decimal


def value_add(a: Decimal, b: Decimal) -> Decimal:
    return a + b
