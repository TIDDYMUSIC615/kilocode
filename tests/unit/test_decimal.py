from decimal import Decimal, getcontext


def test_decimal_addition() -> None:
    getcontext().prec = 28
    a = Decimal("1.10")
    b = Decimal("2.20")
    assert a + b == Decimal("3.30")
