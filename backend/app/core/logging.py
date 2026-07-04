"""
Logging configuration for the application.

Sets up structured logging with consistent formatting
across all modules. Log level is driven by settings.
"""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure the root logger with console output.
    Format includes timestamp, level, module name, and message.
    """
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
    )

    # Quiet down noisy third-party loggers if not debugging
    if not settings.DEBUG:
        for logger_name in ("httpx", "httpcore", "urllib3"):
            logging.getLogger(logger_name).setLevel(logging.WARNING)