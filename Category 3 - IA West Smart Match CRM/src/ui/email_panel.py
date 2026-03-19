"""Email preview panel for the Matches tab.

Renders a generated outreach email with copy-to-clipboard and download
support, triggered when the user clicks "Generate Email" on a match card.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.outreach.email_gen import (
    event_value,
    generate_outreach_email,
)


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
            email = generate_outreach_email(speaker, event, match_scores)

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
