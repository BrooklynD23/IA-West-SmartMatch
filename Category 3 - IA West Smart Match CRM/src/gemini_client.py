"""Minimal Gemini API helpers used by the Category 3 runtime.

The implementation uses the Gemini REST API directly so the project does not
depend on a provider-specific SDK at runtime.
"""

from __future__ import annotations

import json
import socket
from typing import Any
from urllib import error, request

from src.config import GEMINI_BASE_URL


class GeminiAPIError(RuntimeError):
    """Raised when the Gemini API request fails."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable


def _post_json(
    endpoint: str,
    payload: dict[str, Any],
    api_key: str,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """POST JSON to a Gemini REST endpoint and return the parsed response."""
    if not api_key:
        raise GeminiAPIError("GEMINI_API_KEY is not configured")

    url = f"{GEMINI_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    request_body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        message = body or str(exc.reason)
        raise GeminiAPIError(
            f"HTTP {exc.code} calling {endpoint}: {message}",
            status_code=exc.code,
            retryable=exc.code == 429 or exc.code >= 500,
        ) from exc
    except (error.URLError, socket.timeout, TimeoutError) as exc:
        raise GeminiAPIError(
            f"Gemini request failed for {endpoint}: {exc}",
            retryable=True,
        ) from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GeminiAPIError(
            f"Gemini returned invalid JSON for {endpoint}",
        ) from exc


def batch_embed_texts(
    texts: list[str],
    *,
    api_key: str,
    model: str,
    output_dimensionality: int,
    batch_size: int = 20,
    task_type: str = "SEMANTIC_SIMILARITY",
    timeout: float = 30.0,
) -> list[list[float]]:
    """Generate embeddings for texts using Gemini's batch embedding endpoint."""
    embeddings: list[list[float]] = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        payload = {
            "requests": [
                {
                    "model": f"models/{model}",
                    "content": {"parts": [{"text": text}]},
                    "taskType": task_type,
                    "outputDimensionality": output_dimensionality,
                }
                for text in batch
            ],
        }
        response = _post_json(
            f"models/{model}:batchEmbedContents",
            payload,
            api_key,
            timeout=timeout,
        )
        batch_embeddings = response.get("embeddings", [])
        if len(batch_embeddings) != len(batch):
            raise GeminiAPIError(
                f"Gemini embedding response size mismatch for {model}: "
                f"expected {len(batch)}, got {len(batch_embeddings)}"
            )

        for embedding in batch_embeddings:
            values = embedding.get("values")
            if not isinstance(values, list):
                raise GeminiAPIError("Gemini embedding response missing values")
            embeddings.append(values)

    return embeddings


def _extract_text(response: dict[str, Any]) -> str:
    """Extract the first text candidate from a Gemini response payload."""
    candidates = response.get("candidates") or []
    if not candidates:
        return ""

    first_candidate = candidates[0] if isinstance(candidates[0], dict) else {}
    content = first_candidate.get("content") if isinstance(first_candidate, dict) else {}
    parts = content.get("parts") if isinstance(content, dict) else []
    texts = [
        part.get("text", "")
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ]
    return "".join(texts).strip()


def generate_text(
    messages: list[dict[str, str]],
    *,
    api_key: str,
    model: str,
    system_instruction: str = "",
    temperature: float = 0.7,
    max_output_tokens: int = 2000,
    timeout: float = 30.0,
) -> str:
    """Generate a text completion from Gemini using chat-style messages."""
    contents: list[dict[str, Any]] = []
    for message in messages:
        role = str(message.get("role", "user"))
        content = str(message.get("content", "")).strip()
        if not content or role == "system":
            continue
        contents.append(
            {
                "role": "model" if role == "assistant" else "user",
                "parts": [{"text": content}],
            }
        )

    payload: dict[str, Any] = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        },
    }
    if system_instruction.strip():
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    response = _post_json(
        f"models/{model}:generateContent",
        payload,
        api_key,
        timeout=timeout,
    )
    return _extract_text(response)
