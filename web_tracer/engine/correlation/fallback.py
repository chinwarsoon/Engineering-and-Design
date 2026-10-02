"""engine/correlation/fallback.py — URL + time-window fallback matching (T35).

Used when the primary ``trace_id`` join is impossible, i.e. when the browser never
carried a ``traceparent`` header (typically a CORS preflight that refused it) or the
server started a brand-new trace.

Algorithm (workplan §8.4 step 3):

  1. fingerprint both sides: HTTP method + normalised path (query stripped, path
     variables collapsed to ``{id}`` so ``/api/doc/123`` matches ``/api/doc/{id}``);
  2. keep candidates whose fingerprint matches (method+path first, path-only second);
  3. keep only candidates with ``|Δt| ≤ window_ms`` (default ±200 ms, R3);
  4. score: unique candidate ``0.8`` · several candidates (nearest wins) ``0.6`` ·
     path-only ``0.4``. Never 1.0 — a fallback is a guess and says so.

Anything that cannot be matched comes back with one of the six reasons, so the
report can explain *why* instead of just counting a failure (AGENTS.md §5.9).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlsplit

from .models import (
    DEFAULT_WINDOW_MS,
    METHOD_URL_TIME_WINDOW,
    REASON_CLOCK_SKEW,
    REASON_CORS_BLOCKED,
    REASON_MULTIPLE_CANDIDATES,
    REASON_NO_CANDIDATE,
    REASON_OUT_OF_WINDOW,
    SCORE_AMBIGUOUS,
    SCORE_PATH_ONLY,
    SCORE_UNIQUE,
    SKEW_FACTOR,
    NS_PER_MS,
    Match,
    preflight_blocked,
)

_HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
# "POST /api/document" — the shape OTel gives a Spring server span.
_NAME_RE = re.compile(r"^\s*([A-Za-z]+)\s+(/\S*)\s*$")
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_HEX_ID_LENGTHS = (16, 24, 32)  # otel/span id, mongo objectid, trace id


def _looks_like_id(seg: str) -> bool:
    """True for path segments that are almost certainly a variable, not a route part."""
    if not seg:
        return False
    if seg.isdigit():
        return True
    low = seg.lower()
    if _UUID_RE.match(low):
        return True
    if len(low) in _HEX_ID_LENGTHS and all(c in "0123456789abcdef-" for c in low):
        return True
    return False


def normalize_url(raw: str | None) -> str:
    """Normalise a URL to its route form: ``https://t/api/doc/123?q=1`` → ``/api/doc/{id}``.

    Scheme, host, query and fragment are dropped; numeric / uuid / hex id segments
    become ``{id}`` so a concrete request matches the server's route template.
    """
    if not raw:
        return ""
    s = str(raw).strip()
    try:
        parts = urlsplit(s)
    except ValueError:
        return s
    path = parts.path or "/"
    if not path.startswith("/"):
        # e.g. a bare "api/doc" or the span name form handled by the caller
        path = "/" + path
    segs = ["{id}" if _looks_like_id(seg) else seg for seg in path.split("/")]
    out = "/".join(segs) or "/"
    if len(out) > 1:
        out = out.rstrip("/")
    return out


def http_method_of(span: dict) -> str | None:
    """HTTP method of a span, from ``attributes.http.method`` or from its name."""
    attrs = span.get("attributes")
    if isinstance(attrs, dict):
        http = attrs.get("http")
        if isinstance(http, dict) and http.get("method"):
            return str(http["method"]).upper()
        for key in ("http.method", "http.request.method", "method"):
            if attrs.get(key):
                return str(attrs[key]).upper()
    m = _NAME_RE.match(str(span.get("name") or ""))
    if m and m.group(1).upper() in _HTTP_METHODS:
        return m.group(1).upper()
    return None


def http_url_of(span: dict) -> str | None:
    """URL / route of a span, from ``attributes.http.url`` or from its name."""
    attrs = span.get("attributes")
    if isinstance(attrs, dict):
        http = attrs.get("http")
        if isinstance(http, dict) and http.get("url"):
            return str(http["url"])
        for key in ("http.url", "http.target", "http.route", "url.full", "url.path"):
            if attrs.get(key):
                return str(attrs[key])
    m = _NAME_RE.match(str(span.get("name") or ""))
    if m and m.group(1).upper() in _HTTP_METHODS:
        return m.group(2)
    return None


def endpoint_key(span: dict) -> str | None:
    """``"POST /api/doc/{id}"`` — the join fingerprint, or None when no URL is known."""
    path = normalize_url(http_url_of(span))
    if not path:
        return None
    method = http_method_of(span)
    return f"{method} {path}" if method else path


def path_key(span: dict) -> str:
    """Normalised path only (method-agnostic, used for the 0.4 path-only tier)."""
    return normalize_url(http_url_of(span))


@dataclass
class _Candidate:
    span: dict
    method: str | None
    path: str
    t_ns: int


class FallbackMatcher:
    """Match browser request spans to Java handler spans by URL + time window.

    ``time_of`` maps a span to its clock-normalised start in nanoseconds; the
    correlation engine supplies it so both sides share one clock base.
    """

    def __init__(self, window_ms: int = DEFAULT_WINDOW_MS, skew_limit_ms: int | None = None):
        self.window_ms = int(window_ms or DEFAULT_WINDOW_MS)
        self.skew_limit_ms = int(skew_limit_ms if skew_limit_ms is not None else self.window_ms * SKEW_FACTOR)
        # Failures of the last :meth:`match` batch: [{span_id, name, url, reason, nearest_delta_ms}]
        self.failures: list[dict] = []

    # ── candidates ────────────────────────────────────────────────────────────────
    def candidates(self, java_handler_spans: list[dict], time_of: Callable[[dict], int] | None = None) -> list[_Candidate]:
        out: list[_Candidate] = []
        for s in java_handler_spans:
            path = path_key(s)
            if not path:
                continue  # a span without any URL can never be fingerprint-matched
            t = time_of(s) if time_of else int(s.get("start_time_unix_ns") or 0)
            out.append(_Candidate(span=s, method=http_method_of(s), path=path, t_ns=t))
        return out

    # ── single match ──────────────────────────────────────────────────────────────
    def match_one(
        self,
        unit: dict,
        java_handler_spans: list[dict],
        time_of: Callable[[dict], int] | None = None,
    ) -> tuple[Match | None, str | None, float | None]:
        """Correlate one browser request span.

        Returns ``(match, reason, nearest_delta_ms)``. Exactly one of ``match`` /
        ``reason`` is set: a match means "joined", a reason means "and here is why not".
        """
        if preflight_blocked(unit):
            return None, REASON_CORS_BLOCKED, None

        cands = self.candidates(java_handler_spans, time_of)
        if not cands:
            return None, REASON_NO_CANDIDATE, None

        u_path = path_key(unit)
        if not u_path:
            return None, REASON_NO_CANDIDATE, None
        u_method = http_method_of(unit)
        t_u = time_of(unit) if time_of else int(unit.get("start_time_unix_ns") or 0)

        full = [c for c in cands if c.path == u_path and (u_method is None or c.method == u_method)]
        pool = full or [c for c in cands if c.path == u_path]
        if not pool:
            return None, REASON_NO_CANDIDATE, None
        method_matched = bool(full) and u_method is not None

        # signed delta (java − browser); nearest candidate = smallest |delta|
        scored = [((c.t_ns - t_u) / NS_PER_MS, c) for c in pool]
        scored.sort(key=lambda pair: abs(pair[0]))
        nearest_abs = abs(scored[0][0])
        within = [(d, c) for d, c in scored if abs(d) <= self.window_ms]

        if within:
            delta, best = within[0]
            ambiguous = len(within) > 1
            if not method_matched:
                score = SCORE_PATH_ONLY
            elif ambiguous:
                score = SCORE_AMBIGUOUS
            else:
                score = SCORE_UNIQUE
            reason = REASON_MULTIPLE_CANDIDATES if ambiguous else None
            return (
                Match(
                    browser_span_id=unit.get("span_id") or "",
                    java_span_id=best.span.get("span_id") or "",
                    method=METHOD_URL_TIME_WINDOW,
                    score=score,
                    reason=reason,
                    delta_ms=round(delta, 3),
                ),
                None,
                round(nearest_abs, 3),
            )

        reason = REASON_CLOCK_SKEW if nearest_abs > self.skew_limit_ms else REASON_OUT_OF_WINDOW
        return None, reason, round(nearest_abs, 3)

    # ── batch match (documented shape, workplan §8.4) ──────────────────────────────
    def match(
        self,
        http_spans: list[dict],
        java_handler_spans: list[dict],
        time_of: Callable[[dict], int] | None = None,
    ) -> list[Match]:
        """Correlate every browser request span. Failures are recorded on ``self.failures``."""
        self.failures = []
        out: list[Match] = []
        for unit in http_spans:
            m, reason, delta = self.match_one(unit, java_handler_spans, time_of)
            if m is not None:
                out.append(m)
            else:
                self.failures.append(
                    {
                        "span_id": unit.get("span_id"),
                        "name": unit.get("name"),
                        "url": http_url_of(unit),
                        "reason": reason,
                        "nearest_delta_ms": delta,
                    }
                )
        return out
