"""Email preview panel for the Matches tab.

Renders a generated outreach email with copy-to-clipboard and download
support, triggered when the user clicks "Generate Email" on a match card.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.demo_mode import demo_or_live
from src.outreach.email_gen import (
    event_value,
    generate_outreach_email,
)
from src.runtime_state import init_runtime_state


def _normalize_email_payload(email: dict[str, Any]) -> dict[str, str]:
    """Normalize live and demo email payloads into the UI contract."""
    if "subject_line" in email and "full_email" in email:
        return {
            "subject_line": str(email.get("subject_line", "")),
            "greeting": str(email.get("greeting", "")),
            "body": str(email.get("body", "")),
            "closing": str(email.get("closing", "")),
            "full_email": str(email.get("full_email", "")),
        }

    body = str(email.get("body", ""))
    return {
        "subject_line": str(email.get("subject", "")),
        "greeting": "",
        "body": body,
        "closing": "",
        "full_email": body,
    }


def _record_email_generation(speaker: dict[str, Any], event: dict[str, Any]) -> None:
    """Track generated emails once per speaker-event pair for pipeline metrics."""
    init_runtime_state()
    event_name = event_value(event, "Event / Program", "event_name", default="event")
    email_key = f"{speaker.get('Name', '')}::{event_name}"
    generated_email_keys = st.session_state.get("generated_email_keys", [])
    if email_key not in generated_email_keys:
        st.session_state["generated_email_keys"] = [*generated_email_keys, email_key]
        st.session_state["emails_generated"] = len(st.session_state["generated_email_keys"])


def render_email_preview(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, Any],
) -> None:
    """Render the email preview panel within the Matches tab.

    Called when user clicks "Generate Email" on a match card.
    """
    with st.expander("Outreach Email Preview", expanded=True):
        with st.spinner("Generating personalized email..."):
            payload = demo_or_live(
                generate_outreach_email,
                speaker,
                event,
                match_scores,
                fixture_key="email_generation",
                voice="ia_west_chapter",
            )
            email = _normalize_email_payload(payload)
        _record_email_generation(speaker, event)

        st.markdown(f"**Subject:** {email['subject_line']}")
        st.divider()

        st.markdown(email["full_email"])

        st.divider()

        # Copy to clipboard via st.code (allows easy select-all + copy)
        st.caption("Click inside the box below and use Ctrl+A, Ctrl+C to copy:")
        st.code(email["full_email"], language=None)

        # Download as .txt
        speaker_name = speaker.get("Name", "speaker")
        event_name = event_value(
            event, "Event / Program", "event_name", default="event",
        )
        st.download_button(
            label="Download Email as .txt",
            data=email["full_email"],
            file_name=f"outreach_{speaker_name}_{event_name}.txt",
            mime="text/plain",
        )

        # Dismiss button
        if st.button("Close Preview", key="close_email_preview"):
            st.session_state.pop("pending_email_match", None)
            st.rerun()
