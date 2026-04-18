"""
AI Ops Engine — Event Stream

Standard SSE event payloads for live pipeline monitoring.
Breadcrumb: pipeline steps → emit_*() → JSON event strings → SSE clients
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from typing import Any, Dict, Generator, Optional

logger = logging.getLogger(__name__)

# Global event queue (in-process, single-run)
_event_queue: list = []


def _make_event(event_type: str, data: Dict[str, Any]) -> str:
    """
    Format a server-sent event string.

    Args:
        event_type: SSE event name
        data: Event payload dict

    Returns:
        SSE-formatted string
    """
    payload = json.dumps({**data, "timestamp": datetime.now().isoformat()})
    return f"event: {event_type}\ndata: {payload}\n\n"


def emit_pipeline_status(step: str, status: str, message: str = "") -> None:
    """
    Emit a pipeline step status event.

    Args:
        step: Step name (e.g. 'step4_document_processing')
        status: 'running' | 'complete' | 'error'
        message: Optional detail message
    """
    event = _make_event("pipeline_step", {
        "step": step,
        "status": status,
        "message": message,
    })
    _event_queue.append(event)
    logger.debug(f"[event_stream] {step} → {status}")


def emit_pipeline_warning(step: str, message: str, context: Optional[Dict] = None) -> None:
    """
    Emit a pipeline warning event.

    Args:
        step: Step name
        message: Warning message
        context: Optional additional context
    """
    event = _make_event("pipeline_warning", {
        "step": step,
        "message": message,
        "context": context or {},
    })
    _event_queue.append(event)
    logger.debug(f"[event_stream] WARNING {step}: {message}")


def emit_pipeline_error(step: str, error: str, fatal: bool = False) -> None:
    """
    Emit a pipeline error event.

    Args:
        step: Step name
        error: Error message
        fatal: True if this is a fail-fast error
    """
    event = _make_event("pipeline_error", {
        "step": step,
        "error": error,
        "fatal": fatal,
    })
    _event_queue.append(event)
    logger.debug(f"[event_stream] ERROR {step}: {error}")


def emit_pipeline_artifact(artifact_type: str, path: str) -> None:
    """
    Emit an artifact export completion event.

    Args:
        artifact_type: 'csv' | 'excel' | 'json' | 'summary' | 'ai_insight'
        path: File path of the exported artifact
    """
    event = _make_event("pipeline_artifact", {
        "artifact_type": artifact_type,
        "path": path,
    })
    _event_queue.append(event)
    logger.debug(f"[event_stream] ARTIFACT {artifact_type}: {path}")


def get_event_stream() -> Generator[str, None, None]:
    """
    Generator that yields all queued SSE events.

    Yields:
        SSE-formatted event strings
    """
    while _event_queue:
        yield _event_queue.pop(0)


def clear_events() -> None:
    """Clear the event queue (call at start of each pipeline run)."""
    _event_queue.clear()


def get_all_events() -> list:
    """Return all queued events without consuming them."""
    return list(_event_queue)
