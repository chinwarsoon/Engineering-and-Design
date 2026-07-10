"""Phase 1 Backend Server — Dashboard API (port 5001).

Per Appendix G §10, this server provides all Phase 1 API endpoints:
file discovery, document CRUD, pipeline execution, and health scoring.

Revision: 0.8 (T1.83)
- 0.1: Initial server with all Phase 1 API endpoints
- 0.2: T1.69–T1.76: run_id, traversal guard, checkpoint persist, ErrorManager/MessageManager activation, artifact dump
- 0.3: T1.77: ProjectSetupValidator readiness gate, --debug/--level CLI, data_dir/recursive validation
- 0.4: T1.78: data_dir readability check (G2), output-path validation (G4), --skip-readiness flag (G5), _LogCapture.level fix
- 0.5: T1.79: Move ErrorManager construction before readiness gate; replace generic RuntimeError with em.handle_system_error("P1-SETUP-READINESS")
- 0.6: T1.80: Derive output path from config.global_paths.output_dir in _handle_pipeline_start + _run closure; replace hardcoded PRJ_DIR/"eks"/"output"
- 0.7: T1.82: Derive data_dir default from config.global_paths.data_dir instead of hardcoded "eks/data"; honor validation_options.auto_create_folders in readiness gate; remove hardcoded fallback dict in _handle_config_paths
- 0.8: T1.83: Replace 10× PRJ_DIR/"eks" literals with _EKS_ROOT_DEFAULT / config.global_paths.eks_root (schema-driven package root); added eks_root to global_paths_def schema

All endpoints are versioned under /api/v1/.

Standalone usage:
    python eks/ui/backend/phase1_server.py --port 5001
    python eks/ui/backend/phase1_server.py --port 5001 --debug
    python eks/ui/backend/phase1_server.py --port 5001 --level 3

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
    from eks.engine.core.error_manager import ErrorManager
    from eks.engine.core.message_manager import MessageManager
    from eks.engine.core.setup_validator import ProjectSetupValidator
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
_debug_mode = False
_log_level = 1
_skip_readiness = False

# T1.83: EKS package root — schema-driven via global_paths.eks_root
_EKS_ROOT_DEFAULT = "eks"


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

    def _check_traversal(self, resolved_path: Path) -> bool:
        """Return True if path is inside PRJ_DIR. Sends 403 if not."""
        if not resolved_path.is_relative_to(PRJ_DIR.resolve()):
            self._json_response(403, {"error": "Path traversal not allowed"})
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
            "debug_mode": _debug_mode,
            "log_level": _log_level,
        })

    def _handle_config_paths(self):
        """Return global_paths from config (SSOT) — no hardcoded fallbacks (T1.82)."""
        result = {"data_dir": None, "global_paths": None}
        if self._check_imports():
            try:
                loader = SchemaLoader(PRJ_DIR / _EKS_ROOT_DEFAULT / "config")
                config = loader.load_all()
                gp = config.get("global_paths", {})
                result["global_paths"] = {
                    "data_dir": gp.get("data_dir", "data"),
                    "output_dir": gp.get("output_dir", "output"),
                    "archive_dir": gp.get("archive_dir", "archive"),
                    "config_dir": gp.get("config_dir", "config"),
                }
                _cfg_eks_root = gp.get("eks_root", _EKS_ROOT_DEFAULT)
                result["data_dir"] = (PRJ_DIR / _cfg_eks_root / gp.get("data_dir", "data")).as_posix()
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
            [p.relative_to(PRJ_DIR).as_posix() for p in target.iterdir() if p.is_dir()],
            key=lambda x: x.lower(),
        )
        self._json_response(200, {
            "dirs": dirs,
            "parent": target.relative_to(PRJ_DIR).as_posix(),
        })

    def _handle_files_load(self, data: Dict[str, Any]):
        if not self._check_imports():
            return

        # T1.82/T1.83: Derive data_dir default from config
        _fl_loader = SchemaLoader(PRJ_DIR / _EKS_ROOT_DEFAULT / "config")
        _fl_cfg = _fl_loader.load_all()
        _fl_gp = _fl_cfg.get("global_paths", {})
        _fl_eks_root = _fl_gp.get("eks_root", _EKS_ROOT_DEFAULT)
        _fl_data_rel = _fl_gp.get("data_dir", "data")
        _fl_default_data = f"{_fl_eks_root}/{_fl_data_rel}"

        raw_data_dir = data.get("data_dir", _fl_default_data)
        data_dir = (PRJ_DIR / raw_data_dir).resolve()
        if not self._check_traversal(data_dir):
            return
        recursive = data.get("recursive", True)

        loader = SchemaLoader(PRJ_DIR / _fl_eks_root / "config")
        config = loader.load_all()
        doc_config = loader.doc_config

        scanner = FileScanner(config, doc_config=doc_config, logger=_logger)
        discovered = scanner.scan(data_dir, recursive=recursive)
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

        # T1.82: Load config early for schema-driven defaults
        _cfg_loader = SchemaLoader(PRJ_DIR / _EKS_ROOT_DEFAULT / "config")
        _cfg = _cfg_loader.load_all()
        _gp = _cfg.get("global_paths", {})
        _ps = _cfg.get("project_setup", _cfg)
        _eks_root = _gp.get("eks_root", _EKS_ROOT_DEFAULT)
        _data_rel = _gp.get("data_dir", "data")
        _default_data_dir = f"{_eks_root}/{_data_rel}"

        # T1.77: Validate input parameters before any state mutation or concurrency check
        raw_data_dir = data.get("data_dir", _default_data_dir)
        resolved_data_dir = (PRJ_DIR / raw_data_dir).resolve()
        if not self._check_traversal(resolved_data_dir):
            return
        if not resolved_data_dir.exists():
            self._json_response(400, {
                "error": f"data_dir does not exist: {raw_data_dir}",
                "resolved": str(resolved_data_dir),
            })
            return
        if not resolved_data_dir.is_dir():
            self._json_response(400, {
                "error": f"data_dir is not a directory: {raw_data_dir}",
                "resolved": str(resolved_data_dir),
            })
            return
        # G2: Validate data_dir readability
        if not os.access(str(resolved_data_dir), os.R_OK):
            self._json_response(400, {
                "error": f"data_dir is not readable: {raw_data_dir}",
                "resolved": str(resolved_data_dir),
            })
            return
        recursive = data.get("recursive", True)
        if not isinstance(recursive, bool):
            self._json_response(400, {
                "error": f"recursive must be a boolean, got {type(recursive).__name__}",
            })
            return

        # T1.80/T1.82/T1.83: Derive output path from already-loaded config
        _output_rel = _gp.get("output_dir", "output")
        _eks_output_dir = PRJ_DIR / _eks_root / _output_rel

        # G4: Validate output directory is writable before starting pipeline
        output_dir = _eks_output_dir
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            if not os.access(str(output_dir), os.W_OK):
                self._json_response(400, {
                    "error": f"Output directory is not writable: {output_dir}",
                })
                return
        except (OSError, PermissionError) as e:
            self._json_response(400, {
                "error": f"Cannot create or write to output directory: {output_dir}",
                "detail": str(e),
            })
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
        data_dir = raw_data_dir

        with _job_lock:
            _job_state[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "progress": 0,
                "current_stage": "scan",
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
            level = _log_level
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

        # Phase → (progress_after, current_stage) mapping
        # UI stages: scan(0), parse(1), score(2), review(3), register(4)
        _PHASE_PROGRESS = {
            "A": (20, "scan"),
            "B": (75, "parse"),
            "C": (90, "review"),
        }

        def _set_phase(phase: str):
            pct, stage = _PHASE_PROGRESS[phase]
            with _job_lock:
                if _job_state[job_id]["status"] == "cancelled":
                    raise RuntimeError("Pipeline cancelled")
                _job_state[job_id]["progress"] = pct
                _job_state[job_id]["current_stage"] = stage

        # T1.80: Derive OUTPUT_DIR from schema config (resolved above as _eks_output_dir)
        OUTPUT_DIR = _eks_output_dir

        def _run():
            try:
                with _job_lock:
                    if _job_state[job_id]["status"] != "queued":
                        return
                    _job_state[job_id]["status"] = "running"
                    _job_state[job_id]["current_stage"] = "scan"
                # T1.83: Use _eks_root from closure (schema-driven from config)
                loader = SchemaLoader(PRJ_DIR / _eks_root / "config")
                config = loader.load_all()
                doc_config = loader.doc_config
                registry = get_registry()

                # T1.75: Construct ErrorManager/MessageManager before readiness gate (T1.79)
                em = ErrorManager(config_dir=PRJ_DIR / _eks_root / "config", logger=_logger)
                mm = MessageManager(config_dir=PRJ_DIR / _eks_root / "config", logger=_logger)

                # T1.77: Readiness gate — validate project setup before pipeline execution
                if not _skip_readiness:
                    validator = ProjectSetupValidator(
                        project_root=PRJ_DIR,
                        config_registry=config,
                        verbose=_debug_mode,
                    )
                    # T1.86: validation_options removed — default auto_create=True
                    _auto_create = True
                    setup_results = validator.validate_all(auto_create=_auto_create)
                    if setup_results["readiness"] != "YES":
                        missing = validator.get_missing_items()
                        error_codes = setup_results.get("error_codes", [])
                        error_msg = (
                            f"Project setup not ready (readiness={setup_results['readiness']}). "
                            f"Missing folders: {len(missing['folders'])}, "
                            f"Missing files: {len(missing['files'])}. "
                            f"Error codes: {[ec['code'] for ec in error_codes]}"
                        )
                        # T1.79: Raise through ErrorManager with structured code
                        em.handle_system_error("P1-SETUP-READINESS", detail=error_msg)

                job_logger = _LogCapture()
                orchestrator = PipelineOrchestrator(
                    config, doc_config, registry, logger=job_logger,
                    use_telemetry=False,
                    error_manager=em,
                    message_manager=mm,
                )
                orchestrator.initialize_context(
                    data_dir=PRJ_DIR / data_dir,
                    schema_dir=PRJ_DIR / _eks_root / _gp.get("config_dir", "config") / "schemas",
                    output_dir=OUTPUT_DIR,
                    archive_dir=PRJ_DIR / _eks_root / _gp.get("archive_dir", "archive"),
                    config_dir=PRJ_DIR / _eks_root / _gp.get("config_dir", "config"),
                    log_dir=PRJ_DIR / _eks_root / _gp.get("log_dir", "log"),
                )

                # T1.69: Pass job_id as run_id to logger
                if _logger:
                    _logger.run_id = job_id
                _capture_log({"level": "STATUS", "message": f"Pipeline {job_id} started", "context": "_run"})

                phase_a = orchestrator.run_phase_a(PRJ_DIR / data_dir, recursive=recursive)
                _set_phase("A")
                # T1.73: Persist checkpoint after Phase A
                orchestrator.save_checkpoint("A", checkpoint_path=OUTPUT_DIR / f"checkpoint_{job_id}_A.json")

                phase_b = orchestrator.run_phase_b(PRJ_DIR / data_dir, recursive=recursive)
                _set_phase("B")
                orchestrator.save_checkpoint("B", checkpoint_path=OUTPUT_DIR / f"checkpoint_{job_id}_B.json")

                phase_c = orchestrator.run_phase_c()
                _set_phase("C")
                orchestrator.save_checkpoint("C", checkpoint_path=OUTPUT_DIR / f"checkpoint_{job_id}_C.json")

                summary = {"phase_a": phase_a, "phase_b": phase_b, "phase_c": phase_c}
                with _job_lock:
                    _job_state[job_id]["status"] = "completed"
                    _job_state[job_id]["progress"] = 100
                    _job_state[job_id]["current_stage"] = "register"
                    _job_state[job_id]["summary"] = summary

                # T1.76: Persist pipeline_status_{job_id}.json
                status_path = OUTPUT_DIR / f"pipeline_status_{job_id}.json"
                try:
                    status_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(status_path, "w", encoding="utf-8") as f:
                        with _job_lock:
                            json.dump(_job_state.get(job_id, {}), f, indent=2, default=str)
                except Exception:
                    pass

                # T1.76: Persist pipeline_messages_{job_id}.json from ErrorManager/MessageManager
                msg_path = OUTPUT_DIR / f"pipeline_messages_{job_id}.json"
                try:
                    output_data = {
                        "errors": em.get_error_summary(),
                        "messages": mm.get_all_messages(),
                    }
                    msg_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(msg_path, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, indent=2, default=str)
                except Exception:
                    pass

                # T1.76: Persist debug_log.json via logger (filename from config.logging.debug_file_path)
                if _logger:
                    _debug_rel = _cfg.get("logging", {}).get("debug_file_path", "output/debug_log.json")
                    _debug_name = Path(_debug_rel).name
                    _logger.debug_file = OUTPUT_DIR / _debug_name
                    _logger.save_debug_log()

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
    parser.add_argument("--debug", action="store_true", help="Enable debug/trace logging (level 3)")
    parser.add_argument("--level", type=int, default=None, choices=[0, 1, 2, 3],
                        help="Logging level (0=error, 1=info, 2=debug, 3=trace)")
    parser.add_argument("--skip-readiness", action="store_true",
                        help="Bypass project readiness gate (G5 override)")
    args = parser.parse_args()
    
    global _debug_mode, _log_level, _skip_readiness
    _debug_mode = args.debug
    _log_level = args.level if args.level is not None else (3 if args.debug else 1)
    _skip_readiness = args.skip_readiness

    port = args.port or find_free_port(5001)

    if _IMPORTS_OK:
        global _logger
        _logger = EKSLogger("Phase1Server", level=_log_level)
        print(f"[Phase1Server] Engine imports OK (level={_log_level}, debug={_debug_mode})")
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
