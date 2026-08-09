"""Pre-trade risk engine with chain-of-responsibility style rules.

Rules are synchronous and intentionally simple; they operate on an `Order`
TypedDict and raise `RiskRejected` to block orders that violate constraints.
All numeric work uses `decimal.Decimal`.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from typing import Callable, List, TypedDict


# Set a sane default precision for risk math; callers may override.
getcontext().prec = 28


class RiskRejected(Exception):
    pass


class Order(TypedDict):
    symbol: str
    qty: Decimal
    price: Decimal


class RiskRule:
    """Callable rule type: raise `RiskRejected` on failure."""

    def __init__(self, fn: Callable[[Order], None], name: str | None = None) -> None:
        self.fn = fn
        self.name = name or getattr(fn, "__name__", "unnamed")

    def check(self, order: Order) -> None:
        self.fn(order)


class PreTradeRiskEngine:
    def __init__(self) -> None:
        self.rules: List[RiskRule] = []

    def add_rule(self, rule: RiskRule) -> None:
        self.rules.append(rule)

    def validate(self, order: Order) -> None:
        for rule in self.rules:
            rule.check(order)


# Common rules
def max_qty_rule(max_qty: Decimal) -> RiskRule:
    def _check(order: Order) -> None:
        if order["qty"] > max_qty:
            raise RiskRejected(f"qty {order['qty']} > max {max_qty}")

    return RiskRule(_check, name="max_qty")


def notional_limit_rule(max_notional: Decimal) -> RiskRule:
    def _check(order: Order) -> None:
        notional = order["qty"] * order["price"]
        if notional > max_notional:
            raise RiskRejected(f"notional {notional} > max {max_notional}")

    return RiskRule(_check, name="notional_limit")
