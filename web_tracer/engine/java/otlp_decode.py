"""engine/java/otlp_decode.py — decode OTLP/HTTP Exports into SpanEvents (T29, §8.4).

The OTel Java agent ships spans over OTLP/HTTP, either as **protobuf** (binary) or **JSON**.
This module accepts both and normalises them into our frozen ``SpanEvent`` schema:

  * ``application/x-protobuf`` -> :class:`ProtobufUnavailable` is raised when the protobuf
    runtime / OTLP proto stubs are absent. The receiver turns that into an explicit WARN +
    downgrade to ``http/json`` (never a silent failure, workplan §8.4 rule 4 / AGENTS.md §5.9).
  * ``application/json`` (or any other content type) -> decoded directly.

Every produced span is validated against ``engine/schema/span_schema.json`` so malformed
spans fail fast instead of corrupting the trace.
"""
from __future__ import annotations

import base64
import json
from typing import Any

from engine import config, ids
from engine.browser.base import make_span  # shared SpanEvent builder
from engine.schema.validate import validate_span

PROTOBUF_CONTENT_TYPE = "application/x-protobuf"

# OTel span kind enum (https://opentelemetry.io/docs/specs/otel/trace/api/#spankind).
_SPAN_KIND = {0: "unspecified", 1: "internal", 2: "server", 3: "client", 4: "producer", 5: "consumer"}

_HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}


class ProtobufUnavailable(RuntimeError):
    """Raised when an OTLP protobuf payload arrives but protobuf / OTLP proto stubs are missing."""


# ── attribute value coercion ────────────────────────────────────────────────────
def _attr_value_to_py(v: dict) -> Any:
    if not isinstance(v, dict):
        return v
    if "stringValue" in v:
        return v["stringValue"]
    if "intValue" in v:
        return int(v["intValue"])
    if "doubleValue" in v:
        return float(v["doubleValue"])
    if "boolValue" in v:
        return bool(v["boolValue"])
    if "arrayValue" in v:
        return [_attr_value_to_py(x) for x in v["arrayValue"].get("values", [])]
    if "kvlistValue" in v:
        return _attrs_to_dict(v["kvlistValue"].get("values", []))
    if "bytesValue" in v:
        bv = v["bytesValue"]
        return base64.b64encode(bv).decode() if isinstance(bv, (bytes, bytearray)) else bv
    return None


def _attrs_to_dict(attrs: list[dict]) -> dict:
    out: dict[str, Any] = {}
    for a in attrs or []:
        out[a["key"]] = _attr_value_to_py(a.get("value", {}))
    return out


def _hex(b: Any) -> str | None:
    if b is None:
        return None
    if isinstance(b, str):
        return b  # OTLP JSON form is already a hex string
    return b.hex()  # OTLP protobuf form is bytes


# ── JSON decode ──────────────────────────────────────────────────────────────────
def _decode_json(body: bytes) -> list[dict]:
    """Parse an OTLP/HTTP JSON ExportTraceServiceRequest into a normalised raw-span list."""
    data = json.loads(body)
    raw: list[dict] = []
    for rs in data.get("resourceSpans", []):
        resource_attrs = _attrs_to_dict(rs.get("resource", {}).get("attributes", []))
        service_name = resource_attrs.get("service.name", "unknown")
        for ss in rs.get("scopeSpans", []):
            scope = ss.get("scope", {}) or {}
            for sp in ss.get("spans", []):
                raw.append(
                    {
                        "trace_id": _hex(sp.get("traceId")),
                        "span_id": _hex(sp.get("spanId")),
                        "parent_span_id": _hex(sp.get("parentSpanId")),
                        "name": sp.get("name", ""),
                        "kind": int(sp.get("kind", 1)),
                        "start_time_unix_ns": int(sp.get("startTimeUnixNano", 0)),
                        "end_time_unix_ns": int(sp.get("endTimeUnixNano", 0)),
                        "attributes": _attrs_to_dict(sp.get("attributes", [])),
                        "status": sp.get("status", {}) or {},
                        "scope": scope,
                        "service_name": service_name,
                    }
                )
    return raw


# ── protobuf decode (guarded) ─────────────────────────────────────────────────────
def _proto_attr(av: Any) -> Any:
    which = av.WhichOneof("value")
    if which == "string_value":
        return av.string_value
    if which == "int_value":
        return av.int_value
    if which == "double_value":
        return av.double_value
    if which == "bool_value":
        return av.bool_value
    if which == "array_value":
        return [_proto_attr(x) for x in av.array_value.values]
    if which == "kvlist_value":
        return {kv.key: _proto_attr(kv.value) for kv in av.kvlist_value.values}
    return None


def _decode_protobuf(body: bytes) -> list[dict]:
    """Decode OTLP protobuf. Raises :class:`ProtobufUnavailable` if deps are missing."""
    try:
        from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (  # type: ignore
            ExportTraceServiceRequest,
        )
        from google.protobuf.json_format import Parse  # type: ignore
    except Exception as e:  # ImportError or any missing-dependency error
        raise ProtobufUnavailable(
            "OTLP protobuf payload received but the protobuf runtime / OTLP proto stubs are "
            "missing. Install 'protobuf' (and the opentelemetry proto stubs) or set the agent "
            f"to -Dotel.exporter.otlp.protocol=http/json. ({e})"
        ) from e
    msg = ExportTraceServiceRequest()
    Parse(body, msg, ignore_unknown_fields=True)
    raw: list[dict] = []
    for rs in msg.resource_spans:
        resource_attrs = {kv.key: _proto_attr(kv.value) for kv in rs.resource.attributes}
        service_name = resource_attrs.get("service.name", "unknown")
        for ss in rs.scope_spans:
            scope = {"name": ss.scope.name, "version": ss.scope.version}
            for sp in ss.spans:
                raw.append(
                    {
                        "trace_id": sp.trace_id.hex(),
                        "span_id": sp.span_id.hex(),
                        "parent_span_id": sp.parent_span_id.hex() if sp.parent_span_id else None,
                        "name": sp.name,
                        "kind": int(sp.kind),
                        "start_time_unix_ns": int(sp.start_time_unix_nano),
                        "end_time_unix_ns": int(sp.end_time_unix_nano),
                        "attributes": {kv.key: _proto_attr(kv.value) for kv in sp.attributes},
                        "status": {"code": int(sp.status.code), "message": sp.status.message},
                        "scope": scope,
                        "service_name": service_name,
                    }
                )
    return raw


# ── classification (OTel span -> our layer/event_type/kind) ──────────────────────
def _classify(name: str, attrs: dict, kind_num: int) -> tuple[str, str, str]:
    # kind MUST be one of: function | method | request | statement | event
    if "db.statement" in attrs or "db.system" in attrs:
        return "db", "sql", "statement"
    if "http.url" in attrs or "http.method" in attrs or "http.target" in attrs:
        if kind_num == 3:  # CLIENT
            if "http.response.status_code" in attrs or "http.status_code" in attrs:
                return "http", "http_response", "request"
            return "http", "http_request", "request"
        return "java", "controller", "request"  # SERVER handler with an http route
    if kind_num == 2:  # SERVER
        return "java", "controller", "request"
    # internal / method-level: infer the event_type from the class name suffix (kind=method)
    cls = attrs.get("code.namespace") or attrs.get("class.name") or ""
    suffix = cls.split(".")[-1] if cls else name
    if suffix.endswith("Controller"):
        return "java", "controller", "method"
    if suffix.endswith("Service"):
        return "java", "service", "method"
    if suffix.endswith("Repository") or suffix.endswith("Dao") or suffix.endswith("Repo"):
        return "java", "repository", "method"
    return "java", "method", "method"


def _build_source(attrs: dict, name: str) -> dict:
    src: dict[str, Any] = {"file": "<unknown>"}
    ns = attrs.get("code.namespace")
    fn = attrs.get("code.function")
    fp = attrs.get("code.filepath")
    ln = attrs.get("code.lineno")
    if ns:
        src["class_name"] = ns
    if fn:
        src["symbol"] = fn
    if fp:
        src["file"] = fp
    if ln is not None:
        src["line"] = int(ln)
    # fallbacks the Spring AOP aspect adds
    if "class_name" not in src and attrs.get("class.name"):
        src["class_name"] = attrs["class.name"]
    if "symbol" not in src and attrs.get("method.name"):
        src["symbol"] = attrs["method.name"]
    return src


def _map_otel_span(raw: dict, run_id: str) -> dict:
    trace_id = raw["trace_id"] or ids.new_trace_id()
    span_id = raw["span_id"] or ids.new_span_id()
    attrs = raw.get("attributes", {}) or {}
    name = raw["name"] or "<span>"
    kind_num = int(raw.get("kind", 1))
    start = int(raw.get("start_time_unix_ns") or 0)
    end = int(raw.get("end_time_unix_ns") or start)
    duration_ms = max(0.0, (end - start) / 1_000_000.0)
    layer, event_type, kind = _classify(name, attrs, kind_num)
    status_obj = raw.get("status", {}) or {}
    span_status = "error" if int(status_obj.get("code", 0)) == 2 else "ok"
    source = _build_source(attrs, name)
    resource = {"service_name": raw.get("service_name") or "unknown"}
    # method-level spans with a resolved source are trusted (1.0); others still carry trace_id.
    conf = 1.0 if (source.get("class_name") or source.get("file") not in (None, "<unknown>")) else 0.9
    span = make_span(
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=raw.get("parent_span_id"),
        layer=layer,
        event_type=event_type,
        name=name,
        kind=kind,
        source=source,
        start_time_unix_ns=start,
        duration_ms=duration_ms,
        status=span_status,
        confidence=conf,
        correlation_method="trace_id",
        correlation_score=1.0,
        attributes=attrs,
        clock_offset_ms=0.0,
        run_id=run_id,
        collector_name="otlp-receiver",
        collector_version="0.1.0",
        resource=resource,
    )
    validate_span(span)  # fail fast on malformed spans
    return span


# ── public entry point ───────────────────────────────────────────────────────────
def decode(body: bytes, content_type: str, run_id: str | None = None) -> list[dict]:
    """Decode an OTLP payload (protobuf or JSON) into validated SpanEvent dicts."""
    ct = (content_type or "").lower()
    raw = _decode_protobuf(body) if "protobuf" in ct else _decode_json(body)
    rid = run_id or ids.new_trace_id()[:16]
    return [_map_otel_span(r, rid) for r in raw]
