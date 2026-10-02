"""engine/logging_setup.py — tiered logging (AGENTS.md §5.9, no silent failure).

Every module logs status/warnings/errors through the configured logger. The setup
is idempotent: calling it twice returns the same logger without duplicating handlers.
"""
from __future__ import annotations

import logging
from pathlib import Path

DEFAULT_LEVEL = logging.INFO
_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def configure(
    name: str = "web_tracer",
    level: int = DEFAULT_LEVEL,
    log_file: str | Path | None = None,
) -> logging.Logger:
    """Configure and return the named logger. Idempotent."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    logger.addHandler(handler)
    if log_file is not None:
        fh = logging.FileHandler(str(log_file))
        fh.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(fh)
    logger.info(
        "logging configured: name=%s level=%s file=%s",
        name,
        logging.getLevelName(level),
        log_file,
    )
    return logger
