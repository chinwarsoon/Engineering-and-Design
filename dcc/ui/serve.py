import http.server
import socketserver
import socket
import os
import json
import urllib.request
import urllib.error

PORT = 5000
DIRECTORY = "dcc"
OLLAMA_BASE = "http://localhost:11434"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.path = "/Excel Explorer Pro working.html"
        elif self.path.startswith("/ollama/"):
            self._proxy_ollama(self.path.replace("/ollama", ""), "GET")
            return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/ollama/"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else b""
            self._proxy_ollama(self.path.replace("/ollama", ""), "POST", body)
            return
        super().do_POST()

    def _proxy_ollama(self, path, method, body=None):
        url = OLLAMA_BASE + path
        try:
            req = urllib.request.Request(url, data=body, method=method)
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        pass

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
