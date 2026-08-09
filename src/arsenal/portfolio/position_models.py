"""Position models and helpers for VWAP accounting and flips."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Position:
    symbol: str
    qty: Decimal
    vwap: Decimal

    def apply_trade(self, trade_qty: Decimal, trade_price: Decimal) -> Decimal:
        """Apply a trade to this position.

        Returns realized PnL (Decimal). Positive realized means profit.
        Trade conventions: trade_qty > 0 = buy, trade_qty < 0 = sell.
        """
        # same sign => increase position (or open)
        if self.qty == 0 or (self.qty > 0 and trade_qty > 0) or (self.qty < 0 and trade_qty < 0):
            new_qty = self.qty + trade_qty
            if self.qty == 0:
                # opening a new position: set vwap = trade_price
                self.vwap = trade_price
            else:
                # weighted average for same-direction add
                # new_vwap = (old_qty*old_vwap + trade_qty*trade_price) / new_qty
                self.vwap = (
                    (self.qty * self.vwap) + (trade_qty * trade_price)
                ) / new_qty
            self.qty = new_qty
            return Decimal(0)

        # opposite sign => closing or flipping
        # closing amount is min(abs(trade_qty), abs(self.qty))
        close_qty = min(abs(trade_qty), abs(self.qty))
        old_qty = self.qty
        realized = close_qty * (trade_price - self.vwap) if old_qty > 0 else close_qty * (
            self.vwap - trade_price
        )

        # update qty
        new_qty = old_qty + trade_qty
        self.qty = new_qty

        # if flipped (position sign changed relative to old_qty), set new vwap to trade_price for remainder
        if old_qty != 0 and (old_qty > 0 and new_qty < 0 or old_qty < 0 and new_qty > 0):
            # we flipped: remaining qty should use trade_price as vwap
            self.vwap = trade_price
        elif new_qty == 0:
            # fully closed
            self.vwap = Decimal(0)

        return realized
