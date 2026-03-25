"""Match Engine Dashboard page for IA SmartMatch.

Renders the Internal Specialist Matches view using native Streamlit
widgets with numeric score badges by default and an optional Plotly
radar chart for the detailed factor breakdown.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.ui.data_helpers import (
    get_initials,
    get_top_specialists_for_event,
    load_pipeline_data,
    load_poc_contacts,
    load_specialists,
)
from src.ui.page_router import navigate_to, set_user_role


# Factor score simulation per card position (0-100 scale for display)
_FACTOR_SCORES: list[dict[str, int]] = [
    {"Topic": 98, "Role": 95, "Proximity": 90, "Calendar": 85, "History": 100, "Impact": 96},
    {"Topic": 92, "Role": 98, "Proximity": 75, "Calendar": 90, "History": 94, "Impact": 88},
    {"Topic": 95, "Role": 85, "Proximity": 92, "Calendar": 78, "History": 100, "Impact": 90},
]


def render_match_engine_page() -> None:
    """Render the Match Engine dashboard using native Streamlit widgets.

    Shows specialist cards with numeric score badges by default and
    an expandable Plotly radar chart for the detailed factor breakdown.
    """
    # ── Load Data ────────────────────────────────────────────────────────────
    specialists = load_specialists()
    pipeline = load_pipeline_data()
    pocs = load_poc_contacts()

    # ── Select Featured Event ──────────────────────────────────────────────
    featured_event = "CPP Career Center \u2014 Career Fairs"
    top_matches = get_top_specialists_for_event(featured_event, 3)

    if not top_matches and pipeline:
        events = list({row["event_name"] for row in pipeline if row.get("event_name")})
        if events:
            featured_event = events[0]
            top_matches = get_top_specialists_for_event(featured_event, 3)

    match_count = len(
        [r for r in pipeline if r.get("event_name") == featured_event]
    ) or len(pipeline)

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(f"## {featured_event}")
    hc1, hc2 = st.columns([3, 1])
    with hc1:
        st.caption("April 28, 2026 · Scraped Event")
    with hc2:
        st.caption(f"{match_count} Matches Found")

    # ── Specialist Cards ─────────────────────────────────────────────────────
    st.markdown("### Internal Specialist Matches")

    if not top_matches:
        st.info(
            "No ranked specialists available yet. Open the Matches workspace "
            "to generate a shortlist."
        )
    else:
        for idx, spec in enumerate(top_matches):
            name = spec.get("name", "Specialist")
            title = spec.get("title", "")
            company = spec.get("company", "")
            initials = spec.get("initials") or get_initials(name)
            try:
                score_pct = round(float(spec.get("match_score", 0)) * 100)
            except (ValueError, TypeError):
                score_pct = 80
            title_company = f"{title}" + (f", {company}" if company else "")
            tags = spec.get("expertise_tags", "")

            st.markdown("---")
            sc1, sc2, sc3 = st.columns([1, 4, 2])
            with sc1:
                st.markdown(f"### #{idx + 1}")
            with sc2:
                st.markdown(f"**{name}**")
                st.caption(title_company)
                if tags:
                    st.caption(f"Expertise: {tags[:120]}")
            with sc3:
                st.metric("Match Score", f"{score_pct}%")

            # Extended factor breakdown via expander
            factor_scores = _FACTOR_SCORES[idx % len(_FACTOR_SCORES)]
            with st.expander("Show factor breakdown", expanded=False):
                fc1, fc2 = st.columns([1, 1])
                with fc1:
                    for factor, value in factor_scores.items():
                        st.caption(f"{factor}: **{value / 10:.1f}** / 10")
                with fc2:
                    fig = _create_factor_radar(factor_scores)
                    st.plotly_chart(fig, use_container_width=True, key=f"radar_me_{idx}")

            bc1, bc2 = st.columns([1, 1])
            with bc1:
                st.button("Select", key=f"select_spec_{idx}", type="primary")
            with bc2:
                st.button("Initiate Outreach", key=f"outreach_spec_{idx}")

    # ── POC & Event Intelligence sidebar info ──────────────────────────────
    st.markdown("---")
    st.markdown("### Event Intelligence")
    ei1, ei2 = st.columns([1, 1])
    with ei1:
        if pocs:
            poc = pocs[0]
            st.markdown(f"**Primary POC:** {poc.get('name', 'N/A')}")
            st.caption(f"{poc.get('role', '')} — {poc.get('org', '')}")
        else:
            st.caption("No POC contacts available.")
    with ei2:
        event_short = featured_event.replace("\u2014", "-").replace("CPP ", "")
        st.markdown("**AI Reasoning**")
        st.caption(
            f'Prioritize candidates with "CPP" tags. Historic data shows higher '
            f"acceptance rate for local speakers at {event_short}."
        )

    # ── Navigation ───────────────────────────────────────────────────────────
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("< Back to Dashboard", use_container_width=True):
            navigate_to("dashboard")
    with col2:
        if st.button("Sign Out", use_container_width=True):
            set_user_role(None)
            navigate_to("landing", role=None, demo=False)


# ── Helpers ─────────────────────────────────────────────────────────────────


def _create_factor_radar(factor_scores: dict[str, int]) -> go.Figure:
    """Create a Plotly radar chart for the 6 match factors."""
    labels = list(factor_scores.keys())
    values = [v / 100 for v in factor_scores.values()]
    values_closed = values + [values[0]]
    labels_closed = labels + [labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(49, 130, 189, 0.3)",
        line=dict(color="rgba(49, 130, 189, 1.0)", width=2),
        marker=dict(size=6, color="rgba(49, 130, 189, 1.0)"),
        hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=250,
    )
    return fig
