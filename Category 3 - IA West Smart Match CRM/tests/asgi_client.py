"""Minimal in-process ASGI request helper for boundary tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from src.api.main import app


@dataclass
class AsgiResponse:
    status_code: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> Any:
        if not self.body:
            return None
        return json.loads(self.body.decode("utf-8"))

    @property
    def text(self) -> str:
        return self.body.decode("utf-8")


async def request(
    method: str,
    path: str,
    *,
    query: dict[str, Any] | None = None,
    json_body: Any = None,
    headers: dict[str, str] | None = None,
) -> AsgiResponse:
    payload = b""
    encoded_headers: list[tuple[bytes, bytes]] = [(b"host", b"testserver")]

    if json_body is not None:
        payload = json.dumps(json_body).encode("utf-8")
        encoded_headers.append((b"content-type", b"application/json"))

    if headers:
        encoded_headers.extend(
            (key.lower().encode("utf-8"), value.encode("utf-8"))
            for key, value in headers.items()
        )

    query_string = urlencode(query or {}, doseq=True).encode("utf-8")
    messages: list[dict[str, Any]] = []
    delivered = False

    async def receive() -> dict[str, Any]:
        nonlocal delivered
        if delivered:
            return {"type": "http.disconnect"}
        delivered = True
        return {"type": "http.request", "body": payload, "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method.upper(),
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": query_string,
        "root_path": "",
        "headers": encoded_headers,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }

    await app(scope, receive, send)

    start = next(message for message in messages if message["type"] == "http.response.start")
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    response_headers = {
        key.decode("utf-8"): value.decode("utf-8")
        for key, value in start.get("headers", [])
    }
    return AsgiResponse(
        status_code=int(start["status"]),
        headers=response_headers,
        body=body,
    )
