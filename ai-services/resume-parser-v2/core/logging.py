"""
Logging infrastructure using structlog and Rich console logging.
Provides clean contextual logs for development and JSON format for production environments.
"""

import logging
import sys
from typing import Any
import structlog
from rich.console import Console
from rich.logging import RichHandler

from core.config import settings


def setup_logging() -> None:
    """Configures global structlog and standard logging handlers."""
    log_level = getattr(logging, settings.LOG_LEVEL.value, logging.INFO)

    # Standard logging setup
    handlers: list[logging.Handler] = []

    if settings.LOG_JSON_FORMAT or settings.is_production:
        # Stream handler for JSON output
        stream_handler = logging.StreamHandler(sys.stdout)
        handlers.append(stream_handler)
    else:
        # Rich console handler for beautiful colored development logs
        rich_handler = RichHandler(
            console=Console(stderr=True),
            show_path=False,
            enable_link_path=False,
            rich_tracebacks=settings.DEBUG,
        )
        handlers.append(rich_handler)

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers,
        force=True,
    )

    # Configure structlog processors
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.LOG_JSON_FORMAT or settings.is_production:
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ])
    else:
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "resume-parser-v2") -> structlog.stdlib.BoundLogger:
    """Retrieves a bound structlog logger instance."""
    return structlog.get_logger(name)
