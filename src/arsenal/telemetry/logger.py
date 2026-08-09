"""Structured JSON logging configuration using structlog."""

from __future__ import annotations

import logging
from typing import Any, Dict

import structlog


def configure_logging(level: int = logging.INFO) -> None:
    renderer = structlog.processors.JSONRenderer()
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    processors = [structlog.contextvars.merge_contextvars, timestamper, renderer]
    logging.basicConfig(level=level)
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    configure_logging()
    return structlog.get_logger(name)

def log_event(logger: structlog.BoundLogger, event: str, **kwargs: Any) -> None:
    logger.info(event, **kwargs)
