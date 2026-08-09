"""Risk module internals."""

from decimal import Decimal


def max_drawdown(equity: list[Decimal]) -> Decimal:
    if not equity:
        return Decimal(0)
    return max(equity) - min(equity)
