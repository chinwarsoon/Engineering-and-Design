"""backend/routes/java.py — Phase 3 Java runtime endpoints (T29-T33 / WT-20..WT-25).

Endpoints (workplan §8.5 rows 11-17):
  POST /java/receiver/start            begin an OTLP receive session (run_id)
  POST /v1/traces                      OTLP/HTTP export target (protobuf|json) -> ingest
  POST /java/receiver/stop             flush spans to output/runs/<run_id>/java_trace.json
  GET  /java/receiver/status          running / port / span_count / last_batch_at
  GET  /java/trace/{run_id}            SpanEvent[] for a run
  POST /java/import                    java_trace.json or raw OTLP json -> run_id
  GET  /java/instrumentation/strategies   list the 4 strategies
  POST /java/instrumentation/config    selected strategy + snippets + agent args + CORS note
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel

from engine import config, paths
from engine.browser.base import new_run_id
from engine.java import otlp_decode, strategies
from engine.java.otlp_receiver import OtlpReceiver

router = APIRouter()

_RECEIVER: Optional[OtlpReceiver] = None
_SESSIONS: dict[str, dict] = {}  # run_id -> {"spans": [...], "kind": "java"}


def _persist(run_id: str, spans: list[dict]) -> Path:
    d = paths.run_dir(run_id)
    p = d / "java_trace.json"
    p.write_text(json.dumps(spans, indent=2), encoding="utf-8")
    return p


def _parse_java_payload(data: bytes) -> list[dict]:
    obj = json.loads(data)
    if isinstance(obj, dict) and "resourceSpans" in obj:
        return otlp_decode.decode(data, "application/json")
    if isinstance(obj, list):  # already SpanEvent[]
        return obj
    raise ValueError("unrecognised java trace payload")


# ── receiver lifecycle (P0 rows 11-14 + T29) ────────────────────────────────────
@router.post(config.JAVA_RECEIVER_START)
def receiver_start(req: dict = None):
    global _RECEIVER
    channel = (req or {}).get("channel", "auto")
    run_id = new_run_id()
    _RECEIVER = OtlpReceiver(port=config.SERVICE_PORT, channel=channel, run_id=run_id)
    _RECEIVER.start(run_id)
    return {"port": config.SERVICE_PORT, "run_id": run_id, "channel": _RECEIVER.effective_channel()}


@router.post(config.OTLP_TRACES)
async def otlp_traces(request: Request):
    global _RECEIVER
    if _RECEIVER is None or not _RECEIVER.status()["running"]:
        raise HTTPException(status_code=409, detail="receiver not started; POST /java/receiver/start first")
    body = await request.body()
    ct = request.headers.get("content-type", "application/json")
    try:
        n = _RECEIVER.ingest(body, ct)
    except otlp_decode.ProtobufUnavailable as e:
        raise HTTPException(status_code=415, detail=str(e))
    return {"accepted": n}


@router.post(config.JAVA_RECEIVER_STOP)
def receiver_stop(req: dict = None):
    global _RECEIVER
    if _RECEIVER is None:
        raise HTTPException(status_code=404, detail="no active receiver")
    spans = _RECEIVER.stop()
    run_id = _RECEIVER.status()["run_id"]
    _persist(run_id, spans)
    _SESSIONS[run_id] = {"spans": spans, "kind": "java"}
    _RECEIVER = None
    return {"span_count": len(spans), "run_id": run_id}


@router.get(config.JAVA_RECEIVER_STATUS)
def receiver_status():
    if _RECEIVER is None:
        return {"running": False, "port": config.SERVICE_PORT, "span_count": 0, "last_batch_at": None}
    return _RECEIVER.status()


@router.get(config.JAVA_TRACE + "/{run_id}")
def java_trace(run_id: str):
    sess = _SESSIONS.get(run_id)
    if sess is not None:
        return sess["spans"]
    p = paths.run_dir(run_id) / "java_trace.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="no java trace for run_id")
    return json.loads(p.read_text(encoding="utf-8"))


@router.post(config.JAVA_IMPORT)
async def java_import(file: UploadFile = File(...)):
    data = await file.read()
    try:
        spans = _parse_java_payload(data)
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"invalid java trace payload: {e}")
    run_id = new_run_id()
    _persist(run_id, spans)
    _SESSIONS[run_id] = {"spans": spans, "kind": "java"}
    return {"run_id": run_id, "span_count": len(spans)}


# ── instrumentation strategy config (T31) ───────────────────────────────────────
@router.get(config.JAVA_INSTR_STRATEGIES)
def instr_strategies():
    return strategies.describe_strategies()


class InstrConfigReq(BaseModel):
    preference: str = "auto"
    project_path: Optional[str] = None


@router.post(config.JAVA_INSTR_CONFIG)
def instr_config(req: InstrConfigReq):
    proj = Path(req.project_path) if req.project_path else None
    inst = strategies.select_strategy(req.preference, proj)
    cfg = inst.emit_config(proj)
    # Our own backend sets allow_headers="*", so the CORS downgrade never triggers for it.
    cors_ok = True
    return {
        "selected": cfg.name,
        "nested_ok": cfg.nested_ok,
        "agent_args": cfg.agent_args,
        "env": cfg.env,
        "snippets": cfg.snippets,
        "probe_hint": cfg.probe_hint,
        "cors": {"backend_allows_traceparent": cors_ok},
    }
