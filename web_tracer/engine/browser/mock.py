"""engine/browser/mock.py — browser collector with no real browser (T22 acceptance + CI).

Implements ``BrowserTracer`` without Playwright so (a) the abstraction is proven runnable by a
mock and (b) CI exercises all six event types and the user-action root without launching Chromium.
Its spans are schema-validated exactly like the real adapter's, so it doubles as a contract guard.
"""
from __future__ import annotations

import time

from engine.browser.actions import run_actions
from engine.browser.base import Action, BrowserTracer, RecordConfig, make_span
from engine import ids
from engine.schema.validate import validate_span


class MockBrowserAdapter(BrowserTracer):
    COLLECTOR_NAME = "mock-browser"
    COLLECTOR_VERSION = "0.1.0"

    def __init__(self):
        self._trace_id = ids.new_trace_id()
        self._run_id = ids.new_trace_id()[:16]
        self._parent_span_id: str | None = None
        self._clock_offset_ms = 0.0
        self._events: list[dict] = []
        self._cfg: RecordConfig | None = None

    def capabilities(self) -> dict:
        return {"initiator": True, "traceparent": True, "cdp": False, "available": True}

    def start(self, cfg: RecordConfig) -> str:
        self._cfg = cfg
        self._run_id = ids.new_trace_id()[:16]
        self._emit(
            etype="navigation",
            name=cfg.url,
            layer="browser",
            kind="event",
            source={"file": "<page>", "symbol": "goto"},
            attributes={"url": cfg.url},
        )
        if cfg.actions:
            run_actions(
                self,
                cfg.actions,
                trace_id=self._trace_id,
                run_id=self._run_id,
                clock_offset_ms=self._clock_offset_ms,
            )
        else:
            self._sample_events()
        return self._run_id

    def _sample_events(self) -> None:
        """Emit the remaining five event types so every type is covered without actions."""
        self._emit(
            etype="http_request",
            name="https://app/api/document",
            layer="http",
            kind="request",
            source={"file": "static/js/document.js", "line": 145, "symbol": "submitDocument"},
            attributes={
                "http": {"method": "POST", "url": "https://app/api/document", "resource_type": "fetch"},
                "initiator": {
                    "file": "static/js/document.js",
                    "line": 145,
                    "function": "submitDocument",
                    "type": "fetch",
                },
            },
        )
        self._emit(
            etype="http_response",
            name="https://app/api/document",
            layer="http",
            kind="request",
            source={"file": "static/js/document.js", "symbol": "submitDocument"},
            attributes={
                "http": {
                    "method": "POST",
                    "url": "https://app/api/document",
                    "status": 200,
                    "req_bytes": 512,
                    "res_bytes": 1284,
                }
            },
        )
        self._emit(
            etype="console",
            name="log",
            layer="browser",
            kind="event",
            source={"file": "<console>"},
            attributes={"text": "loaded"},
        )
        self._emit(
            etype="error",
            name="pageerror",
            layer="browser",
            kind="event",
            source={"file": "<page>"},
            status="error",
            attributes={"message": "boom"},
        )
        self._emit(
            etype="dom_event",
            name="screenshot",
            layer="browser",
            kind="event",
            source={"file": "<page>"},
            attributes={"screenshot": "run_x/err.png"},
        )

    def stop(self) -> list[dict]:
        return list(self._events)

    def get_events(self) -> list[dict]:
        return list(self._events)

    # ---- action hooks ----
    def begin_user_span(self, span: dict) -> None:
        self._events.append(span)
        self._parent_span_id = span["span_id"]

    def end_user_span(self) -> None:
        self._parent_span_id = None

    def perform_action(self, action: Action) -> None:
        if action.kind == "click":
            self._emit(
                etype="dom_event",
                name=f"click:{action.selector}",
                layer="browser",
                kind="event",
                source={"file": "<page>", "symbol": "onClick"},
                attributes={"selector": action.selector},
                parent=self._parent_span_id,
            )

    # ---- internal ----
    def _emit(self, *, etype, name, layer, kind, source, start_ns=None, duration_ms=0.0, **kw) -> dict:
        span = make_span(
            trace_id=self._trace_id,
            span_id=ids.new_span_id(),
            parent_span_id=kw.pop("parent", None) or self._parent_span_id,
            layer=layer,
            event_type=etype,
            name=name,
            kind=kind,
            source=source,
            start_time_unix_ns=start_ns or time.time_ns(),
            duration_ms=duration_ms,
            run_id=self._run_id,
            clock_offset_ms=self._clock_offset_ms,
            **kw,
        )
        validate_span(span)
        self._events.append(span)
        return span
