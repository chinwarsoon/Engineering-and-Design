"""Phase 2 clock-offset calibration tests (T26)."""
from __future__ import annotations

from engine import clock


def test_calibrate_is_offset():
    # 1_000_000_000 ns (1.0 s) browser vs 1_000_300_000 ns (1.0003 s) server -> 0.3 ms.
    assert clock.calibrate(1_000_000_000, 1_000_300_000) == 0.3


def test_normalize_spans_inplace():
    spans = [{"start_time_unix_ns": 2_000_000_000, "clock_offset_ms": 0.0}]
    clock.normalize_spans(spans, 0.3)
    assert spans[0]["start_time_unix_ns"] == clock.normalize(2_000_000_000, 0.3)
    assert spans[0]["clock_offset_ms"] == 0.3


def test_offset_stable_roundtrip():
    base_ns = 5_000_000_000
    offset = clock.calibrate(1_000_000_000, 1_500_000_000)  # 0.5 ms
    norm = clock.normalize(base_ns, offset)
    assert clock.reverse_offset(norm, offset) == base_ns  # |Δt| stable, fully reversible
