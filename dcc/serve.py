"""
serve.py — DCC local HTTP server with HTML file picker.
Serves all .html files under dcc/ and presents a VS Code-styled
index page at / so the user can click any tool to open it.

Also proxies /api/* → FastAPI backend (port 8000) so the browser
never needs to reach a second port (avoids Codespaces private-port issues).

Usage:
    python serve.py              # default port 5000
    python serve.py --port 8080  # custom port
"""

import http.server
import socketserver
import os
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import unquote

PORT = 5000
ROOT = Path(__file__).parent.resolve()
BACKEND_PORT = 8000

SCAN_DIRS = ["ui", "tracer", "publish"]
EXCLUDE_DIRS = {"node_modules", "archive", "backup", "__pycache__"}
FOLDER_LABELS = {
    "ui":      ("🖥️",  "UI Tools"),
    "tracer":  ("⚙️",  "Tracer"),
    "publish": ("📦", "Published"),
}


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
            f'</a>'
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

    def do_GET(self):
        path = unquote(self.path).split("?")[0]
        if path.startswith("/api/"):
            _proxy(self, "GET")
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

    def do_POST(self):
        path = unquote(self.path).split("?")[0]
        if path.startswith("/api/"):
            _proxy(self, "POST")
            return
        self.send_response(405)
        self.end_headers()

    def log_message(self, fmt, *args):
        code = args[1] if len(args) > 1 else "?"
        if str(code) not in ("200", "304"):
            print(f"  {self.address_string()} {args[0]} → {code}")


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DCC local tool server")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on (default 5000)")
    args = parser.parse_args()
    PORT = args.port

    with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"DCC Tool Launcher → http://localhost:{PORT}")
        print(f"Serving {sum(len(v) for v in _collect_html(SCAN_DIRS).values())} tools from {ROOT}")
        httpd.serve_forever()
