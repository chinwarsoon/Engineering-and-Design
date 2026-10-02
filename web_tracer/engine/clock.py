"""engine/clock.py — clock-offset normalisation (workplan §8.4).

The browser and the backend may run on clocks that are slightly offset. Each
collector records its offset from the base clock (the browser, per workplan
§8.3.2 ``clock.base``), so every span's ``start_time`` can be normalised to the
base clock before correlation. ``estimate_offset`` measures the offset; ``normalize``
applies it; ``reverse_offset`` undoes it (acceptance: an injected offset can be
reversed).
"""
from __future__ import annotations

_NS_PER_MS = 1_000_000


def normalize(ts_local_ns: int, offset_ms: float) -> int:
    """Return base-clock nanoseconds for a local timestamp plus this collector's offset.

    ``offset_ms`` is ``server_ts - browser_ts`` (ms); subtracting it maps a local
    (server) timestamp back onto the browser base clock.
    """
    return int(ts_local_ns - offset_ms * _NS_PER_MS)


def estimate_offset(browser_ts_ns: int, server_ts_ns: int) -> float:
    """Estimate the collector (server) offset from the browser base clock, in ms."""
    return (server_ts_ns - browser_ts_ns) / _NS_PER_MS


def reverse_offset(normalized_ns: int, offset_ms: float) -> int:
    """Undo :func:`normalize` — recover the local timestamp from base ns + offset."""
    return int(normalized_ns + offset_ms * _NS_PER_MS)


def calibrate(browser_ts_ns: int, server_ts_ns: int) -> float:
    """Phase 2 clock-offset calibration (T26): alias of :func:`estimate_offset`.

    Sample a (browser, server) timestamp pair at record start; the returned offset is
    the server's skew from the browser base clock and is held constant for the run so
    ``|Δt|`` between collectors stays stable.
    """
    return estimate_offset(browser_ts_ns, server_ts_ns)


def normalize_spans(spans: list[dict], offset_ms: float) -> None:
    """In-place normalise a list of SpanEvent dicts onto the browser base clock (T26).

    Subtracts ``offset_ms`` from every ``start_time_unix_ns`` and stamps
    ``clock_offset_ms`` so the correlation engine (P4) uses a single, stable base clock.
    """
    for span in spans:
        ts = span.get("start_time_unix_ns")
        if isinstance(ts, int):
            span["start_time_unix_ns"] = normalize(ts, offset_ms)
        span["clock_offset_ms"] = offset_ms
