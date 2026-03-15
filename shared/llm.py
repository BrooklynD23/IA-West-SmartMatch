"""
shared/llm.py — Lightweight LLM client wrapper.

Usage (copy or import from category src/):
    from shared.llm import call_llm
    response = call_llm(prompt="Summarise this: ...", system="You are a helpful assistant.")
"""
from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _client() -> OpenAI:
    base_url = os.getenv("OPENROUTER_BASE_URL")
    api_key = os.getenv("OPENROUTER_API_KEY") if base_url else os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("No API key found. Set OPENAI_API_KEY or OPENROUTER_API_KEY in .env")
    return OpenAI(api_key=api_key, base_url=base_url)


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
        model: Model ID (defaults to LLM_MODEL env var or gpt-4o-mini).
        temperature: Sampling temperature.
        max_tokens: Max tokens in response.

    Returns:
        Response text string.
    """
    resolved_model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
    client = _client()

    completion = client.chat.completions.create(
        model=resolved_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return completion.choices[0].message.content or ""
