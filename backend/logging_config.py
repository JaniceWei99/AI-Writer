"""Structured logging configuration for the application."""

import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure the root logger and return the app logger."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on reload
    if not root.handlers:
        root.addHandler(handler)

    # Quiet noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logging.getLogger("app")
