"""engine/browser/actions.py — user actions as the trace root (T25, §8.4).

A recorded journey is a list of ``Action`` steps. Each step becomes a ``layer=user`` root
span; the browser/network spans the step triggers nest beneath it (M4: "user action becomes
the trace root"). The collector adapter implements three tiny hooks so this module stays
adapter-agnostic (works for Playwright and the MockBrowserAdapter alike).
"""
from __future__ import annotations

import time

from engine.browser.base import Action, make_span
from engine import ids


def make_user_action_span(
    action: Action,
    *,
    trace_id: str,
    run_id: str,
    clock_offset_ms: float = 0.0,
    parent_span_id: str | None = None,
    start_time_unix_ns: int | None = None,
) -> dict:
    """Build the ``layer=user`` root span for one action step."""
    if start_time_unix_ns is None:
        start_time_unix_ns = time.time_ns()
    name = f"{action.kind}:{action.selector or action.url or ''}"
    return make_span(
        trace_id=trace_id,
        span_id=ids.new_span_id(),
        parent_span_id=parent_span_id,
        layer="user",
        event_type="user_action",
        name=name,
        kind="event",
        source={"file": "<user>", "symbol": action.kind},
        start_time_unix_ns=start_time_unix_ns,
        duration_ms=0.0,
        confidence=1.0,
        correlation_method="inferred",
        correlation_score=0.9,
        attributes={
            "action": action.kind,
            "selector": action.selector,
            "value": action.value,
            "url": action.url,
        },
        clock_offset_ms=clock_offset_ms,
        run_id=run_id,
        collector_name="user-action",
    )


def run_actions(adapter, actions: list[Action], *, trace_id: str, run_id: str, clock_offset_ms: float = 0.0) -> list[dict]:
    """Drive ``adapter`` through ``actions`` as user-action roots.

    The adapter must implement ``begin_user_span(span)``, ``perform_action(action)`` and
    ``end_user_span()`` so it can append the root span and set the parenting context that
    subsequent browser/network spans should nest under.
    """
    roots: list[dict] = []
    for action in actions:
        span = make_user_action_span(action, trace_id=trace_id, run_id=run_id, clock_offset_ms=clock_offset_ms)
        adapter.begin_user_span(span)
        try:
            adapter.perform_action(action)
        finally:
            adapter.end_user_span()
        roots.append(span)
    return roots
