"""engine/java/otlp_receiver.py — OTLP/HTTP receiver: dual channel + batch write (T29, §8.4).

The receiver accepts OTLP spans over HTTP on the same :8100 service port (the OTel agent is
pointed at ``/v1/traces``). It supports both the **protobuf** and **json** channels; when a
protobuf payload arrives but the protobuf runtime is missing it downgrades with an explicit
WARN (never silent, workplan §8.4 rule 4). Spans are accumulated in memory and batch-written
to ``output/runs/<run_id>/java_trace.json`` on stop, so a trace imported on another machine
yields the same tree (offline replay, §8.6).
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

from engine import config, paths
from engine.browser.base import new_run_id
from engine.java import otlp_decode

import logging

logger = logging.getLogger("web_tracer.otlp")


class OtlpReceiver:
    def __init__(
        self,
        host: str = config.SERVICE_HOST,
        port: int = config.SERVICE_PORT,
        out_dir: Path | None = None,
        channel: str = "auto",
        run_id: str | None = None,
    ):
        self.host = host
        self.port = port
        self.out_dir = Path(out_dir) if out_dir else paths.runs_root()
        self.channel = channel  # "auto" | "protobuf" | "json"
        self._run_id = run_id
        self._spans: list[dict] = []
        self._lock = threading.Lock()
        self._running = False
        self._last_batch_at: int | None = None
        self._downgraded = False

    # ---- lifecycle ----
    def start(self, run_id: str | None = None) -> str:
        self._run_id = run_id or new_run_id()
        self._running = True
        self._spans = []
        self._last_batch_at = None
        self._downgraded = False
        return self._run_id

    def set_run(self, run_id: str) -> None:
        self._run_id = run_id

    def stop(self) -> list[dict]:
        self._running = False
        spans = list(self._spans)
        if self._run_id:
            self._persist(self._run_id, spans)
        return spans

    # ---- ingest ----
    def ingest(self, body: bytes, content_type: str) -> int:
        if not self._running:
            raise RuntimeError("receiver not started")
        if "protobuf" in (content_type or "").lower() and self.effective_channel() != "protobuf":
            # protobuf requested but we cannot decode it -> downgrade flag + explicit error
            self._downgraded = True
            logger.warning("OTLP protobuf unavailable; agent must use http/json (channel downgraded)")
            raise otlp_decode.ProtobufUnavailable(
                "protobuf channel unavailable; set -Dotel.exporter.otlp.protocol=http/json"
            )
        spans = otlp_decode.decode(body, content_type, self._run_id)
        with self._lock:
            self._spans.extend(spans)
            self._last_batch_at = time.time_ns()
        return len(spans)

    def effective_channel(self) -> str:
        """The channel we can actually serve: protobuf only if its deps are importable."""
        if self.channel == "json":
            return "json"
        try:  # pragma: no cover - depends on an optional dependency
            import opentelemetry.proto.collector.trace.v1.trace_service_pb2  # noqa: F401
            return "protobuf"
        except Exception:
            return "json"

    def get_spans(self) -> list[dict]:
        return list(self._spans)

    def status(self) -> dict:
        return {
            "running": self._running,
            "port": self.port,
            "span_count": len(self._spans),
            "last_batch_at": self._last_batch_at,
            "run_id": self._run_id,
            "channel": self.effective_channel(),
            "requested_channel": self.channel,
            "downgraded": self._downgraded,
        }

    def _persist(self, run_id: str, spans: list[dict]) -> Path:
        d = paths.run_dir(run_id)
        p = d / "java_trace.json"
        p.write_text(json.dumps(spans, indent=2), encoding="utf-8")
        return p
