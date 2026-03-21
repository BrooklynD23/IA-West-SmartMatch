#!/usr/bin/env python3
"""Minimal local backend service for CAT3 frontend integration testing."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def _build_handler() -> type[BaseHTTPRequestHandler]:
    class DevBackendHandler(BaseHTTPRequestHandler):
        def _write_json(self, payload: dict, status_code: int = 200) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - stdlib signature
            if self.path == "/health":
                self._write_json({"status": "ok", "service": "cat3-dev-backend"})
                return
            if self.path == "/":
                self._write_json(
                    {
                        "message": "CAT3 dev backend is running.",
                        "health": "/health",
                    }
                )
                return
            self._write_json({"error": "Not found", "path": self.path}, status_code=404)

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            # Keep console output concise during local dev runs.
            return

    return DevBackendHandler


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CAT3 local dev backend.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), _build_handler())
    print(f"[dev-backend] Running on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("[dev-backend] Stopped.", flush=True)


if __name__ == "__main__":
    main()
