"""engine/browser/playwright_adapter.py — full Playwright capture adapter (T23, §8.4).

Maps the six Phase 2 event types to SpanEvents (workplan §9 M2):
  navigation, click (dom_event), XHR (http_request + http_response), console, error, screenshot.

``playwright`` is an OPTIONAL dependency (requirements-optional.txt); its import is guarded so
this module imports cleanly even when Playwright is absent (CI uses ``MockBrowserAdapter``). Only
``start()`` raises if Playwright is missing. Every span is validated by ``_to_span`` before it is
kept, so malformed spans fail fast instead of corrupting the trace (AGENTS.md §5.9).
"""
from __future__ import annotations

import time
from pathlib import Path

from engine.browser.actions import run_actions
from engine.browser.base import Action, BrowserTracer, RecordConfig, make_span
from engine import ids, paths
from engine.schema.validate import validate_span

import logging

logger = logging.getLogger("web_tracer.browser")

try:
    from playwright.sync_api import Browser, Page, sync_playwright  # type: ignore

    _PLAYWRIGHT_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only where playwright is missing
    sync_playwright = None  # type: ignore
    Page = None  # type: ignore
    Browser = None  # type: ignore
    _PLAYWRIGHT_AVAILABLE = False

_INITIATOR_JS = (Path(__file__).parent / "initiator_script.js").read_text(encoding="utf-8")


class PlaywrightAdapter(BrowserTracer):
    COLLECTOR_NAME = "playwright-adapter"
    COLLECTOR_VERSION = "0.1.0"

    def __init__(self):
        self._trace_id = ids.new_trace_id()
        self._run_id = ids.new_trace_id()[:16]
        self._parent_span_id: str | None = None
        self._clock_offset_ms = 0.0  # browser IS the base clock; JVM skew handled in P4
        self._events: list[dict] = []
        self._cfg: RecordConfig | None = None
        self._request_spans: dict[str, str] = {}
        self._pw = None
        self._browser = None
        self._page: "Page | None" = None

    # ---- BrowserTracer interface ----
    def capabilities(self) -> dict:
        return {
            "initiator": _PLAYWRIGHT_AVAILABLE,
            "traceparent": True,
            "cdp": False,
            "available": _PLAYWRIGHT_AVAILABLE,
        }

    def start(self, cfg: RecordConfig) -> str:
        if not _PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "Playwright is not installed. Install via requirements-optional.txt (optional dep) "
                "or use the MockBrowserAdapter for CI without a browser."
            )
        self._cfg = cfg
        self._run_id = ids.new_trace_id()[:16]
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=cfg.headless)
        self._page = self._browser.new_page()
        if cfg.capture_initiator:
            self._page.add_init_script(_INITIATOR_JS)
        self._page.on("request", self._on_request)
        self._page.on("response", self._on_response)
        if cfg.capture_console:
            self._page.on("console", self._on_console)
        self._page.on("pageerror", self._on_pageerror)
        self._page.goto(cfg.url, timeout=cfg.timeout_ms)
        if cfg.actions:
            run_actions(
                self,
                cfg.actions,
                trace_id=self._trace_id,
                run_id=self._run_id,
                clock_offset_ms=self._clock_offset_ms,
            )
        return self._run_id

    def stop(self) -> list[dict]:
        try:
            if self._page is not None:
                self._page.close()
        finally:
            if self._browser is not None:
                self._browser.close()
            if self._pw is not None:
                self._pw.stop()
        return list(self._events)

    def get_events(self) -> list[dict]:
        return list(self._events)

    # ---- action hooks used by run_actions (T25) ----
    def begin_user_span(self, span: dict) -> None:
        self._events.append(span)
        self._parent_span_id = span["span_id"]

    def end_user_span(self) -> None:
        self._parent_span_id = None

    def perform_action(self, action: Action) -> None:
        if self._page is None:
            return
        if action.kind == "click" and action.selector:
            self._page.click(action.selector, timeout=action.timeout_ms)
        elif action.kind == "fill" and action.selector:
            self._page.fill(action.selector, action.value or "", timeout=action.timeout_ms)
        elif action.kind == "navigate" and action.url:
            self._page.goto(action.url, timeout=action.timeout_ms)
        elif action.kind == "hover" and action.selector:
            self._page.hover(action.selector, timeout=action.timeout_ms)
        elif action.kind == "wait":
            self._page.wait_for_timeout(action.timeout_ms)
        elif action.kind == "scroll" and action.selector:
            self._page.eval_on_selector(action.selector, "el => el.scrollIntoView()")
        # unknown kinds are ignored but still recorded as a user root span

    # ---- event -> span ----
    def _on_request(self, request) -> None:
        sid = ids.new_span_id()
        initiator = self._read_initiator(request.url) if self._cfg and self._cfg.capture_initiator else None
        attrs: dict = {
            "http": {
                "method": request.method,
                "url": request.url,
                "resource_type": request.resource_type,
            }
        }
        if initiator:
            attrs["initiator"] = initiator
        self._request_spans[request.url] = sid
        self._events.append(
            self._to_span(
                etype="http_request",
                name=request.url,
                layer="http",
                kind="request",
                source={"file": "<network>", "symbol": request.resource_type},
                start_ns=time.time_ns(),
                duration_ms=0.0,
                attributes=attrs,
                parent=self._parent_span_id,
                span_id=sid,
            )
        )

    def _on_response(self, response) -> None:
        req = response.request
        parent = self._request_spans.get(req.url, self._parent_span_id)
        self._events.append(
            self._to_span(
                etype="http_response",
                name=req.url,
                layer="http",
                kind="request",
                source={"file": "<network>", "symbol": req.resource_type},
                start_ns=time.time_ns(),
                duration_ms=0.0,
                attributes={
                    "http": {
                        "method": req.method,
                        "url": req.url,
                        "status": response.status,
                        "req_bytes": len(req.post_data or ""),
                        "res_bytes": _safe_len(response.body()),
                    }
                },
                parent=parent,
            )
        )

    def _on_console(self, msg) -> None:
        self._events.append(
            self._to_span(
                etype="console",
                name=msg.type,
                layer="browser",
                kind="event",
                source={"file": "<console>"},
                start_ns=time.time_ns(),
                duration_ms=0.0,
                attributes={"text": msg.text},
            )
        )

    def _on_pageerror(self, err) -> None:
        attrs: dict = {"message": str(err)}
        if self._cfg and self._cfg.screenshot_on_error and self._page is not None:
            try:
                shot = paths.run_dir(self._run_id) / f"error_{ids.new_span_id()}.png"
                self._page.screenshot(path=str(shot))
                attrs["screenshot"] = str(shot)
            except Exception as e:  # never fatal
                logger.warning("screenshot failed: %s", e)
        self._events.append(
            self._to_span(
                etype="error",
                name="pageerror",
                layer="browser",
                kind="event",
                source={"file": "<page>"},
                start_ns=time.time_ns(),
                duration_ms=0.0,
                status="error",
                attributes=attrs,
            )
        )

    def _read_initiator(self, url: str):
        if self._page is None:
            return None
        try:
            return self._page.evaluate(
                "(u) => { const ks = Object.keys(window.__wt_initiators || {});"
                " const k = ks.find(kk => kk.indexOf(u) === 0);"
                " return k ? window.__wt_initiators[k] : null; }",
                url,
            )
        except Exception:
            return None

    # ---- shared span builder (also unit-tested without a browser) ----
    def _to_span(
        self,
        *,
        etype: str,
        name: str,
        layer: str,
        kind: str,
        source: dict,
        start_ns: int,
        duration_ms: float,
        attributes: dict | None = None,
        parent: str | None = None,
        status: str = "ok",
        confidence: float = 1.0,
        correlation_method: str = "trace_id",
        correlation_score: float = 1.0,
        correlation_reason: str | None = None,
        language: str | None = None,
        resource: dict | None = None,
        span_id: str | None = None,
    ) -> dict:
        span = make_span(
            trace_id=self._trace_id,
            span_id=span_id or ids.new_span_id(),
            parent_span_id=parent if parent is not None else self._parent_span_id,
            layer=layer,
            event_type=etype,
            name=name,
            kind=kind,
            source=source,
            start_time_unix_ns=start_ns,
            duration_ms=duration_ms,
            status=status,
            confidence=confidence,
            correlation_method=correlation_method,
            correlation_score=correlation_score,
            correlation_reason=correlation_reason,
            attributes=attributes,
            clock_offset_ms=self._clock_offset_ms,
            run_id=self._run_id,
            collector_name=self.COLLECTOR_NAME,
            collector_version=self.COLLECTOR_VERSION,
            language=language,
            resource=resource,
        )
        validate_span(span)  # fail fast on malformed spans (no silent corruption)
        return span


def _safe_len(b) -> int:
    try:
        return len(b) if b is not None else 0
    except TypeError:
        return 0
