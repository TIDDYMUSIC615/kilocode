"""Internal backtest helpers."""

from decimal import Decimal


def pnl(start: Decimal, end: Decimal) -> Decimal:
    return end - start
