from decimal import Decimal

from arsenal.portfolio.position_keeper import PositionKeeper


def test_vwap_and_flip_and_realized() -> None:
    pk = PositionKeeper()
    # buy 10 @1.00
    pk.apply_trade("FOO", Decimal("10"), Decimal("1"))
    # buy 10 @2.00 => vwap should be 1.5
    pk.apply_trade("FOO", Decimal("10"), Decimal("2"))
    pos = pk.positions["FOO"]
    assert pos.qty == Decimal("20")
    assert pos.vwap == Decimal("3") / Decimal("2")

    # sell 25 @3.00 => closes 20 with realized 20*(3-1.5)=30, and opens short -5@3.0
    realized = pk.apply_trade("FOO", Decimal("-25"), Decimal("3"))
    assert realized == Decimal("30")
    pos = pk.positions["FOO"]
    assert pos.qty == Decimal("-5")
    assert pos.vwap == Decimal("3")


def test_drawdown_trips_and_generates_close_orders() -> None:
    pk = PositionKeeper(drawdown_threshold=Decimal("0.1"))
    # start with cash 0, buy 100 @10 -> cash -=1000
    pk.apply_trade("BAR", Decimal("100"), Decimal("10"))
    # set market price high -> equity increases
    pk.update_market_price("BAR", Decimal("11"))
    peak = pk.get_total_equity()
    assert peak > 0
    # drop market price to trigger >10% drawdown
    pk.update_market_price("BAR", Decimal("5"))
    assert pk.tripped is True
    orders = pk.generate_close_orders()
    assert orders and orders[0][0] == "BAR"
