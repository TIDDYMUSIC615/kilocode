"""Position keeper with VWAP accounting, cash, realized PnL, and drawdown circuit breaker."""

from __future__ import annotations

from decimal import Decimal, getcontext
from typing import Dict, List, Tuple

from .position_models import Position


getcontext().prec = 28


class CircuitBreakerTripped(Exception):
    pass


class PositionKeeper:
    def __init__(self, drawdown_threshold: Decimal = Decimal("0.2")) -> None:
        self.positions: Dict[str, Position] = {}
        self.cash: Decimal = Decimal("0")
        self.realized: Decimal = Decimal("0")
        self.market: Dict[str, Decimal] = {}
        self.equity_history: List[Decimal] = []
        self.peak_equity: Decimal = Decimal("0")
        self.drawdown_threshold = drawdown_threshold
        self.tripped = False

    def apply_trade(self, symbol: str, qty: Decimal, price: Decimal) -> Decimal:
        """Apply a trade, update cash, position, and realized PnL. Returns realized."""
        pos = self.positions.get(symbol)
        if pos is None:
            pos = Position(symbol=symbol, qty=Decimal("0"), vwap=Decimal("0"))
            self.positions[symbol] = pos

        # cash decreases by qty * price (buy positive -> cash -= cost)
        self.cash -= qty * price

        realized = pos.apply_trade(qty, price)
        self.realized += realized

        return realized

    def update_market_price(self, symbol: str, price: Decimal) -> None:
        self.market[symbol] = price
        self._update_equity()

    def _update_equity(self) -> None:
        # compute total equity as cash + realized + market value of positions
        total = self.cash + self.realized
        for s, pos in self.positions.items():
            mp = self.market.get(s)
            if mp is None:
                continue
            total += pos.qty * mp
        self.equity_history.append(total)
        if total > self.peak_equity:
            self.peak_equity = total
        self._check_drawdown(total)

    def _check_drawdown(self, current: Decimal) -> None:
        if self.peak_equity == 0:
            return
        dd = (self.peak_equity - current) / self.peak_equity
        if dd >= self.drawdown_threshold:
            self.tripped = True

    def get_total_equity(self) -> Decimal:
        if not self.equity_history:
            self._update_equity()
        return self.equity_history[-1]

    def generate_close_orders(self) -> List[Tuple[str, Decimal]]:
        """When circuit breaker trips, generate close orders for all positions.

        Returns list of (symbol, qty_to_close) where qty_to_close should be applied
        (negative of current qty).
        """
        orders: List[Tuple[str, Decimal]] = []
        if not self.tripped:
            return orders
        for s, pos in self.positions.items():
            if pos.qty != 0:
                orders.append((s, -pos.qty))
        return orders
