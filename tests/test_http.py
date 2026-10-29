import io
import json
import unittest
from types import SimpleNamespace

from app import Handler, WORKFLOW


def call(method, path, payload=None, extra_headers=None):
    body = json.dumps(payload).encode("utf-8") if payload is not None else b""
    handler = object.__new__(Handler)
    handler.server = SimpleNamespace(server_port=8765)
    handler.path = path
    handler.headers = {"Host": "127.0.0.1:8765", "Content-Type": "application/json", "Content-Length": str(len(body))}
    handler.headers.update(extra_headers or {})
    handler.rfile = io.BytesIO(body)
    handler.wfile = io.BytesIO()
    response = {}
    handler.send_response = lambda status: response.update(status=status)
    handler.send_header = lambda key, value: None
    handler.end_headers = lambda: None
    getattr(handler, f"do_{method}")()
    return response["status"], json.loads(handler.wfile.getvalue())


class HttpTests(unittest.TestCase):
    def setUp(self):
        WORKFLOW.reset()

    def test_state_is_synthetic(self):
        status, data = call("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(data["mode"], "synthetic_only")

    def test_cross_origin_write_rejected(self):
        status, data = call("POST", "/api/reset", {}, {"Origin": "https://example.invalid"})
        self.assertEqual(status, 403)
        self.assertEqual(data["error"], "invalid_origin")

    def test_mock_workflow_over_http_handler(self):
        status, data = call("POST", "/api/check-in", {"case_id": "case-a"})
        self.assertEqual(status, 200)
        self.assertEqual(data["cases"]["case-a"]["status"], "awaiting_reply")
        status, data = call("POST", "/api/reply", {"case_id": "case-a", "reply_key": "urgent"})
        self.assertEqual(status, 200)
        self.assertEqual(data["cases"]["case-a"]["alert"], "open")


if __name__ == "__main__":
    unittest.main()
