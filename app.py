"""Local-only HTTP adapter for the synthetic workflow."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from domain import Workflow


ROOT = Path(__file__).parent / "static"
WORKFLOW = Workflow()
MAX_BODY_BYTES = 1024


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format_string, *args):
        # Demo requests may contain user-entered data; do not log them.
        pass

    def _send(self, status, body, content_type):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(encoded)

    def _json(self, status, data):
        self._send(status, json.dumps(data), "application/json; charset=utf-8")

    def _host_ok(self):
        host = self.headers.get("Host", "")
        return host in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

    def do_GET(self):
        if not self._host_ok():
            return self._json(400, {"error": "invalid_host"})
        files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/app.js": ("app.js", "application/javascript; charset=utf-8"),
            "/styles.css": ("styles.css", "text/css; charset=utf-8")
        }
        if self.path == "/api/state":
            return self._json(200, {"cases": WORKFLOW.state(), "mode": "synthetic_only"})
        if self.path not in files:
            return self._json(404, {"error": "not_found"})
        filename, content_type = files[self.path]
        return self._send(200, (ROOT / filename).read_text(encoding="utf-8"), content_type)

    def do_POST(self):
        if not self._host_ok():
            return self._json(400, {"error": "invalid_host"})
        origin = self.headers.get("Origin")
        if origin and origin not in {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}:
            return self._json(403, {"error": "invalid_origin"})
        if self.headers.get("Content-Type", "").split(";", 1)[0].lower() != "application/json":
            return self._json(415, {"error": "json_required"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY_BYTES:
                return self._json(413, {"error": "invalid_body_size"})
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("JSON object required")
            if self.path == "/api/reset":
                WORKFLOW.reset()
                state = WORKFLOW.state()
            elif self.path == "/api/check-in":
                state = WORKFLOW.send_mock_check_in(data.get("case_id"))
            elif self.path == "/api/reply":
                state = WORKFLOW.submit_reply(data.get("case_id"), data.get("reply_key"))
            elif self.path == "/api/acknowledge":
                state = WORKFLOW.acknowledge(data.get("case_id"))
            else:
                return self._json(404, {"error": "not_found"})
            return self._json(200, {"cases": state, "mode": "synthetic_only"})
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            return self._json(400, {"error": str(error)})


def main():
    server = HTTPServer(("127.0.0.1", 8765), Handler)
    print("Synthetic workflow ready at http://127.0.0.1:8765")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
