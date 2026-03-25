"""Coordinator Dashboard page for IA SmartMatch.

Renders the Institutional Dashboard using native Streamlit widgets
(st.metric, st.columns, st.plotly_chart) instead of an iframe-rendered
HTML template.  Data loading is unchanged from the original implementation.
"""

from __future__ import annotations

import streamlit as st

from src.ui.expansion_map import render_coordinator_density_map
from src.ui.data_helpers import (
    get_initials,
    get_recent_poc_activity,
    get_top_specialists_for_event,
    load_pipeline_data,
    load_poc_contacts,
    load_specialists,
)
from src.ui.page_router import navigate_to, set_user_role


def render_coordinator_dashboard(speakers_df=None) -> None:
    """Render the full Coordinator Institutional Dashboard page.

    Uses native Streamlit widgets for all primary navigation and metrics
    so that every CTA is a real interactive control rather than static
    HTML markup inside an iframe.
    """
    # ── Load Data ────────────────────────────────────────────────────────────
    specialists = load_specialists()
    pocs = load_poc_contacts()
    pipeline = load_pipeline_data()
    activity = get_recent_poc_activity(5)

    # ── Compute Metrics ──────────────────────────────────────────────────────
    unique_events = list({row["event_name"] for row in pipeline if row.get("event_name")})
    scraped_events_count = len(unique_events)
    poc_count = len(pocs)
    volunteer_pct = 88  # Demo value matching mockup

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown("## Institutional Dashboard")
    st.caption(
        "Monitoring West Coast Campus Event Density & Volunteer Alignment."
    )

    # ── Metrics Row ──────────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Scraped Events Today", scraped_events_count, "+12%")
    with m2:
        st.metric("New POC Found", poc_count)
    with m3:
        st.metric("Volunteer Availability", f"{volunteer_pct}%")

    # ── Main Layout: Map + Matches | Live Feed ───────────────────────────────
    col_main, col_feed = st.columns([2, 1])

    with col_main:
        # ── Campus Coverage Map ──────────────────────────────────────────────
        st.markdown("### Campus Coverage Map")
        st.caption(
            "Plotly coverage uses campus hubs and synthetic density "
            "shading for reachability context."
        )
        if speakers_df is not None:
            figure, unmapped_metros = render_coordinator_density_map(speakers_df)
            st.plotly_chart(
                figure,
                use_container_width=True,
                config={"displayModeBar": False},
                key="coordinator_density_map",
            )
            if unmapped_metros:
                st.warning(
                    "Some speaker metros are not mapped yet and were excluded "
                    "from the coverage map: "
                    + ", ".join(sorted(unmapped_metros))
                )
        else:
            st.info(
                "Coverage map is unavailable — speaker data was not provided."
            )

        # ── Active High-Priority Matches ─────────────────────────────────────
        st.markdown("### Active High-Priority Matches")

        event_top_scores: dict[str, float] = {}
        for row in pipeline:
            event = row.get("event_name", "")
            try:
                score = float(row.get("match_score", 0))
            except (ValueError, TypeError):
                score = 0.0
            if event not in event_top_scores or score > event_top_scores[event]:
                event_top_scores[event] = score

        top_events = sorted(event_top_scores.items(), key=lambda x: -x[1])[:4]

        for event_name, top_score in top_events:
            alignment_pct = round(top_score * 100)
            top_specs = get_top_specialists_for_event(event_name, 3)
            institution = _derive_institution(event_name)
            spec_names = ", ".join(s.get("name", "?") for s in top_specs[:3])

            with st.container():
                ec1, ec2, ec3 = st.columns([4, 2, 2])
                with ec1:
                    st.markdown(f"**{event_name}**")
                    st.caption(f"{institution} · {spec_names or 'No matches yet'}")
                with ec2:
                    st.metric("Alignment", f"{alignment_pct}% Fit", label_visibility="collapsed")
                with ec3:
                    if st.button("Assign", key=f"assign_{event_name}"):
                        navigate_to("matches")

        if st.button("View Pipeline →", key="view_pipeline_link"):
            navigate_to("pipeline")

    # ── Right Column: Live Discovery Feed ────────────────────────────────────
    with col_feed:
        st.markdown("### Live Discovery Feed")

        if activity:
            for idx, item in enumerate(activity[:3]):
                poc_name = item.get("poc_name", "Unknown")
                org = item.get("org", "")
                comm_type = item.get("type", "email").title()
                time_label = ["Just Now", "14 Minutes Ago", "1 Hour Ago"][min(idx, 2)]
                st.markdown(f"**{time_label}**")
                st.markdown(f"POC Activity: **{poc_name}**")
                st.caption(f"{org} · {comm_type} logged")
                if idx == 0:
                    if st.button("Connect now", key="connect_now_feed"):
                        navigate_to("discovery")
                st.divider()

        # Static feed items matching demo content
        _static_feed = [
            ("2 Hours Ago", "New Event Scraped: AI Research Forum",
             "Caltech, Pasadena · Detected via RSS/Academic Calendar"),
            ("3 Hours Ago", "Data Refresh Complete",
             "Oregon State University calendar sync successful. 18 new entries."),
            ("4 Hours Ago", "Volunteer Alert: Availability Shift",
             "Mark Thompson (Regional Lead) updated status to 'Active'."),
            ("Yesterday", "Monthly Summary Generated",
             "Academic engagement is up 22% in the Southern California region."),
        ]
        for time_label, title, detail in _static_feed:
            st.markdown(f"**{time_label}**")
            st.markdown(title)
            st.caption(detail)
            st.divider()

    # ── Navigation Buttons ───────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("View Match Engine", type="primary", use_container_width=True):
            navigate_to("match_engine")
    with col2:
        if st.button("Sign Out", use_container_width=True):
            set_user_role(None)
            navigate_to("landing", role=None, demo=False)


# ── Helper ────────────────────────────────────────────────────────────────────

def _derive_institution(event_name: str) -> str:
    """Derive a short institution label from an event name string."""
    lower = event_name.lower()
    if "cpp" in lower or "cal poly" in lower or "bronco" in lower:
        return "Cal Poly Pomona"
    if "ucla" in lower:
        return "UCLA"
    if "stanford" in lower:
        return "Stanford University"
    if "ucsd" in lower or "san diego" in lower:
        return "UC San Diego"
    if "swift" in lower:
        return "SWIFT Consortium"
    if "our" in lower or "rsca" in lower or "cars" in lower:
        return "Cal Poly Pomona OUR"
    return "West Coast Campus"
