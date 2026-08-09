from decimal import Decimal

import pytest

from arsenal.risk.engine import (
    PreTradeRiskEngine,
    max_qty_rule,
    notional_limit_rule,
    Order,
    RiskRejected,
)


def test_accept_and_reject_rules() -> None:
    engine = PreTradeRiskEngine()
    engine.add_rule(max_qty_rule(Decimal("100")))
    engine.add_rule(notional_limit_rule(Decimal("10000")))

    ok_order: Order = {"symbol": "FOO", "qty": Decimal("10"), "price": Decimal("5")}
    engine.validate(ok_order)  # should not raise

    bad_qty: Order = {"symbol": "FOO", "qty": Decimal("200"), "price": Decimal("1")}
    with pytest.raises(RiskRejected):
        engine.validate(bad_qty)

    bad_notional: Order = {"symbol": "BAR", "qty": Decimal("100"), "price": Decimal("200")}
    with pytest.raises(RiskRejected):
        engine.validate(bad_notional)
