"""backend/routes/browser.py — Phase 2 browser capture endpoints (workplan §9 rows 6-10, T28).

Five endpoints, each path constant imported from ``engine.config`` (single source, §8.5 hard
contract rule). A session registry holds the live tracer between record/start and record/stop;
``set_tracer_factory`` lets tests inject ``MockBrowserAdapter`` so no real browser is needed.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from engine import config, paths
from engine.browser.base import Action, RecordConfig
from engine.browser.recorder import Recorder
from engine.browser.traceparent import CorsProbe, probe_cors

router = APIRouter()

_SESSIONS: dict[str, dict] = {}
_FACTORY = None


def set_tracer_factory(fn) -> None:
    """Override the tracer factory (used by tests to inject MockBrowserAdapter)."""
    global _FACTORY
    _FACTORY = fn


def _make_tracer():
    if _FACTORY is not None:
        return _FACTORY()
    from engine.browser.playwright_adapter import PlaywrightAdapter

    return PlaywrightAdapter()


class ActionReq(BaseModel):
    kind: str
    selector: Optional[str] = None
    value: Optional[str] = None
    url: Optional[str] = None
    timeout_ms: int = 30_000


class RecordConfigReq(BaseModel):
    url: str
    headless: bool = True
    inject_traceparent: bool = True
    capture_initiator: bool = True
    capture_console: bool = True
    screenshot_on_error: bool = True
    actions: list[ActionReq] = []
    timeout_ms: int = 30_000
    out_dir: Optional[str] = None

    def to_dataclass(self) -> RecordConfig:
        return RecordConfig(
            url=self.url,
            headless=self.headless,
            inject_traceparent=self.inject_traceparent,
            capture_initiator=self.capture_initiator,
            capture_console=self.capture_console,
            screenshot_on_error=self.screenshot_on_error,
            actions=[
                Action(kind=a.kind, selector=a.selector, value=a.value, url=a.url, timeout_ms=a.timeout_ms)
                for a in self.actions
            ],
            timeout_ms=self.timeout_ms,
            out_dir=Path(self.out_dir) if self.out_dir else None,
        )


@router.post(config.BROWSER_RECORD_START)
def record_start(req: RecordConfigReq):
    cfg = req.to_dataclass()
    cors = probe_cors(cfg.url)
    tracer = _make_tracer()
    run_id = tracer.start(cfg)
    _SESSIONS[run_id] = {"tracer": tracer, "cfg": cfg, "cors": cors, "spans": None}
    return {"run_id": run_id, "cors_probe": {"observed": cors.observed, "allowed": cors.allowed}}


@router.post(config.BROWSER_RECORD_STOP)
def record_stop(payload: dict):
    run_id = payload.get("run_id")
    sess = _SESSIONS.get(run_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="unknown run_id")
    spans = sess["tracer"].stop()
    rec = Recorder(sess["tracer"], paths.runs_root())
    path = rec.persist(run_id, spans, sess["cfg"])
    sess["spans"] = spans
    return {"span_count": len(spans), "path": str(path)}


@router.get(config.BROWSER_RECORD_STATUS)
def record_status(run_id: Optional[str] = None):
    if run_id:
        sess = _SESSIONS.get(run_id)
        if sess is None:
            raise HTTPException(status_code=404, detail="unknown run_id")
        recording = sess.get("spans") is None
        spans = sess.get("spans") or []
        cors: CorsProbe = sess["cors"]
        return {
            "recording": recording,
            "span_count": len(spans),
            "cors": {"observed": cors.observed, "allowed": cors.allowed},
        }
    return {
        "recording": any(s.get("spans") is None for s in _SESSIONS.values()),
        "active_sessions": len(_SESSIONS),
    }


@router.get(config.BROWSER_TRACE + "/{run_id}")
def trace(run_id: str):
    sess = _SESSIONS.get(run_id)
    if sess is not None and sess.get("spans") is not None:
        return sess["spans"]
    p = paths.run_dir(run_id) / "browser_trace.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="no trace for run_id")
    return json.loads(p.read_text(encoding="utf-8"))


@router.post(config.BROWSER_IMPORT)
async def import_trace(file: UploadFile = File(...)):
    data = await file.read()
    rec = Recorder(None, paths.runs_root())
    run_id, span_count = rec.import_payload(file.filename or "import.json", data)
    return {"run_id": run_id, "span_count": span_count}
