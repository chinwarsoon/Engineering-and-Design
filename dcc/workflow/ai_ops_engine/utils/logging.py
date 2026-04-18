"""
AI Ops Engine — Logging Utilities

Tiered logging helpers following agent_rule.md Section 6.
Breadcrumb: used by all ai_ops_engine modules.
"""

from __future__ import annotations
import logging


def get_engine_logger(name: str) -> logging.Logger:
    """
    Get a logger for an ai_ops_engine module.

    Args:
        name: Module name (e.g. 'ai_ops_engine.core.engine')

    Returns:
        Configured logger
    """
    return logging.getLogger(name)


def log_step(logger: logging.Logger, step: str, detail: str, level: int = 1) -> None:
    """
    Log a processing step with indentation per hierarchy level.

    Args:
        logger: Logger instance
        step: Step name
        detail: Detail message
        level: Hierarchy depth (1=info, 2=debug, 3=trace)
    """
    indent = "  " * level
    msg = f"{indent}[ai_ops] {step}: {detail}"
    if level == 1:
        logger.info(msg)
    elif level == 2:
        logger.debug(msg)
    else:
        logger.debug(msg)
