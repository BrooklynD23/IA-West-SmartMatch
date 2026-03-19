"""shared/llm.py - Lightweight Gemini client wrapper.

Usage:
    from shared.llm import call_llm
    response = call_llm(prompt="Summarise this: ...", system="You are a helpful assistant.")
"""
from __future__ import annotations

import json
import os
import socket
from typing import Optional
from urllib import error, request

from dotenv import load_dotenv

load_dotenv()


def _post_json(endpoint: str, payload: dict, api_key: str, timeout: float = 30.0) -> dict:
    base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise EnvironmentError(f"HTTP {exc.code} calling Gemini API: {body}") from exc
    except (error.URLError, socket.timeout, TimeoutError) as exc:
        raise EnvironmentError(f"Gemini API request failed: {exc}") from exc


def _extract_text(response: dict) -> str:
    candidates = response.get("candidates") or []
    if not candidates:
        return ""
    first = candidates[0] if isinstance(candidates[0], dict) else {}
    content = first.get("content", {}) if isinstance(first, dict) else {}
    parts = content.get("parts", []) if isinstance(content, dict) else []
    return "".join(
        part.get("text", "")
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ).strip()


def call_llm(
    prompt: str,
    system: str = "You are a helpful assistant.",
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """
    Send a single prompt to the LLM and return the text response.

    Args:
        prompt: User message.
        system: System prompt / persona.
        model: Model ID (defaults to GEMINI_TEXT_MODEL env var or gemini-2.5-flash-lite).
        temperature: Sampling temperature.
        max_tokens: Max tokens in response.

    Returns:
        Response text string.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("No API key found. Set GEMINI_API_KEY in .env")
    resolved_model = model or os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash-lite")

    response = _post_json(
        f"models/{resolved_model}:generateContent",
        {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        },
        api_key,
    )
    return _extract_text(response)
