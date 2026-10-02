"""engine/ids.py — W3C TraceContext id generation (workplan §8.4).

Span ids are 8 bytes (16 hex); trace ids are 16 bytes (32 hex). ``make_traceparent``
produces a ``traceparent`` header value of the form ``00-<trace_id>-<span_id>-<flags>``.
"""
from __future__ import annotations

import secrets


def new_trace_id() -> str:
    """Return a 32-hex-character W3C trace id."""
    return secrets.token_hex(16)


def new_span_id() -> str:
    """Return a 16-hex-character W3C span id."""
    return secrets.token_hex(8)


def make_traceparent(trace_id: str, span_id: str, sampled: bool = True) -> str:
    """Build a ``traceparent`` header value.

    Format: ``00-<trace_id>-<span_id>-<flags>`` where flags is ``01`` (sampled)
    or ``00``. ``trace_id``/``span_id`` must already be valid hex (no validation here).
    """
    flags = "01" if sampled else "00"
    return f"00-{trace_id}-{span_id}-{flags}"
