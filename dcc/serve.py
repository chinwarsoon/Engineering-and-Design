"""
serve.py — DCC local HTTP server with HTML file picker.
Serves all .html files under dcc/ and presents a VS Code-styled
index page at / so the user can click any tool to open it.

Also handles /api/v1/pipeline/* endpoints directly (run + status)
so the browser can trigger dcc_engine_pipeline.py and poll for results.

Falls back to proxying other /api/* → FastAPI backend (port 8000) for
any other API calls (e.g. Ollama proxy, etc.).

Usage:
    python serve.py              # default port 5000
    python serve.py --port 8080  # custom port
"""

import argparse
import http.server
import json
import logging
import os
import socketserver
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from urllib.parse import unquote

PORT = 5000
ROOT = Path(__file__).parent.resolve()
BACKEND_PORT = 8000
OLLAMA_BASE = "http://localhost:11434"

SCAN_DIRS = ["ui", "tracer", "publish"]
EXCLUDE_DIRS = {"node_modules", "archive", "backup", "__pycache__"}
FOLDER_LABELS = {
    "ui": ("🖥️", "UI Tools"),
    "tracer": ("⚙️", "Tracer"),
    "publish": ("📦", "Published"),
}

# ─── PIPELINE RUN STATE ──────────────────────────────────────────────────────
# Tracks the currently active (or last completed) pipeline run.
# Only one run is allowed at a time.

_run_lock = threading.Lock()

_run_state = {
    "run_id": None,
    "status": "IDLE",  # IDLE | RUNNING | COMPLETED | FAILED
    "message": "",
    "log_lines": [],  # stdout/stderr lines captured so far
    "started_at": None,
    "ended_at": None,
    "stages": [],  # populated from pipeline output parsing
}

_PIPELINE_SCRIPT = ROOT / "workflow" / "dcc_engine_pipeline.py"


def _resolve_project_root(base_path: str) -> str:
    """
    Normalize base_path to the project root that contains config/schemas/.

    The UI sends the directory of the selected Excel file (e.g. .../dcc/data/).
    The pipeline expects the project root (e.g. .../dcc/) which contains
    config/schemas/dcc_register_setup.json.

    Strategy: walk up from the provided path until a directory containing
    config/schemas/ is found. Falls back to the original path if not found
    within 5 levels (avoids walking past the project boundary).
    """
    current = Path(base_path).resolve()
    for _ in range(5):
        if (current / "config" / "schemas").is_dir():
            return str(current)
        parent = current.parent
        if parent == current:  # reached filesystem root
            break
        current = parent
    return base_path  # fallback: return original, let pipeline report the error


# Stage keywords to detect in pipeline stdout and map to stage card IDs
_STAGE_PATTERNS = [
    ("stage1", ["File Upload", "upload", "input file"]),
    ("stage2", ["Sheet Selection", "sheet", "header row"]),
    ("stage3", ["Column Mapping", "column mapping", "mapper"]),
    ("stage4", ["Data Validation", "validation", "processor"]),
    ("stage5", ["Processing", "calculation", "reorder"]),
    ("stage6", ["Export", "export", "CSV", "Excel"]),
]


def _parse_stage_from_line(line: str) -> str | None:
    """Return stage id if the line matches a known stage keyword."""
    lower = line.lower()
    for stage_id, keywords in _STAGE_PATTERNS:
        if any(kw.lower() in lower for kw in keywords):
            return stage_id
    return None


def _run_pipeline_async(run_id: str, base_path: str, upload_file_name: str) -> None:
    """
    Execute dcc_engine_pipeline.py in a subprocess.
    Captures stdout/stderr line-by-line into _run_state["log_lines"].
    Updates _run_state["status"] on completion.
    """
    global _run_state

    cmd = [
        sys.executable,
        str(_PIPELINE_SCRIPT),
        "--base-path",
        base_path,
    ]
    if upload_file_name:
        cmd += ["--upload-file", upload_file_name]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    active_stages = {}  # stage_id -> status

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(ROOT / "workflow"),
            env=env,
        )

        with _run_lock:
            _run_state["log_lines"].append(
                f"[{time.strftime('%H:%M:%S')}] Pipeline started (PID {proc.pid})"
            )
            _run_state["log_lines"].append(
                f"[{time.strftime('%H:%M:%S')}] base_path: {base_path}"
            )
            if upload_file_name:
                _run_state["log_lines"].append(
                    f"[{time.strftime('%H:%M:%S')}] upload_file: {upload_file_name}"
                )

        for raw_line in proc.stdout:
            line = raw_line.rstrip()
            ts = time.strftime("%H:%M:%S")
            entry = f"[{ts}] {line}"

            # Detect stage transitions from output
            stage_id = _parse_stage_from_line(line)
            if stage_id and stage_id not in active_stages:
                active_stages[stage_id] = "RUNNING"

            # Mark previous stages as PASS when a new one starts
            stage_ids = [s[0] for s in _STAGE_PATTERNS]
            if stage_id:
                idx = stage_ids.index(stage_id)
                for prev in stage_ids[:idx]:
                    if active_stages.get(prev) == "RUNNING":
                        active_stages[prev] = "PASS"

            # Detect export completion → mark all stages PASS
            if "export" in line.lower() and ("✓" in line or "complete" in line.lower()):
                for sid in stage_ids:
                    if active_stages.get(sid) in ("RUNNING", None):
                        active_stages[sid] = "PASS"

            # Build stages list for status response
            stages_snapshot = [
                {"id": sid, "status": active_stages.get(sid, "PENDING")}
                for sid in stage_ids
            ]

            with _run_lock:
                _run_state["log_lines"].append(entry)
                _run_state["stages"] = stages_snapshot

        proc.wait()
        ended = time.strftime("%Y-%m-%dT%H:%M:%S")

        # Mark all stages that were running as PASS/FAIL based on return code
        final_stage_status = "PASS" if proc.returncode == 0 else "FAIL"
        for sid in [s[0] for s in _STAGE_PATTERNS]:
            if (
                active_stages.get(sid) in ("RUNNING", None)
                and active_stages.get(sid) != "PASS"
            ):
                active_stages[sid] = final_stage_status

        stages_final = [
            {"id": sid, "status": active_stages.get(sid, "PENDING")}
            for sid in [s[0] for s in _STAGE_PATTERNS]
        ]

        with _run_lock:
            _run_state["ended_at"] = ended
            _run_state["stages"] = stages_final
            if proc.returncode == 0:
                _run_state["status"] = "COMPLETED"
                _run_state["message"] = "Pipeline completed successfully."
                _run_state["log_lines"].append(
                    f"[{time.strftime('%H:%M:%S')}] ✓ Pipeline exited with code 0"
                )
            else:
                _run_state["status"] = "FAILED"
                _run_state["message"] = f"Pipeline exited with code {proc.returncode}."
                _run_state["log_lines"].append(
                    f"[{time.strftime('%H:%M:%S')}] ✗ Pipeline exited with code {proc.returncode}"
                )

    except Exception as exc:
        with _run_lock:
            _run_state["status"] = "FAILED"
            _run_state["message"] = str(exc)
            _run_state["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            _run_state["log_lines"].append(f"[ERROR] {exc}")


def _handle_pipeline_run(handler) -> None:
    """Handle POST /api/v1/pipeline/run"""
    global _run_state

    # Read request body
    length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(length) if length else b"{}"
    try:
        payload = json.loads(body)
    except Exception:
        payload = {}

    raw_base_path = payload.get("base_path", str(ROOT))
    upload_file_name = payload.get("upload_file_name", "")

    # Normalize: the UI sends the directory of the selected file (e.g. .../dcc/data/).
    # The pipeline needs the project root that contains config/schemas/.
    base_path = _resolve_project_root(raw_base_path)

    # Reject if already running
    with _run_lock:
        if _run_state["status"] == "RUNNING":
            resp = json.dumps(
                {
                    "error": "Pipeline already running",
                    "run_id": _run_state["run_id"],
                }
            ).encode()
            handler.send_response(409)
            handler.send_header("Content-Type", "application/json")
            handler.send_header("Content-Length", str(len(resp)))
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.end_headers()
            handler.wfile.write(resp)
            return

        # Reset state for new run
        run_id = str(uuid.uuid4())[:8]
        _run_state.update(
            {
                "run_id": run_id,
                "status": "RUNNING",
                "message": "Pipeline started",
                "log_lines": [],
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "ended_at": None,
                "stages": [],
            }
        )

    # Launch pipeline in background thread
    t = threading.Thread(
        target=_run_pipeline_async,
        args=(run_id, base_path, upload_file_name),
        daemon=True,
    )
    t.start()

    resp = json.dumps(
        {"run_id": run_id, "status": "RUNNING", "message": "Pipeline started"}
    ).encode()
    handler.send_response(202)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(resp)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(resp)


def _handle_pipeline_status(handler) -> None:
    """Handle GET /api/v1/pipeline/status"""
    with _run_lock:
        # Return new log lines since last poll (tracked by client via ?since= param)
        # For simplicity, always return all lines (client deduplicates by appending)
        snapshot = dict(_run_state)

    resp = json.dumps(snapshot).encode()
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(resp)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(resp)


def _proxy(handler, method: str) -> None:
    """Forward /api/* to the FastAPI backend, stripping the /api prefix."""
    target_path = handler.path[4:]  # strip /api
    target_url = f"http://localhost:{BACKEND_PORT}{target_path}"

    length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(length) if length else None

    req = urllib.request.Request(
        target_url,
        data=body,
        method=method,
        headers={
            "Content-Type": handler.headers.get("Content-Type", "application/json")
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = resp.read()
            handler.send_response(resp.status)
            handler.send_header(
                "Content-Type", resp.headers.get("Content-Type", "application/json")
            )
            handler.send_header("Content-Length", str(len(payload)))
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.end_headers()
            handler.wfile.write(payload)
    except urllib.error.HTTPError as exc:
        payload = exc.read()
        handler.send_response(exc.code)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(payload)))
        handler.end_headers()
        handler.wfile.write(payload)
    except Exception as exc:
        msg = str(exc).encode()
        handler.send_response(502)
        handler.send_header("Content-Type", "text/plain")
        handler.send_header("Content-Length", str(len(msg)))
        handler.end_headers()
        handler.wfile.write(msg)


def _proxy_ollama(handler, path: str, method: str, body: bytes = None) -> None:
    """Forward /ollama/* to the local Ollama server."""
    target_url = f"{OLLAMA_BASE}{path}"
    req = urllib.request.Request(target_url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read()
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.send_header("Content-Length", str(len(payload)))
            handler.end_headers()
            handler.wfile.write(payload)
    except urllib.error.URLError as exc:
        msg = json.dumps({"error": str(exc)}).encode()
        handler.send_response(502)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(msg)))
        handler.end_headers()
        handler.wfile.write(msg)
    except Exception as exc:
        msg = json.dumps({"error": str(exc)}).encode()
        handler.send_response(500)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(msg)))
        handler.end_headers()
        handler.wfile.write(msg)


def _collect_html(scan_dirs):
    """Walk scan_dirs and return {folder_key: [{name, rel}]} dict."""
    groups = {}
    for folder in scan_dirs:
        base = ROOT / folder
        if not base.exists():
            continue
        files = []
        for html in sorted(base.rglob("*.html")):
            parts = set(html.relative_to(ROOT).parts)
            if parts & EXCLUDE_DIRS:
                continue
            rel = html.relative_to(ROOT).as_posix()
            files.append({"name": html.name, "rel": rel})
        if files:
            groups[folder] = files
    return groups


def _build_index():
    """Generate the picker HTML page."""
    groups = _collect_html(SCAN_DIRS)
    total = sum(len(v) for v in groups.values())

    cards_html = ""
    for folder, files in groups.items():
        icon, label = FOLDER_LABELS.get(folder, ("📄", folder))
        items = "".join(
            f'<a class="file-link" href="/{f["rel"]}">'
            f'<span class="file-icon">📄</span>'
            f'<span class="file-name">{f["name"]}</span>'
            f"</a>"
            for f in files
        )
        cards_html += f"""
        <div class="group-card">
          <div class="group-header">
            <span class="group-icon">{icon}</span>
            <span class="group-label">{label}</span>
            <span class="group-count">{len(files)}</span>
          </div>
          <div class="group-files">{items}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DCC Tool Launcher</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Inter',sans-serif;font-size:13px;background:#0d1117;color:#e6edf3;min-height:100vh}}
  .titlebar{{height:36px;background:#161b22;border-bottom:1px solid #30363d;
             display:flex;align-items:center;padding:0 16px;gap:10px;position:sticky;top:0;z-index:10}}
  .titlebar-logo{{font-weight:700;font-size:13px;color:#e6edf3}}
  .titlebar-logo span{{color:#58a6ff}}
  .titlebar-meta{{margin-left:auto;font-size:11px;color:#484f58}}
  .search-wrap{{padding:16px 20px 8px;max-width:900px;margin:0 auto}}
  .search-input{{width:100%;background:#21262d;border:1px solid #30363d;border-radius:6px;
                 padding:8px 14px;color:#e6edf3;font-size:13px;font-family:inherit;outline:none}}
  .search-input:focus{{border-color:#58a6ff}}
  .search-input::placeholder{{color:#484f58}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
         gap:14px;padding:12px 20px 32px;max-width:900px;margin:0 auto}}
  .group-card{{background:#161b22;border:1px solid #30363d;border-radius:8px;overflow:hidden}}
  .group-header{{display:flex;align-items:center;gap:8px;padding:10px 14px;
                 background:#21262d;border-bottom:1px solid #30363d}}
  .group-icon{{font-size:15px}}
  .group-label{{font-weight:600;font-size:12px;color:#e6edf3;flex:1}}
  .group-count{{font-size:10px;background:#2d333b;color:#8b949e;
                padding:1px 7px;border-radius:10px;font-weight:600}}
  .group-files{{padding:8px 0}}
  .file-link{{display:flex;align-items:center;gap:8px;padding:7px 14px;
              color:#8b949e;text-decoration:none;transition:background .12s,color .12s}}
  .file-link:hover{{background:#21262d;color:#58a6ff}}
  .file-icon{{font-size:13px;flex-shrink:0}}
  .file-name{{font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  .file-link.hidden{{display:none}}
  .statusbar{{position:fixed;bottom:0;left:0;right:0;height:22px;background:#2f81f7;
              color:#fff;display:flex;align-items:center;padding:0 14px;font-size:11px;gap:16px}}
  .sb-right{{margin-left:auto}}
</style>
</head>
<body>
<div class="titlebar">
  <span class="titlebar-logo">DCC <span>Tool Launcher</span></span>
  <span class="titlebar-meta">{total} tools available</span>
</div>
<div class="search-wrap">
  <input id="search" class="search-input" type="search"
         placeholder="Search tools..." autofocus autocomplete="off">
</div>
<div class="grid" id="grid">
  {cards_html}
</div>
<div class="statusbar">
  <span id="status-count">{total} tools</span>
  <span class="sb-right">DCC Local Server · port {PORT}</span>
</div>
<script>
const input = document.getElementById('search');
input.addEventListener('input', function() {{
  const q = this.value.toLowerCase();
  let visible = 0;
  document.querySelectorAll('.file-link').forEach(a => {{
    const match = a.querySelector('.file-name').textContent.toLowerCase().includes(q);
    a.classList.toggle('hidden', !match);
    if (match) visible++;
  }});
  document.querySelectorAll('.group-card').forEach(card => {{
    const anyVisible = [...card.querySelectorAll('.file-link')].some(a => !a.classList.contains('hidden'));
    card.style.display = anyVisible ? '' : 'none';
  }});
  document.getElementById('status-count').textContent =
    q ? visible + ' of {total} tools' : '{total} tools';
}});
</script>
</body>
</html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        path = unquote(self.path).split("?")[0]
        if path == "/api/v1/pipeline/run":
            _handle_pipeline_run(self)
            return
        # Safety net: catch any other /api/v1/pipeline/* that wasn't matched above
        if path.startswith("/api/v1/pipeline/"):
            msg = json.dumps({"error": f"Unknown pipeline endpoint: {path}"}).encode()
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(msg)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(msg)
            return
        if path.startswith("/api/"):
            _proxy(self, "POST")
            return
        if path.startswith("/ollama/"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else b""
            _proxy_ollama(self, path.replace("/ollama", ""), "POST", body)
            return
        self.send_response(405)
        self.end_headers()

    def do_GET(self):
        path = unquote(self.path).split("?")[0]
        if path == "/api/v1/pipeline/status":
            _handle_pipeline_status(self)
            return
        # Safety net: catch any other /api/v1/pipeline/* that wasn't matched above
        if path.startswith("/api/v1/pipeline/"):
            msg = json.dumps({"error": f"Unknown pipeline endpoint: {path}"}).encode()
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(msg)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(msg)
            return
        if path.startswith("/api/"):
            _proxy(self, "GET")
            return
        if path.startswith("/ollama/"):
            _proxy_ollama(self, path.replace("/ollama", ""), "GET")
            return
        if path in ("/", ""):
            body = _build_index().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        code = args[1] if len(args) > 1 else "?"
        if str(code) not in ("200", "304"):
            print(f"  {self.address_string()} {args[0]} → {code}")


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        import traceback

        etype, value, _ = sys.exc_info()
        if etype is ConnectionResetError:
            logging.debug(
                "Connection reset by %s (client closed connection)", client_address
            )
            return
        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DCC local tool server")
    parser.add_argument(
        "--port", type=int, default=PORT, help="Port to listen on (default 5000)"
    )
    args = parser.parse_args()
    PORT = args.port

    with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"DCC Tool Launcher → http://localhost:{PORT}")
        print(
            f"Serving {sum(len(v) for v in _collect_html(SCAN_DIRS).values())} tools from {ROOT}"
        )
        httpd.serve_forever()
