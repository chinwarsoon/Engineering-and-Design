"""EKS Main Server — Launcher + Proxy (port 5000).

Per Appendix G §10, the main server acts as a file-picker landing page
and reverse proxy for phase-specific backends:
  - /                          → HTML file picker (lists eks/ui/*.html)
  - /api/*                     → proxy to localhost:5001 (Phase 1 backend)
  - /ollama/*                  → proxy to localhost:11434 (Ollama API)
  - /ui/<path>                 → static file serve from eks/ui/

Usage:
    python eks/server.py
    python eks/server.py --port 5000
"""

import json
import os
import re
import socket
import sys
import threading
from argparse import ArgumentParser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
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


UI_DIR = Path(__file__).resolve().parent / "ui"


class MainServerHandler(SimpleHTTPRequestHandler):
    """Request handler for the main launcher server."""

    # Target backends
    phase1_backend: str = "http://127.0.0.1:5001"
    ollama_backend: str = "http://127.0.0.1:11434"

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._serve_static("index.html")
        elif path.startswith("/api/"):
            self._proxy_to(self.phase1_backend)
        elif path.startswith("/ollama/"):
            self._proxy_to(self.ollama_backend)
        elif path.startswith("/ui/"):
            self._serve_static(path[4:])
        else:
            self._serve_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            self._proxy_to(self.phase1_backend)
        elif path.startswith("/ollama/"):
            self._proxy_to(self.ollama_backend)
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._proxy_to(self.phase1_backend)
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._proxy_to(self.phase1_backend)
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    # ------------------------------------------------------------------
    def _serve_file_picker(self):
        """Render HTML file picker listing standalone tools in eks/ui/."""
        self.send_response(200)
        self._set_cors()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        html_files = sorted(UI_DIR.glob("**/*.html"))
        links = []
        for f in html_files:
            rel = f.relative_to(UI_DIR)
            name = rel.stem.replace("_", " ").replace("-", " ").title()
            links.append(f'<li><a href="/ui/{rel.as_posix()}">{name}</a> <code>({rel.as_posix()})</code></li>')

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>EKS Launcher</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }}
  h1 {{ color: #333; }}
  ul {{ list-style: none; padding: 0; }}
  li {{ padding: 0.5rem 0; border-bottom: 1px solid #eee; }}
  a {{ color: #0066cc; text-decoration: none; font-size: 1.1rem; }}
  a:hover {{ text-decoration: underline; }}
  code {{ color: #888; font-size: 0.85rem; margin-left: 0.5rem; }}
  .info {{ margin-top: 2rem; padding: 1rem; background: #f5f5f5; border-radius: 4px; font-size: 0.9rem; }}
</style>
</head>
<body>
<h1>EKS — Engineering Knowledge System</h1>
<p>Select a tool to launch:</p>
<ul>
{''.join(links)}
</ul>
<div class="info">
<strong>Proxies:</strong><br>
/api/* → Phase 1 backend (:{self.server.server_address[1] + 1})<br>
/ollama/* → Ollama API (:11434)
</div>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))

    def _serve_static(self, rel_path: str):
        """Serve static files from eks/ui/ directory."""
        safe = Path(rel_path).as_posix().lstrip("/")
        file_path = UI_DIR / safe
        if file_path.exists() and file_path.is_file():
            ext = file_path.suffix.lower()
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
            self.send_header("Content-Length", str(file_path.stat().st_size))
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self._set_cors()
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def _proxy_to(self, target_base: str):
        """Proxy the current request to *target_base*."""
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
            resp = urlopen(req, timeout=30)
            self.send_response(resp.status)
            self._set_cors()
            for k, v in resp.headers.items():
                if k.lower() not in ("transfer-encoding", "connection", "content-encoding"):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.read())
        except Exception as e:
            self.send_response(502)
            self._set_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default logging to stderr; use print instead."""
        print(f"[MainServer] {args[0]} {args[1]} {args[2]}")


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
    # Start a thread to read and print subprocess output
    def _reader():
        for line in proc.stdout:
            print(f"[Phase1Backend] {line.decode('utf-8', errors='replace').rstrip()}")
    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    return proc


def main():
    parser = ArgumentParser(description="EKS Main Launcher Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default 5000)")
    parser.add_argument("--phase1-port", type=int, default=None,
                        help="Phase 1 backend port (default: auto, main_port + 1)")
    parser.add_argument("--skip-phase1", action="store_true", help="Skip launching Phase 1 backend")
    args = parser.parse_args()

    phase1_port = args.phase1_port or (args.port + 1)

    if not args.skip_phase1:
        free = find_free_port(phase1_port)
        if free != phase1_port:
            print(f"[MainServer] Phase 1 backend port {phase1_port} in use, using {free}")
            phase1_port = free
        print(f"[MainServer] Starting Phase 1 backend on port {phase1_port}...")
        start_phase1_backend(phase1_port)

    MainServerHandler.phase1_backend = f"http://127.0.0.1:{phase1_port}"

    server = ReusableTCPServer(("0.0.0.0", args.port), MainServerHandler)
    print(f"[MainServer] Listening on http://0.0.0.0:{args.port}")
    print(f"[MainServer] Phase 1 backend at {MainServerHandler.phase1_backend}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[MainServer] Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
