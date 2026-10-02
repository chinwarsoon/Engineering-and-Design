"""engine/browser/traceparent.py — W3C traceparent injection + CORS preflight probe (T17/T24).

The initiating-function problem is solved by the page-side ``initiator_script.js`` patch
(``add_init_script``), not by ``extraHTTPHeaders`` — the latter is page-level and cannot name
the function that started the request. This module owns (a) the per-page ``traceparent``
header hook point and (b) the CORS preflight probe that decides whether the server will
strip ``traceparent`` (in which case correlation must downgrade to url_time_window).
"""
from __future__ import annotations

from dataclasses import dataclass

import httpx

from engine import ids


@dataclass
class CorsProbe:
    """Result of a preflight probe carrying a ``traceparent`` header."""

    observed: bool
    allowed: bool
    note: str = ""


def ensure_headers(page, inject: bool) -> None:
    """Hook point for per-request ``traceparent`` injection.

    With ``inject=False`` this is a no-op. When ``inject=True`` the real header is attached
    by the page-side patch (see ``initiator_script.js``); ``extraHTTPHeaders`` is intentionally
    NOT used here because it cannot capture the initiating function (workplan §8.3.1).
    """
    if not inject:
        return
    # The concrete per-request header is applied inside the injected script; this function
    # exists so adapters have a single, named call site for the inject decision.


def probe_cors(url: str, timeout: float = 5.0) -> CorsProbe:
    """OPTIONS-preflight probe that carries a ``traceparent`` header.

    If the server lists ``traceparent`` in ``access-control-allow-headers`` the real request
    will keep the header and correlation can use ``trace_id`` (confidence 1.0). Any network or
    import failure is treated as *allowed* (cannot determine) so recording still proceeds; only
    an explicit missing ACAO/traceparent triggers a downgrade flag (``allowed=False``).
    """
    try:
        tp = ids.make_traceparent(ids.new_trace_id(), ids.new_span_id())
        r = httpx.options(
            url,
            headers={
                "traceparent": tp,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "traceparent",
            },
            timeout=timeout,
            follow_redirects=True,
        )
    except Exception as e:  # network/import error — cannot determine, assume allowed
        return CorsProbe(observed=False, allowed=True, note=f"probe skipped: {e}")
    allow_headers = r.headers.get("access-control-allow-headers", "").lower()
    allowed = "access-control-allow-headers" in {k.lower() for k in r.headers} and "traceparent" in allow_headers
    return CorsProbe(observed=True, allowed=allowed, note=f"status={r.status_code}")
