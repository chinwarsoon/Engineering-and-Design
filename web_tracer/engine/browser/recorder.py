"""engine/browser/recorder.py — record, persist and package browser sessions (T22/T27, §8.6).

``record`` drives a tracer through a ``RecordConfig`` and writes ``browser_trace.json`` into
``output/runs/<run_id>/`` (single source: ``engine.paths.run_dir``). ``package`` zips a run so
it can be imported on another machine (M5: offline replay); ``import_zip`` / ``import_payload``
unpack it into a fresh ``run_id`` and return the span count.
"""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any

from engine import paths
from engine.browser.base import BrowserTracer, RecordConfig, new_run_id


class Recorder:
    def __init__(self, tracer: BrowserTracer | None, runs_root: Path | None = None):
        self.tracer = tracer
        self.runs_root = Path(runs_root) if runs_root else paths.runs_root()

    def record(self, cfg: RecordConfig) -> "RunResult":
        if self.tracer is None:
            raise ValueError("Recorder needs a tracer to record")
        run_id = self.tracer.start(cfg)
        spans = self.tracer.stop()
        path = self.persist(run_id, spans, cfg)
        return RunResult(run_id=run_id, span_count=len(spans), path=path)

    def persist(self, run_id: str, spans: list[dict], cfg: RecordConfig | None = None) -> Path:
        d = paths.run_dir(run_id)
        (d / "browser_trace.json").write_text(json.dumps(spans, indent=2), encoding="utf-8")
        if cfg is not None:
            (d / "config.json").write_text(json.dumps(_cfg_dump(cfg), indent=2), encoding="utf-8")
        return d / "browser_trace.json"

    def package(self, run_id: str) -> Path:
        d = paths.run_dir(run_id)
        zip_path = self.runs_root / f"{run_id}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(d.iterdir()):
                if f.is_file():
                    z.write(f, arcname=f.name)
        return zip_path

    def import_zip(self, zip_path: str | Path, run_id: str | None = None) -> str:
        run_id = run_id or new_run_id()
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(paths.run_dir(run_id))
        return run_id

    def import_payload(self, filename: str, data: bytes) -> tuple[str, int]:
        run_id = new_run_id()
        if filename.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(paths.run_dir(run_id))
        else:
            spans = json.loads(data)
            self.persist(run_id, spans)
        p = paths.run_dir(run_id) / "browser_trace.json"
        spans = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
        return run_id, len(spans)


class RunResult:
    def __init__(self, run_id: str, span_count: int, path: Path):
        self.run_id = run_id
        self.span_count = span_count
        self.path = path


def _cfg_dump(cfg: RecordConfig) -> dict:
    out: dict[str, Any] = {
        "url": cfg.url,
        "headless": cfg.headless,
        "inject_traceparent": cfg.inject_traceparent,
        "capture_initiator": cfg.capture_initiator,
        "capture_console": cfg.capture_console,
        "screenshot_on_error": cfg.screenshot_on_error,
        "timeout_ms": cfg.timeout_ms,
        "actions": [a.__dict__ for a in cfg.actions],
    }
    if cfg.out_dir is not None:
        out["out_dir"] = str(cfg.out_dir)
    return out
