"""EKS Main Server — Launcher + Proxy (port 5000).

Per Appendix G §10, the main server acts as a file-picker landing page
and reverse proxy for phase-specific backends:
  - /                          → _build_index() dynamic tool-picker
  - /api/v{N}/*                → proxy to localhost:500{N} (phase N backend)
  - /api/*                     → 404 JSON (un-versioned paths rejected)
  - /ollama/*                  → proxy to localhost:11434 (Ollama API)
  - /ui/<path>                 → static file serve from ROOT/ui/

Usage:
    python eks/server.py
    python eks/server.py --port 5000 --phase1-port 5001
"""

import json
import os
import re
import socket
import sys
import threading
import traceback
from argparse import ArgumentParser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, unquote
from urllib.request import Request, urlopen


def find_free_port(start: int = 5001, max_attempts: int = 100) -> int:
    """Find a free port starting from *start*."""
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError(f"No free port found in range {start}-{start + max_attempts}")


class ReusableTCPServer(HTTPServer):
    """HTTPServer that reuses the address so we can restart quickly."""
    allow_reuse_address = True
    daemon_threads = True


ROOT = Path(__file__).parent.resolve()
COMMON = ROOT.parent / "common"
SCAN_DIRS = ["ui"]
EXCLUDE_DIRS: set = {"node_modules", "archive", "backup", "__pycache__", "static", "templates"}
FOLDER_LABELS: Dict[str, tuple] = {"ui": ("🖥️", "EKS Tools")}


class MainServerHandler(SimpleHTTPRequestHandler):
    """Request handler for the main launcher server."""

    phase1_backend: str = "http://127.0.0.1:5001"
    ollama_backend: str = "http://127.0.0.1:11434"
    proxy_ports: Dict[int, int] = {1: 5001}

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    # ------------------------------------------------------------------
    # Compliance hooks (AGENTS.md §18.12)
    # ------------------------------------------------------------------
    def end_headers(self) -> None:
        """Inject cache-busting headers on every response (A)."""
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def handle_error(self, request, client_address) -> None:
        """Suppress ConnectionResetError tracebacks (C)."""
        exc = sys.exc_info()[1]
        if isinstance(exc, ConnectionResetError):
            return
        super().handle_error(request, client_address)

    def log_message(self, format, *args) -> None:
        """Suppress 200/304 log lines (F)."""
        if args[0] in ("200", "304"):
            return
        print(f"[MainServer] {args[0]} {args[1]} {args[2]}")

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------
    def _get_backend_for(self, path: str) -> str:
        """Extract version N from /api/v{N}/ and return target backend URL."""
        m = re.match(r"/api/v(\d+)/", path)
        if m:
            n = int(m.group(1))
            port = self.proxy_ports.get(n, 5000 + n)
            return f"http://127.0.0.1:{port}"
        return self.phase1_backend

    def _route_api(self):
        """Route versioned API calls to phase backends; reject un-versioned."""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path.startswith("/api/v") and re.match(r"/api/v\d+/", path):
            self._proxy_to(self._get_backend_for(path))
        elif path.startswith("/api/"):
            self.send_response(404)
            self._set_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": f"Unknown API path: {path}. Use versioned prefix /api/v{N}/"}).encode()
            )
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/":
            self._build_index()
        elif path.startswith("/api/"):
            self._route_api()
        elif path.startswith("/ollama/"):
            self._proxy_ollama()
        elif path.startswith("/common/"):
            self._serve_common(path[8:])
        elif path.startswith("/ui/"):
            self._serve_static("ui/" + path[4:])
        else:
            self._serve_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path.startswith("/api/"):
            self._route_api()
        elif path.startswith("/ollama/"):
            self._proxy_ollama()
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    def do_PUT(self):
        path = unquote(urlparse(self.path).path)
        if path.startswith("/api/"):
            self._route_api()
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    def do_DELETE(self):
        path = unquote(urlparse(self.path).path)
        if path.startswith("/api/"):
            self._route_api()
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    # ------------------------------------------------------------------
    # _build_index() — dynamic tool-picker (AGENTS.md §18.12)
    # ------------------------------------------------------------------
    def _collect_html(self) -> Dict[str, Any]:
        """Walk SCAN_DIRS and return grouped file list."""
        result: Dict[str, Any] = {}
        for scan_dir in SCAN_DIRS:
            scan_path = ROOT / scan_dir
            if not scan_path.is_dir():
                continue
            for f in sorted(scan_path.rglob("*.html")):
                if any(excl in f.parts for excl in EXCLUDE_DIRS):
                    continue
                rel = f.relative_to(ROOT).as_posix()
                parent = f.parent
                try:
                    folder_rel = parent.relative_to(scan_path).as_posix()
                except ValueError:
                    folder_rel = "."
                folder_key = f"{scan_dir}/{folder_rel}" if folder_rel != "." else scan_dir
                icon, label = FOLDER_LABELS.get(scan_dir, ("📄", scan_dir.title()))
                if folder_key not in result:
                    result[folder_key] = {"icon": icon, "label": label, "files": []}
                name = f.stem.replace("_", " ").replace("-", " ").title()
                result[folder_key]["files"].append({"name": name, "rel_path": rel})
        return result

    def _build_index(self):
        """Generate and serve the dynamic tool-picker page."""
        groups = self._collect_html()
        total = sum(len(g["files"]) for g in groups.values())
        cards = ""
        for fkey in sorted(groups):
            g = groups[fkey]
            for fe in g["files"]:
                cards += (
                    f'<div class="card" onclick="location.href=\'/{fe["rel_path"]}\'">'
                    f'<div class="card-icon">{g["icon"]}</div>'
                    f'<div class="card-label">{fe["name"]}</div>'
                    f'<div class="card-path">{fe["rel_path"]}</div></div>\n'
                )
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EKS Launcher</title>
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;min-height:100vh;display:flex;flex-direction:column}}
  .header{{padding:2rem 1rem 1rem;text-align:center;border-bottom:1px solid #30363d}}
  .header h1{{font-size:1.5rem;font-weight:600;color:#f0f6fc}}
  .header p{{color:#8b949e;font-size:.85rem;margin-top:.25rem}}
  .search{{max-width:480px;margin:1rem auto 0}}
  .search input{{width:100%;padding:.5rem .75rem;background:#161b22;border:1px solid #30363d;border-radius:6px;color:#c9d1d9;font-size:.85rem;outline:none}}
  .search input:focus{{border-color:#58a6ff}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;padding:1.5rem;max-width:960px;margin:0 auto;flex:1}}
  .card{{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:1rem;cursor:pointer;transition:border-color .2s,box-shadow .2s}}
  .card:hover{{border-color:#58a6ff;box-shadow:0 0 0 1px #58a6ff}}
  .card-icon{{font-size:2rem;margin-bottom:.5rem}}
  .card-label{{font-weight:600;font-size:.9rem;color:#f0f6fc}}
  .card-path{{font-size:.75rem;color:#8b949e;margin-top:.25rem}}
  .footer{{padding:.5rem 1rem;border-top:1px solid #30363d;font-size:.75rem;color:#8b949e;text-align:center}}
</style>
</head>
<body>
<div class="header"><h1>EKS — Engineering Knowledge System</h1><p>Select a tool to launch</p><div class="search"><input type="text" id="q" placeholder="Filter tools..." oninput="filterCards(this.value)"></div></div>
<div class="grid" id="grid">{cards}</div>
<div class="footer">{total} tool(s) available</div>
<script>
function filterCards(q){{q=q.toLowerCase();document.querySelectorAll('.card').forEach(function(c){{c.style.display=c.textContent.toLowerCase().includes(q)?'':'none'}})}}
</script>
</body>
</html>"""
        body = html.encode("utf-8")
        self.send_response(200)
        self._set_cors()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ------------------------------------------------------------------
    # Static file serving (with path security)
    # ------------------------------------------------------------------
    def _serve_static(self, rel_path: str):
        """Serve static files from ROOT directory with traversal guard."""
        safe = Path(rel_path).as_posix().lstrip("/")
        resolved = (ROOT / safe).resolve()
        if not resolved.is_relative_to(ROOT):
            self.send_response(403)
            self._set_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Access denied"}')
            return
        if resolved.exists() and resolved.is_file():
            ext = resolved.suffix.lower()
            content_type = {
                ".html": "text/html",
                ".css": "text/css",
                ".js": "application/javascript",
                ".json": "application/json",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon",
            }.get(ext, "application/octet-stream")
            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(resolved.stat().st_size))
            self.end_headers()
            with open(resolved, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    # ------------------------------------------------------------------
    # Static file serving — /common/ (shared design system)
    # ------------------------------------------------------------------
    def _serve_common(self, rel_path: str):
        """Serve files from the project-wide common/ directory."""
        safe = Path(rel_path).as_posix().lstrip("/")
        resolved = (COMMON / safe).resolve()
        if not resolved.is_relative_to(COMMON):
            self.send_response(403)
            self._set_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Access denied"}')
            return
        if resolved.exists() and resolved.is_file():
            ext = resolved.suffix.lower()
            content_type = {
                ".html": "text/html",
                ".css": "text/css",
                ".js": "application/javascript",
                ".json": "application/json",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon",
            }.get(ext, "application/octet-stream")
            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(resolved.stat().st_size))
            self.end_headers()
            with open(resolved, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    # ------------------------------------------------------------------
    # Proxy — phase backends
    # ------------------------------------------------------------------
    def _proxy_to(self, target_base: str):
        """Proxy request to a phase backend. Timeout: 120s (E)."""
        parsed = urlparse(self.path)
        target_url = target_base.rstrip("/") + parsed.path
        if parsed.query:
            target_url += "?" + parsed.query
        body = None
        content_length = self.headers.get("Content-Length")
        if content_length:
            body = self.rfile.read(int(content_length))
        try:
            req = Request(
                target_url,
                data=body,
                headers={k: v for k, v in self.headers.items() if k.lower() not in ("host", "connection")},
                method=self.command,
            )
            resp = urlopen(req, timeout=120)
            self.send_response(resp.status)
            self._set_cors()
            for k, v in resp.headers.items():
                if k.lower() not in ("transfer-encoding", "connection", "content-encoding"):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.read())
        except HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            self._set_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        except URLError as e:
            if "Connection refused" in str(e):
                port = target_base.split(":")[-1]
                self.send_response(503)
                self._set_cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({
                        "error": "Phase backend not running",
                        "port": int(port),
                        "start": f"python eks/ui/backend/phase1_server.py",
                    }).encode()
                )
            else:
                self.send_response(502)
                self._set_cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({
                        "status": "error",
                        "error": {"code": "PROXY_UPSTREAM_ERR", "message": str(e), "severity": "HIGH"},
                    }).encode()
                )
        except Exception as e:
            self.send_response(500)
            self._set_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({
                    "status": "error",
                    "error": {"code": "PROXY_INTERNAL_ERR", "message": str(e), "severity": "HIGH"},
                }).encode()
            )

    # ------------------------------------------------------------------
    # Proxy — Ollama
    # ------------------------------------------------------------------
    def _proxy_ollama(self):
        """Proxy /ollama/* to localhost:11434. Timeout: 30s."""
        path = unquote(urlparse(self.path).path)
        target_url = self.ollama_backend.rstrip("/") + path[len("/ollama"):]
        body = None
        content_length = self.headers.get("Content-Length")
        if content_length:
            body = self.rfile.read(int(content_length))
        try:
            req = Request(
                target_url,
                data=body,
                headers={k: v for k, v in self.headers.items() if k.lower() not in ("host", "connection")},
                method=self.command,
            )
            resp = urlopen(req, timeout=30)
            self.send_response(resp.status)
            self._set_cors()
            for k, v in resp.headers.items():
                if k.lower() not in ("transfer-encoding", "connection", "content-encoding"):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.read())
        except URLError as e:
            self.send_response(503)
            self._set_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({
                    "error": "Ollama not running on port 11434. Install from https://ollama.ai and start with: ollama serve",
                }).encode()
            )
        except Exception as e:
            self.send_response(500)
            self._set_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


def start_phase1_backend(port: int):
    """Start the Phase 1 backend server as a subprocess."""
    import subprocess
    script = Path(__file__).resolve().parent / "ui" / "backend" / "phase1_server.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.Popen(
        [sys.executable, str(script), "--port", str(port)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    def _reader():
        for line in proc.stdout:
            print(f"[Phase1Backend] {line.decode('utf-8', errors='replace').rstrip()}")

    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    return proc


def main():
    parser = ArgumentParser(description="EKS Main Launcher Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default 5000)")
    parser.add_argument("--phase1-port", type=int, default=None, help="Phase 1 backend port (default: auto, main_port + 1)")
    parser.add_argument("--skip-phase1", action="store_true", help="Skip launching Phase 1 backend")
    args = parser.parse_args()

    actual_port = find_free_port(args.port)
    if actual_port != args.port:
        print(f"[MainServer] Port {args.port} in use, using {actual_port}")

    phase1_port = args.phase1_port or (actual_port + 1)
    if not args.skip_phase1:
        free = find_free_port(phase1_port)
        if free != phase1_port:
            print(f"[MainServer] Phase 1 backend port {phase1_port} in use, using {free}")
            phase1_port = free
        print(f"[MainServer] Starting Phase 1 backend on port {phase1_port}...")
        start_phase1_backend(phase1_port)

    MainServerHandler.phase1_backend = f"http://127.0.0.1:{phase1_port}"
    MainServerHandler.proxy_ports[1] = phase1_port

    server = ReusableTCPServer(("0.0.0.0", actual_port), MainServerHandler)
    print(f"[MainServer] EKS Tool Launcher -> http://localhost:{actual_port}")
    print(f"[MainServer] Phase 1 backend at {MainServerHandler.phase1_backend}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[MainServer] Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
