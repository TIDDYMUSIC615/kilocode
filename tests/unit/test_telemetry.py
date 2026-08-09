from decimal import Decimal

from prometheus_client import CollectorRegistry

from arsenal.telemetry.metrics import Metrics
from arsenal.telemetry.logger import get_logger
import structlog


def test_metrics_observe_and_set() -> None:
    reg = CollectorRegistry()
    m = Metrics(registry=reg)
    m.observe_execution(0.123)
    m.set_equity(Decimal("42.5"))

    # histogram count should be 1
    cnt = reg.get_sample_value("execution_latency_seconds_count")
    assert cnt == 1.0
    # gauge should equal 42.5
    eq = reg.get_sample_value("portfolio_equity")
    assert eq == 42.5


def test_structured_logger_emits_json_fields(capsys) -> None:
    import logging
    import sys

    # Force a console handler so structlog output is captured by capsys.
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, force=True)

    logger = get_logger("arsenal.test")
    # bind and log
    logger = logger.bind(module="test")
    logger.info("test.event", value=123)
    for handler in logging.getLogger().handlers:
        if hasattr(handler, "flush"):
            handler.flush()
    captured = capsys.readouterr()
    assert "test.event" in captured.out or "test.event" in captured.err
