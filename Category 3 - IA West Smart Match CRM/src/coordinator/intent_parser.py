"""Gemini-powered intent parser for coordinator commands.

Pure Python — no Streamlit imports. Fully testable in isolation.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from src.config import GEMINI_API_KEY, GEMINI_TEXT_MODEL
from src.gemini_client import GeminiAPIError, generate_text

logger = logging.getLogger(__name__)

SUPPORTED_INTENTS: frozenset[str] = frozenset({
    "discover_events",
    "rank_speakers",
    "generate_outreach",
    "check_contacts",
    "prepare_campaign",
    "unknown",
})

ACTION_REGISTRY: list[dict[str, str]] = [
    {"intent": "discover_events",   "agent": "Discovery Agent",       "description": "Scrape universities for new events"},
    {"intent": "rank_speakers",     "agent": "Matching Agent",        "description": "Rank speakers for a target event"},
    {"intent": "generate_outreach", "agent": "Outreach Agent",        "description": "Draft outreach emails for a match"},
    {"intent": "check_contacts",    "agent": "Contacts Agent",        "description": "Review POC contact status"},
    {"intent": "prepare_campaign",  "agent": "Campaign Orchestrator", "description": "Discover events + rank speakers + generate outreach (parallel)"},
]

MULTI_STEP_INTENTS: dict[str, list[str]] = {
    "prepare_campaign": ["discover_events", "rank_speakers", "generate_outreach"],
}

_SYSTEM_PROMPT = """\
You are Jarvis, an AI coordinator assistant. Given a coordinator command and a list
of available agent actions, identify the best matching intent and return ONLY valid JSON.

Available actions:
{actions}

Response format (JSON only, no markdown):
{{
  "intent": "<one of the intent keys above, or 'unknown'>",
  "agent": "<agent display name>",
  "params": {{}},
  "reasoning": "<one sentence explaining why>"
}}

If the command asks to "prepare", "launch campaign", or "full outreach", use "prepare_campaign" intent.
"""


@dataclass(frozen=True)
class ParsedIntent:
    """Immutable result of intent parsing.

    Carries all fields needed to construct an ActionProposal.
    """

    intent: str
    agent: str
    params: dict[str, Any]
    reasoning: str
    raw_text: str


def _strip_markdown_fence(text: str) -> str:
    """Remove triple-backtick fences that Gemini occasionally adds."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        return "\n".join(inner).strip()
    return stripped


_KEYWORD_PATTERNS: list[tuple[list[str], str]] = [
    (["find event", "discover event", "scrape", "new event", "find new"],
     "discover_events"),
    (["rank speaker", "match speaker", "best speaker", "rank specialist",
      "who should", "top speaker"],
     "rank_speakers"),
    (["outreach", "email", "draft email", "send email", "generate email",
      "write email"],
     "generate_outreach"),
    (["contact", "poc", "follow up", "check contact"],
     "check_contacts"),
    (["campaign", "full outreach", "prepare campaign", "launch campaign"],
     "prepare_campaign"),
]


def _keyword_fallback(text: str) -> ParsedIntent | None:
    """Simple keyword-based intent matching for offline / demo mode.

    Returns None if no keyword pattern matches.
    """
    lower = text.lower()
    for keywords, intent in _KEYWORD_PATTERNS:
        if any(kw in lower for kw in keywords):
            entry = next(
                (a for a in ACTION_REGISTRY if a["intent"] == intent),
                None,
            )
            return ParsedIntent(
                intent=intent,
                agent=entry["agent"] if entry else "Jarvis",
                params={},
                reasoning=f"Matched keyword in: {text!r}",
                raw_text=text,
            )
    return None


def parse_intent(text: str) -> ParsedIntent:
    """Parse coordinator text into a structured intent. Never raises.

    Uses Gemini LLM when an API key is available; falls back to keyword
    matching for offline / demo operation.
    """
    # Try LLM parsing when API key is configured
    if GEMINI_API_KEY and GEMINI_API_KEY != "AIza...":
        actions_str = json.dumps(ACTION_REGISTRY, indent=2)
        system = _SYSTEM_PROMPT.format(actions=actions_str)
        try:
            raw = generate_text(
                messages=[{"role": "user", "content": text}],
                api_key=GEMINI_API_KEY,
                model=GEMINI_TEXT_MODEL,
                system_instruction=system,
                temperature=0.1,
                max_output_tokens=300,
                timeout=10.0,
            )
            cleaned = _strip_markdown_fence(raw)
            data = json.loads(cleaned)
            intent = data.get("intent", "unknown")
            if intent not in SUPPORTED_INTENTS:
                intent = "unknown"
            return ParsedIntent(
                intent=intent,
                agent=data.get("agent", "Jarvis"),
                params=data.get("params", {}),
                reasoning=data.get("reasoning", ""),
                raw_text=text,
            )
        except (GeminiAPIError, json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("LLM intent parsing failed, trying keyword fallback: %s", exc)

    # Keyword fallback for offline / demo mode
    fallback = _keyword_fallback(text)
    if fallback is not None:
        return fallback

    return ParsedIntent(
        intent="unknown",
        agent="Jarvis",
        params={},
        reasoning="",
        raw_text=text,
    )
