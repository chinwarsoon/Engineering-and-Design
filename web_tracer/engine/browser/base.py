"""engine/browser/base.py — BrowserTracer abstraction (workplan T22, §8.4).

Every browser collector (Playwright, the CI MockBrowserAdapter, later CDP/BiDi adapters)
implements this ABC so the recorder and backend routes stay adapter-agnostic. The shared
``make_span`` helper guarantees every collector emits a schema-compliant SpanEvent dict.
"""
from __future__ import annotations

import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


def new_run_id() -> str:
    """A human-readable, collision-resistant recording id (run-YYYYMMDD-HHMMSS-ab)."""
    return "run-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(2)


@dataclass
class Action:
    """One step in a recorded journey (T25). The adapter performs it and emits a
    ``layer=user`` root span so the triggered browser/network spans nest beneath it."""

    kind: str  # click | navigate | fill | wait | hover | scroll
    selector: str | None = None
    value: str | None = None
    url: str | None = None
    timeout_ms: int = 30_000


@dataclass
class RecordConfig:
    """Frozen recording contract (workplan §8.4). Single shape used by every adapter
    and by ``POST /browser/record/start`` (T28)."""

    url: str
    headless: bool = True
    inject_traceparent: bool = True
    capture_initiator: bool = True
    capture_console: bool = True
    screenshot_on_error: bool = True
    actions: list[Action] = field(default_factory=list)
    timeout_ms: int = 30_000
    out_dir: Path | None = None


class BrowserTracer(ABC):
    """Abstract browser collector. Implementations return plain SpanEvent dicts
    (validated against ``engine/schema/span_schema.json``)."""

    @abstractmethod
    def start(self, cfg: RecordConfig) -> str:
        """Begin recording; return the ``run_id``."""

    @abstractmethod
    def stop(self) -> list[dict]:
        """End recording and return the collected SpanEvent dicts."""

    @abstractmethod
    def get_events(self) -> list[dict]:
        """Return events collected so far without stopping."""

    @abstractmethod
    def capabilities(self) -> dict:
        """Return ``{initiator, traceparent, cdp, available}``."""


def make_span(
    *,
    trace_id: str,
    span_id: str,
    parent_span_id: str | None,
    layer: str,
    event_type: str,
    name: str,
    kind: str,
    source: dict,
    start_time_unix_ns: int,
    duration_ms: float,
    status: str = "ok",
    confidence: float = 1.0,
    correlation_method: str = "trace_id",
    correlation_score: float = 1.0,
    correlation_reason: str | None = None,
    attributes: dict | None = None,
    clock_offset_ms: float = 0.0,
    run_id: str,
    collector_name: str = "browser",
    collector_version: str = "0.1.0",
    language: str | None = None,
    resource: dict | None = None,
) -> dict:
    """Build a schema-compliant SpanEvent dict (workplan §8.3.1).

    ``source`` must carry at least ``file``; other source keys are copied only when
    present so adapters never emit ``null`` for optional fields (the schema forbids it).
    """
    src: dict[str, Any] = {"file": "<unknown>"}
    if isinstance(source, dict):
        src["file"] = source.get("file", "<unknown>")
        for key in ("line", "column", "symbol", "class_name", "package"):
            if source.get(key) is not None:
                src[key] = source[key]
    span: dict[str, Any] = {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "layer": layer,
        "event_type": event_type,
        "name": name,
        "kind": kind,
        "source": src,
        "start_time_unix_ns": start_time_unix_ns,
        "duration_ms": duration_ms,
        "status": status,
        "confidence": confidence,
        "correlation": {
            "method": correlation_method,
            "score": correlation_score,
            "reason": correlation_reason,
        },
        "attributes": attributes or {},
        "clock_offset_ms": clock_offset_ms,
        "collector": {"name": collector_name, "version": collector_version, "run_id": run_id},
    }
    if language is not None:
        span["language"] = language
    if resource is not None:
        span["resource"] = resource
    return span
