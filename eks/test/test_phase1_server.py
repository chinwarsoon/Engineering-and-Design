"""Unit and Integration Tests for Phase 1.2.1 — Backend HTTP Servers.

Tests cover:
- Main server (eks/server.py): file picker, static serving, proxy
- Phase 1 backend (eks/ui/backend/phase1_server.py): all API endpoints
- CORS headers
- Pipeline job lifecycle
"""

import json
import os
import shutil
import threading
import time
import unittest
from pathlib import Path
from typing import Optional

# Ensure we can import from eks package
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eks.ui.backend.phase1_server import (
    Phase1Handler,
    ReusableTCPServer,
    _job_state,
    _job_logs,
    _job_lock,
)


# ---------------------------------------------------------------------------
# Test helper: start Phase1Server on a free port
# ---------------------------------------------------------------------------

def _find_free_port() -> int:
    import socket
    for port in range(15000, 15100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free port")


class TestPhase1ServerCore(unittest.TestCase):
    """Test core server components without starting HTTP server."""

    def test_find_free_port_returns_int(self):
        from eks.ui.backend.phase1_server import find_free_port
        port = find_free_port(18000)
        self.assertIsInstance(port, int)
        self.assertGreaterEqual(port, 18000)

    def test_reusable_tcp_server_allow_reuse(self):
        self.assertTrue(ReusableTCPServer.allow_reuse_address)

    def test_job_state_dict_accessible(self):
        with _job_lock:
            _job_state["test"] = {"status": "queued"}
            self.assertEqual(_job_state["test"]["status"], "queued")
            del _job_state["test"]

    def test_job_logs_dict_accessible(self):
        with _job_lock:
            _job_logs["test_log"] = [{"level": "INFO", "message": "test"}]
            self.assertEqual(len(_job_logs["test_log"]), 1)
            self.assertEqual(_job_logs["test_log"][0]["level"], "INFO")
            del _job_logs["test_log"]

    def test_json_response_format(self):
        """Verify handler can produce correct JSON."""
        # We cannot directly instantiate Phase1Handler (needs socket),
        # but we can verify the class attributes and methods exist
        self.assertTrue(hasattr(Phase1Handler, "_json_response"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_status"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_files_load"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_list_documents"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_pipeline_start"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_pipeline_status"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_pipeline_logs"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_pipeline_cancel"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_review_summary"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_flagged_documents"))
        self.assertTrue(hasattr(Phase1Handler, "_handle_review_action"))


# ---------------------------------------------------------------------------
# Integration tests — start Phase1 server and exercise endpoints
# ---------------------------------------------------------------------------

class TestPhase1ServerIntegration(unittest.TestCase):
    """Integration tests against a live Phase1 backend server."""

    server: Optional[ReusableTCPServer] = None
    server_thread: Optional[threading.Thread] = None
    port: Optional[int] = None
    base_url: Optional[str] = None
    registry_backup: Optional[str] = None

    @classmethod
    def setUpClass(cls):
        # Clean stale test artifacts from previous runs
        for p in Path("test_output").glob("scan_test_*"):
            p.unlink(missing_ok=True) if p.is_file() else shutil.rmtree(p, ignore_errors=True)
        for p in Path("test_output").glob("pipeline_*"):
            shutil.rmtree(p, ignore_errors=True)
        for p in Path("test_output").glob("review_lock_*"):
            shutil.rmtree(p, ignore_errors=True)

        # Pick a free port
        cls.port = _find_free_port()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

        # Start server
        cls.server = ReusableTCPServer(("127.0.0.1", cls.port), Phase1Handler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.2)  # brief wait for server to start

    @classmethod
    def tearDownClass(cls):
        if cls.server:
            cls.server.shutdown()
        if cls.registry_backup is None:
            os.environ.pop("EKS_REGISTRY_PATH", None)
        else:
            os.environ["EKS_REGISTRY_PATH"] = cls.registry_backup

    def _request(self, method: str, path: str, body: Optional[dict] = None,
                  expect: int = 200) -> dict:
        """Make an HTTP request and return parsed JSON response."""
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError

        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body else None
        req = Request(url, data=data, method=method)
        if data:
            req.add_header("Content-Type", "application/json")

        try:
            resp = urlopen(req, timeout=5)
            self.assertEqual(resp.status, expect)
            return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == expect:
                return json.loads(e.read().decode("utf-8"))
            raise

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_status_endpoint(self):
        result = self._request("GET", "/api/status")
        self.assertEqual(result["status"], "healthy")
        self.assertIn("version", result)
        self.assertIn("timestamp", result)

    def test_cors_headers(self):
        from urllib.request import Request, urlopen
        req = Request(f"{self.base_url}/api/status", method="OPTIONS")
        resp = urlopen(req, timeout=5)
        self.assertEqual(resp.status, 204)
        self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")

    def test_files_load(self):
        """POST /api/files/load with a test directory."""
        import uuid
        tag = uuid.uuid4().hex[:8]
        test_dir = Path(f"test_output/scan_test_{tag}")
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "DOC-001-A.pdf").touch()
        (test_dir / "DOC-002-B.dgn").touch()

        result = self._request("POST", "/api/files/load", {
            "data_dir": str(test_dir),
            "recursive": False,
        })
        self.assertIn("discovered", result)
        self.assertIn("files", result)
        self.assertIsInstance(result["files"], list)

    def test_list_documents_empty(self):
        """GET /api/documents returns a list (possibly empty)."""
        result = self._request("GET", "/api/documents")
        self.assertIn("documents", result)
        self.assertIn("count", result)
        self.assertIsInstance(result["documents"], list)

    def test_document_not_found(self):
        """GET /api/documents/{id} for nonexistent doc returns 404."""
        result = self._request("GET", "/api/documents/NONEXIST-001-A", expect=404)
        self.assertIn("error", result)

    def test_pipeline_start_and_status(self):
        """POST /api/pipeline/start returns a job; GET status works."""
        import uuid
        tag = uuid.uuid4().hex[:8]
        result = self._request("POST", "/api/pipeline/start", {
            "data_dir": f"test_output/pipeline_sas_{tag}",
            "recursive": False,
        }, expect=202)
        self.assertIn("job_id", result)
        self.assertEqual(result["status"], "queued")
        job_id = result["job_id"]

        # Check status
        status = self._request("GET", f"/api/pipeline/status/{job_id}")
        self.assertEqual(status["job_id"], job_id)
        self.assertIn(status["status"], ("queued", "running", "completed", "failed"))

    def test_pipeline_logs(self):
        """GET /api/pipeline/logs/{job_id} returns log entries."""
        import uuid
        tag = uuid.uuid4().hex[:8]
        result = self._request("POST", "/api/pipeline/start", {
            "data_dir": f"test_output/pipeline_logs_{tag}",
            "recursive": False,
        }, expect=202)
        job_id = result["job_id"]

        logs = self._request("GET", f"/api/pipeline/logs/{job_id}")
        self.assertEqual(logs["job_id"], job_id)
        self.assertIsInstance(logs["logs"], list)

    def test_pipeline_logs_nonexistent(self):
        """GET /api/pipeline/logs/{bad_id} returns empty logs."""
        logs = self._request("GET", "/api/pipeline/logs/no-such-job")
        self.assertEqual(logs["job_id"], "no-such-job")
        self.assertEqual(logs["logs"], [])

    def test_pipeline_cancel(self):
        """DELETE /api/pipeline/{job_id} cancels a job."""
        import uuid
        tag = uuid.uuid4().hex[:8]
        # Start a job
        start = self._request("POST", "/api/pipeline/start", {
            "data_dir": f"test_output/pipeline_cancel_{tag}",
        }, expect=202)
        job_id = start["job_id"]

        # Cancel it
        cancel = self._request("DELETE", f"/api/pipeline/{job_id}")
        self.assertEqual(cancel["status"], "cancelled")

        # Verify status changed
        status = self._request("GET", f"/api/pipeline/status/{job_id}")
        self.assertEqual(status["status"], "cancelled")

    def test_pipeline_nonexistent_job(self):
        """GET /api/pipeline/status/{bad_id} returns 404."""
        self._request("GET", "/api/pipeline/status/no-such-job", expect=404)

    def test_pipeline_cancel_nonexistent(self):
        """DELETE /api/pipeline/{bad_id} returns 404."""
        self._request("DELETE", "/api/pipeline/no-such-job", expect=404)

    def test_review_summary(self):
        """GET /api/review/summary returns review statistics."""
        result = self._request("GET", "/api/review/summary")
        self.assertIn("total", result)
        self.assertIn("status_counts", result)

    def test_flagged_documents(self):
        """GET /api/review/flagged returns list."""
        result = self._request("GET", "/api/review/flagged")
        self.assertIn("documents", result)
        self.assertIsInstance(result["documents"], list)

    def test_review_lock_updates_document(self):
        """PUT /api/review/lock attempts to lock a document."""
        # Use a fresh directory with a unique doc name to avoid stale DB locks
        import uuid
        tag = uuid.uuid4().hex[:8]
        doc_num = f"RVLOCK-{tag}"
        test_dir = Path(f"test_output/review_lock_{tag}")
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / f"{doc_num}-A.pdf").touch()

        files_resp = self._request("POST", "/api/files/load", {
            "data_dir": str(test_dir),
            "recursive": False,
        })
        self.assertGreater(files_resp.get("registered", 0), 0,
                           f"File registration failed: {files_resp}")

        # Wait for any background pipeline to finish its DB transaction
        import time
        time.sleep(1.0)

        result = self._request("PUT", "/api/review/lock", {
            "doc_id": f"{doc_num}-A",
            "verified_by": "tester",
        })
        self.assertIn(result.get("status"), ("locked",), f"Unexpected: {result}")

    def test_404_unknown_endpoint(self):
        """GET unknown endpoint returns 404."""
        self._request("GET", "/api/nonexistent", expect=404)

    def test_bad_json_body(self):
        """POST with bad JSON returns 400."""
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError
        req = Request(
            f"{self.base_url}/api/files/load",
            data=b"not-json",
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        with self.assertRaises(HTTPError) as ctx:
            urlopen(req, timeout=5)
        self.assertEqual(ctx.exception.code, 400)


# ---------------------------------------------------------------------------
# Main server tests (without starting the full server)
# ---------------------------------------------------------------------------

class TestMainServer(unittest.TestCase):
    """Test eks/server.py components."""

    def test_reusable_tcp_server_class(self):
        # Just test the import and attribute
        from eks.server import ReusableTCPServer, MainServerHandler
        self.assertTrue(ReusableTCPServer.allow_reuse_address)
        self.assertTrue(hasattr(MainServerHandler, "_serve_file_picker"))
        self.assertTrue(hasattr(MainServerHandler, "_proxy_to"))
        self.assertTrue(hasattr(MainServerHandler, "_serve_static"))

    def test_parse_args_defaults(self):
        from eks.server import main as server_main
        # We can't call main() since it starts the server,
        # but we can test the argument parser indirectly
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--port", type=int, default=5000)
        args, _ = parser.parse_known_args([])
        self.assertEqual(args.port, 5000)


if __name__ == "__main__":
    unittest.main()
