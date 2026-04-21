"""
serve.py — Minimal standalone file server for the DCC Static Tracer dashboard.

Serves static_dashboard.html and proxies /api/* to the FastAPI backend.
No DCC project paths or assumptions — works from any directory.

Usage (called by launch.py):
    python tracer/serve.py --port 5000 --backend-port 8000
"""

import argparse
import http.server
import socketserver
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import unquote

_HERE = Path(__file__).parent.resolve()
_DASHBOARD = _HERE / "static_dashboard.html"


def _proxy(handler, method: str, backend_port: int) -> None:
    target_path = handler.path[4:]  # strip /api
    target_url = f"http://localhost:{backend_port}{target_path}"
    length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(length) if length else None
    req = urllib.request.Request(
        target_url, data=body, method=method,
        headers={"Content-Type": handler.headers.get("Content-Type", "application/json")},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = resp.read()
            handler.send_response(resp.status)
            handler.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
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


def make_handler(backend_port: int):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(_HERE), **kwargs)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):
            path = unquote(self.path).split("?")[0]
            if path.startswith("/api/"):
                _proxy(self, "GET", backend_port)
                return
            if path in ("/", ""):
                # Serve the dashboard directly at root
                body = _DASHBOARD.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                super().do_GET()

        def do_POST(self):
            path = unquote(self.path).split("?")[0]
            if path.startswith("/api/"):
                _proxy(self, "POST", backend_port)
                return
            self.send_response(405)
            self.end_headers()

        def log_message(self, fmt, *args):
            code = args[1] if len(args) > 1 else "?"
            if str(code) not in ("200", "304"):
                print(f"  {self.address_string()} {args[0]} → {code}")

    return Handler


class _ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    parser = argparse.ArgumentParser(description="DCC Tracer dashboard file server")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--backend-port", type=int, default=8000)
    args = parser.parse_args()

    Handler = make_handler(args.backend_port)
    with _ReusableTCPServer(("0.0.0.0", args.port), Handler) as httpd:
        print(f"Dashboard server → http://localhost:{args.port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
