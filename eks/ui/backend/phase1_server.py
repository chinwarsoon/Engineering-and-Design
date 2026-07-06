"""Phase 1 Backend Server — Dashboard API (port 5001).

Per Appendix G §10, this server provides all Phase 1 API endpoints:
file discovery, document CRUD, pipeline execution, and health scoring.

All endpoints are versioned under /api/v1/.

Standalone usage:
    python eks/ui/backend/phase1_server.py --port 5001

Read-only endpoints on the DuckDB registry:
  - GET  /api/v1/config/paths
  - GET  /api/v1/files/list-dirs
  - GET  /api/v1/documents
  - GET  /api/v1/documents/{id}
  - GET  /api/v1/pipeline/status/{job_id}
  - GET  /api/v1/pipeline/logs/{job_id}
  - GET  /api/v1/review/summary
  - GET  /api/v1/review/flagged

Read-write endpoints on the DuckDB registry:
  - POST /api/v1/files/load
  - POST /api/v1/pipeline/start
  - PUT  /api/v1/documents/{id}
  - PUT  /api/v1/review/lock
  - PUT  /api/v1/review/recalculate
  - DELETE /api/v1/pipeline/{job_id}
"""

import json
import os
import re
import socket
import sys
import threading
import time
import uuid
from argparse import ArgumentParser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, unquote, parse_qs

# Ensure package resolution
SRV_DIR = Path(__file__).resolve().parent                      # eks/ui/backend/
PRJ_DIR = SRV_DIR.parent.parent.parent                         # repo root
if str(PRJ_DIR) not in sys.path:
    sys.path.insert(0, str(PRJ_DIR))

# ---------------------------------------------------------------------------
# Dependency guard — catch missing conda env early
# ---------------------------------------------------------------------------
_IMPORTS_OK = True
_IMPORT_ERROR: Optional[str] = None

try:
    from eks.engine.core import DocumentRegistry
    from eks.engine.core.schema_loader import SchemaLoader
    from eks.engine.core.file_scanner import FileScanner
    from eks.engine.core.pipeline_orchestrator import PipelineOrchestrator
    from eks.engine.core.review_manager import ManualReviewManager
    from eks.engine.logging.logger import EKSLogger
except ImportError as e:
    _IMPORTS_OK = False
    _IMPORT_ERROR = str(e)


def find_free_port(start: int = 5001, max_attempts: int = 100) -> int:
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError(f"No free port in range {start}-{start + max_attempts}")


# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------
_registry: Optional["DocumentRegistry"] = None
_registry_lock = threading.Lock()

_job_state: Dict[str, Dict[str, Any]] = {}
_job_logs: Dict[str, List[Dict[str, Any]]] = {}
_job_lock = threading.RLock()

_logger = EKSLogger("Phase1Server", level=1) if _IMPORTS_OK else None


def _with_retry(fn, retries=3, delay=0.5):
    """Execute *fn* with retries on IOError (DuckDB locking contention)."""
    for attempt in range(retries):
        try:
            return fn()
        except (IOError, OSError) as e:
            if attempt < retries - 1:
                if _logger:
                    _logger.warning(f"DB lock contention (attempt {attempt+1}/{retries}): {e}")
                time.sleep(delay)
            else:
                raise


def get_registry():
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = DocumentRegistry(logger=_logger)
    return _registry


class ReusableTCPServer(HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        exc = sys.exc_info()[1]
        if isinstance(exc, ConnectionResetError):
            return
        super().handle_error(request, client_address)


# ---------------------------------------------------------------------------
# Request Handler
# ---------------------------------------------------------------------------

class Phase1Handler(SimpleHTTPRequestHandler):

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def handle_error(self, request, client_address):
        exc = sys.exc_info()[1]
        if isinstance(exc, ConnectionResetError):
            return
        super().handle_error(request, client_address)

    def log_message(self, format, *args) -> None:
        if args[0] in ("200", "304"):
            return
        print(f"[Phase1Server] {args[0]} {args[1]} {args[2]}")

    def _json_response(self, code: int, data: Any):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(code)
        self._set_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length > 0 else b""

    def _parse_path(self) -> Tuple[List[str], Dict[str, str]]:
        """Return (path_segments, query_params) with URL decode."""
        parsed = urlparse(unquote(self.path))
        segments = [s for s in parsed.path.split("/") if s]
        qs = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
        return segments, qs

    # ------------------------------------------------------------------
    # Imports-available check
    # ------------------------------------------------------------------
    def _check_imports(self) -> bool:
        """Return False if engine imports failed. Sends 503 if unavailable."""
        if not _IMPORTS_OK:
            self._json_response(503, {
                "error": "Phase 1 engine unavailable",
                "detail": _IMPORT_ERROR,
                "install": "conda activate eks",
            })
            return False
        return True

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------
    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        try:
            segments, qs = self._parse_path()
            if segments == ["api", "v1", "status"]:
                self._handle_status()
            elif segments == ["api", "v1", "config", "paths"]:
                self._handle_config_paths()
            elif segments == ["api", "v1", "files", "list-dirs"]:
                self._handle_list_dirs(qs)
            elif segments[:3] == ["api", "v1", "documents"] and len(segments) == 4:
                self._handle_get_document(segments[3])
            elif segments == ["api", "v1", "documents"]:
                self._handle_list_documents(qs)
            elif segments[:4] == ["api", "v1", "pipeline", "status"] and len(segments) == 5:
                self._handle_pipeline_status(segments[4])
            elif segments[:4] == ["api", "v1", "pipeline", "logs"] and len(segments) == 5:
                self._handle_pipeline_logs(segments[4])
            elif segments == ["api", "v1", "review", "summary"]:
                self._handle_review_summary()
            elif segments[:4] == ["api", "v1", "review", "flagged"]:
                self._handle_flagged_documents()
            else:
                self._json_response(404, {"error": "Not found"})
        except Exception as e:
            if _logger:
                _logger.error(f"GET {self.path}: {e}", context="Phase1Handler.do_GET")
            self._json_response(500, {"error": str(e)})

    def do_POST(self):
        try:
            segments, qs = self._parse_path()
            body = self._read_body()
            data = json.loads(body) if body else {}

            if segments == ["api", "v1", "files", "load"]:
                self._handle_files_load(data)
            elif segments == ["api", "v1", "pipeline", "start"]:
                self._handle_pipeline_start(data)
            else:
                self._json_response(404, {"error": "Not found"})
        except json.JSONDecodeError:
            self._json_response(400, {"error": "Invalid JSON"})
        except Exception as e:
            if _logger:
                _logger.error(f"POST {self.path}: {e}", context="Phase1Handler.do_POST")
            self._json_response(500, {"error": str(e)})

    def do_PUT(self):
        try:
            segments, qs = self._parse_path()
            body = self._read_body()
            data = json.loads(body) if body else {}

            if segments[:3] == ["api", "v1", "documents"] and len(segments) == 4:
                self._handle_update_document(segments[3], data)
            elif segments[:3] == ["api", "v1", "review"] and len(segments) == 4:
                self._handle_review_action(segments[3], data)
            else:
                self._json_response(404, {"error": "Not found"})
        except json.JSONDecodeError:
            self._json_response(400, {"error": "Invalid JSON"})
        except Exception as e:
            if _logger:
                _logger.error(f"PUT {self.path}: {e}", context="Phase1Handler.do_PUT")
            self._json_response(500, {"error": str(e)})

    def do_DELETE(self):
        try:
            segments, qs = self._parse_path()
            if segments[:3] == ["api", "v1", "pipeline"] and len(segments) == 4:
                self._handle_pipeline_cancel(segments[3])
            else:
                self._json_response(404, {"error": "Not found"})
        except Exception as e:
            if _logger:
                _logger.error(f"DELETE {self.path}: {e}", context="Phase1Handler.do_DELETE")
            self._json_response(500, {"error": str(e)})

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_status(self):
        self._json_response(200, {
            "status": "healthy",
            "version": "0.1.0",
            "phase": 1,
            "timestamp": datetime.utcnow().isoformat(),
            "imports_ok": _IMPORTS_OK,
        })

    def _handle_config_paths(self):
        """Return global_paths from config (SSOT) plus effective defaults."""
        default_data_dir = "eks/data"
        result = {
            "data_dir": default_data_dir,
            "global_paths": {
                "data_dir": "data",
                "output_dir": "output",
                "archive_dir": "archive",
                "config_dir": "config",
            }
        }
        if self._check_imports():
            try:
                loader = SchemaLoader("eks/config")
                config = loader.load_all()
                gp = config.get("global_paths", {})
                result["global_paths"] = {
                    "data_dir": gp.get("data_dir", "data"),
                    "output_dir": gp.get("output_dir", "output"),
                    "archive_dir": gp.get("archive_dir", "archive"),
                    "config_dir": gp.get("config_dir", "config"),
                }
                result["data_dir"] = str(PRJ_DIR / "eks" / gp.get("data_dir", "data"))
            except Exception:
                pass
        self._json_response(200, result)

    def _handle_list_dirs(self, qs: Dict[str, str]):
        """List subdirectories of a parent path, with traversal guard."""
        parent = qs.get("parent", ".")
        target = (PRJ_DIR / parent).resolve()
        if not target.is_relative_to(PRJ_DIR.resolve()):
            self._json_response(403, {"error": "Path traversal not allowed"})
            return
        if not target.is_dir():
            self._json_response(404, {"error": f"Directory not found: {parent}"})
            return
        dirs = sorted(
            [str(p.relative_to(PRJ_DIR)) for p in target.iterdir() if p.is_dir()],
            key=lambda x: x.lower(),
        )
        self._json_response(200, {
            "dirs": dirs,
            "parent": str(target.relative_to(PRJ_DIR)),
        })

    def _handle_files_load(self, data: Dict[str, Any]):
        if not self._check_imports():
            return

        data_dir = data.get("data_dir", "eks/data")
        recursive = data.get("recursive", True)

        loader = SchemaLoader("eks/config")
        config = loader.load_all()
        doc_config = loader.doc_config

        scanner = FileScanner(config, doc_config=doc_config, logger=_logger)
        discovered = scanner.scan(Path(data_dir), recursive=recursive)
        valid, unknown = scanner.validate_file_types(discovered)
        registered = 0
        registry = get_registry()

        def _register(file_info):
            nonlocal registered
            metadata = scanner.build_placeholder_metadata(file_info)
            doc_number = metadata.get("document_number")
            if not doc_number:
                if _logger:
                    _logger.warning(f"Skipping file without document_number: {file_info['file_name']}")
                return
            metadata.setdefault("revision", "00")
            existing = _with_retry(lambda: registry.get_document(doc_number, revision=metadata["revision"]))
            if existing:
                return
            metadata["document_type"] = scanner._infer_doc_type(file_info["file_type"])
            _with_retry(lambda: registry.register_document(metadata))
            registered += 1

        for file_info in valid:
            try:
                _register(file_info)
            except Exception as e:
                if _logger:
                    _logger.warning(f"Failed to register {file_info.get('file_name')}: {e}")

        self._json_response(200, {
            "discovered": len(discovered),
            "valid": len(valid),
            "unknown": len(unknown),
            "registered": registered,
            "files": discovered,
        })

    def _handle_list_documents(self, qs: Dict[str, str]):
        filters = {}
        for key in ("document_type", "discipline", "project_number", "status", "extract_status"):
            if key in qs:
                filters[key] = qs[key]
        latest_only = qs.get("latest_only", "true").lower() == "true"
        order_by = qs.get("order_by", "document_number")

        def _action():
            return get_registry().list_documents(filters=filters, latest_only=latest_only, order_by=order_by)
        docs = _with_retry(_action)
        self._json_response(200, {"count": len(docs), "documents": docs})

    def _handle_get_document(self, doc_id: str):
        parts = doc_id.rsplit("-", 1)
        doc_number = parts[0]
        revision = parts[1] if len(parts) > 1 else None

        def _action():
            return get_registry().get_document(doc_number, revision=revision)
        doc = _with_retry(_action)
        if doc:
            self._json_response(200, doc)
        else:
            self._json_response(404, {"error": f"Document not found: {doc_id}"})

    def _handle_update_document(self, doc_id: str, data: Dict[str, Any]):
        def _action():
            manager = ManualReviewManager(get_registry(), logger=_logger)
            return manager.correct_metadata(doc_id, data)
        ok = _with_retry(_action)
        if ok:
            self._json_response(200, {"status": "updated", "id": doc_id})
        else:
            self._json_response(400, {"error": f"Update failed for {doc_id}"})

    def _handle_pipeline_start(self, data: Dict[str, Any]):
        if not self._check_imports():
            return

        # Concurrency guard — reject if a pipeline is already running (G10.5 #9)
        with _job_lock:
            for existing_job in _job_state.values():
                if existing_job.get("status") == "running":
                    self._json_response(409, {
                        "error": f"A pipeline job is already running (job_id: {existing_job['job_id']}). Cancel it or wait for completion.",
                    })
                    return

        job_id = str(uuid.uuid4())
        data_dir = data.get("data_dir", "eks/data")
        recursive = data.get("recursive", True)

        with _job_lock:
            _job_state[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "progress": 0,
                "data_dir": data_dir,
                "created_at": datetime.utcnow().isoformat(),
                "summary": None,
                "error": None,
            }
            _job_logs[job_id] = []

        def _capture_log(entry: Dict[str, Any]):
            with _job_lock:
                if job_id in _job_logs:
                    _job_logs[job_id].append(entry)

        class _LogCapture:
            def status(self, msg, context=""):
                _capture_log({"level": "STATUS", "message": msg, "context": context})
                if _logger:
                    _logger.status(msg, context=context)
            def info(self, msg, context=""):
                _capture_log({"level": "INFO", "message": msg, "context": context})
                if _logger:
                    _logger.info(msg, context=context)
            def warning(self, msg, context=""):
                _capture_log({"level": "WARNING", "message": msg, "context": context})
                if _logger:
                    _logger.warning(msg, context=context)
            def error(self, msg, context=""):
                _capture_log({"level": "ERROR", "message": msg, "context": context})
                if _logger:
                    _logger.error(msg, context=context)

        def _run():
            try:
                with _job_lock:
                    if _job_state[job_id]["status"] != "queued":
                        return  # was cancelled before we started
                    _job_state[job_id]["status"] = "running"
                loader = SchemaLoader("eks/config")
                config = loader.load_all()
                doc_config = loader.doc_config
                registry = get_registry()
                job_logger = _LogCapture()
                orchestrator = PipelineOrchestrator(
                    config, doc_config, registry, logger=job_logger, use_telemetry=False
                )
                orchestrator.initialize_context(
                    data_dir=Path(data_dir),
                    schema_dir=Path("eks/config/schemas"),
                    output_dir=Path("eks/output"),
                    archive_dir=Path("eks/archive"),
                    config_dir=Path("eks/config"),
                    log_dir=Path("eks/log"),
                )
                summary = orchestrator.run_full_pipeline(Path(data_dir), recursive=recursive)
                with _job_lock:
                    _job_state[job_id]["status"] = "completed"
                    _job_state[job_id]["progress"] = 100
                    _job_state[job_id]["summary"] = summary
            except Exception as e:
                _capture_log({"level": "ERROR", "message": f"Pipeline failed: {e}", "context": "_run_pipeline"})
                if _logger:
                    _logger.error(f"Pipeline {job_id} failed: {e}", context="_run_pipeline")
                with _job_lock:
                    _job_state[job_id]["status"] = "failed"
                    _job_state[job_id]["error"] = str(e)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        self._json_response(202, {"job_id": job_id, "status": "queued"})

    def _handle_pipeline_status(self, job_id: str):
        with _job_lock:
            job = _job_state.get(job_id)
        if job is None:
            self._json_response(404, {"error": f"Job not found: {job_id}"})
        else:
            self._json_response(200, job)

    def _handle_pipeline_logs(self, job_id: str):
        with _job_lock:
            logs = _job_logs.get(job_id, [])
        self._json_response(200, {"job_id": job_id, "logs": logs})

    def _handle_pipeline_cancel(self, job_id: str):
        with _job_lock:
            job = _job_state.get(job_id)
            if job and job["status"] in ("queued", "running"):
                job["status"] = "cancelled"
                self._json_response(200, {"status": "cancelled", "job_id": job_id})
            elif job:
                self._json_response(400, {"error": f"Job is {job['status']}, cannot cancel"})
            else:
                self._json_response(404, {"error": f"Job not found: {job_id}"})

    def _handle_review_summary(self):
        def _action():
            manager = ManualReviewManager(get_registry(), logger=_logger)
            return manager.get_review_summary()
        summary = _with_retry(_action)
        self._json_response(200, summary)

    def _handle_flagged_documents(self):
        def _action():
            manager = ManualReviewManager(get_registry(), logger=_logger)
            return manager.get_flagged_documents()
        flagged = _with_retry(_action)
        self._json_response(200, {"count": len(flagged), "documents": flagged})

    def _handle_review_action(self, action: str, data: Dict[str, Any]):
        doc_id = data.get("doc_id", "")
        if action == "lock":
            def _action():
                manager = ManualReviewManager(get_registry(), logger=_logger)
                return manager.lock_document(doc_id, data.get("verified_by", "reviewer"))
            ok = _with_retry(_action)
            if ok:
                self._json_response(200, {"status": "locked", "id": doc_id})
            else:
                self._json_response(400, {"error": f"Lock failed for {doc_id}"})
        elif action == "recalculate":
            def _action():
                manager = ManualReviewManager(get_registry(), logger=_logger)
                return manager.recalculate_score(doc_id)
            score = _with_retry(_action)
            self._json_response(200, {"status": "recalculated", "id": doc_id, "score": score})
        else:
            self._json_response(404, {"error": f"Unknown action: {action}"})


def main():
    parser = ArgumentParser(description="EKS Phase 1 Backend Server")
    parser.add_argument("--port", type=int, default=None, help="Port (default: auto)")
    args = parser.parse_args()

    port = args.port or find_free_port(5001)

    if _IMPORTS_OK:
        print(f"[Phase1Server] Engine imports OK")
    else:
        print(f"[Phase1Server] ⚠ Engine imports failed: {_IMPORT_ERROR}. Run: conda activate eks")

    server = ReusableTCPServer(("0.0.0.0", port), Phase1Handler)
    print(f"[Phase1Server] Phase 1 Backend -> http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Phase1Server] Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
