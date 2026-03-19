"""
Matches tab UI component for IA SmartMatch CRM.
"""

import logging

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.config import DEFAULT_WEIGHTS
from src.matching.engine import rank_speakers_for_course, rank_speakers_for_event
from src.matching.explanations import (
    fallback_match_explanation,
    generate_match_explanation,
    load_cached_explanation,
)
from src.utils import format_course_display_name, format_course_identifier

logger = logging.getLogger(__name__)


def render_matches_tab(
    events: pd.DataFrame,
    courses: pd.DataFrame,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    event_embeddings: dict[str, np.ndarray],
    course_embeddings: dict[str, np.ndarray],
    ia_event_calendar: pd.DataFrame,
) -> None:
    """Render the Matches tab in the Streamlit app."""
    _render_weight_sliders()

    view_mode = st.sidebar.radio(
        "View Mode",
        options=["Events", "Courses"],
        index=0,
        key="matches_view_mode",
    )

    if view_mode == "Events":
        _render_event_matches(
            events, speakers, speaker_embeddings, event_embeddings,
            ia_event_calendar,
        )
    else:
        _render_course_matches(
            courses, speakers, speaker_embeddings, course_embeddings,
            ia_event_calendar,
        )


def _render_weight_sliders() -> None:
    """Render 6 weight-tuning sliders in the sidebar."""
    st.sidebar.markdown("### Match Weights")
    st.sidebar.caption("Adjust weights to change ranking priorities. Weights are normalized automatically.")

    factor_labels = {
        "topic_relevance": "Topic Relevance",
        "role_fit": "Role Fit",
        "geographic_proximity": "Geographic Proximity",
        "calendar_fit": "Calendar Fit",
        "historical_conversion": "Historical Conversion",
        "student_interest": "Student Interest",
    }

    if "match_weights" not in st.session_state:
        st.session_state["match_weights"] = dict(DEFAULT_WEIGHTS)

    for factor_key, label in factor_labels.items():
        current_val = st.session_state["match_weights"].get(
            factor_key, DEFAULT_WEIGHTS[factor_key]
        )
        new_val = st.sidebar.slider(
            label,
            min_value=0.0,
            max_value=1.0,
            value=current_val,
            step=0.05,
            key=f"slider_{factor_key}",
        )
        st.session_state["match_weights"][factor_key] = new_val

    w = st.session_state["match_weights"]
    total = sum(w.values())
    if total > 0:
        st.sidebar.markdown("---")
        st.sidebar.caption("Normalized weights:")
        for k, v in w.items():
            normalized = v / total
            st.sidebar.text(f"  {factor_labels[k]}: {normalized:.0%}")
    else:
        st.sidebar.warning("All weights are zero. Scores will be 0.0.")

    if st.sidebar.button("Reset to Defaults", key="reset_weights"):
        st.session_state["match_weights"] = dict(DEFAULT_WEIGHTS)
        st.rerun()


def _render_event_matches(
    events: pd.DataFrame,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    event_embeddings: dict[str, np.ndarray],
    ia_event_calendar: pd.DataFrame,
) -> None:
    """Render event-based matching view."""
    event_names = events["Event / Program"].tolist()
    selected_event_name = st.selectbox(
        "Select an Event",
        options=event_names,
        index=0,
        key="selected_event",
    )

    selected_event = events[
        events["Event / Program"] == selected_event_name
    ].iloc[0]

    st.markdown(f"### Top 3 Matches for: *{selected_event_name}*")

    weights = st.session_state.get("match_weights", DEFAULT_WEIGHTS)
    event_emb = event_embeddings.get(selected_event_name, None)

    top_matches = rank_speakers_for_event(
        event_row=selected_event,
        speakers_df=speakers,
        speaker_embeddings=speaker_embeddings,
        event_embedding=event_emb,
        ia_event_calendar=ia_event_calendar,
        weights=weights,
        top_n=3,
    )

    for match in top_matches:
        _render_match_card(match=match, event=selected_event)


def _render_course_matches(
    courses: pd.DataFrame,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    course_embeddings: dict[str, np.ndarray],
    ia_event_calendar: pd.DataFrame,
) -> None:
    """Render course-based matching view (guest lectures)."""
    show_high = st.sidebar.checkbox("High-fit courses", value=True, key="filter_high")
    show_medium = st.sidebar.checkbox("Medium-fit courses", value=False, key="filter_medium")

    fit_values = []
    if show_high:
        fit_values.append("High")
    if show_medium:
        fit_values.append("Medium")

    if not fit_values:
        st.info("Select at least one course fit level in the sidebar.")
        return

    filtered_courses = courses[courses["Guest Lecture Fit"].isin(fit_values)]
    st.markdown(f"**{len(filtered_courses)} courses** matching filter criteria")

    course_labels = [
        (
            f"{format_course_display_name(row['Course'], row.get('Section'), row['Title'])} "
            f"({row['Guest Lecture Fit']})"
        )
        for _, row in filtered_courses.iterrows()
    ]
    if not course_labels:
        st.info("No courses match the selected filters.")
        return

    selected_label = st.selectbox(
        "Select a Course Section",
        options=course_labels,
        index=0,
        key="selected_course",
    )

    selected_idx = course_labels.index(selected_label)
    selected_course = filtered_courses.iloc[selected_idx]

    course_key = format_course_identifier(
        selected_course.get("Course"),
        selected_course.get("Section"),
    )
    st.markdown(f"### Top 3 Guest Lecture Matches: *{selected_label}*")

    weights = st.session_state.get("match_weights", DEFAULT_WEIGHTS)
    course_emb = course_embeddings.get(course_key, None)

    top_matches = rank_speakers_for_course(
        course_row=selected_course,
        speakers_df=speakers,
        speaker_embeddings=speaker_embeddings,
        course_embedding=course_emb,
        ia_event_calendar=ia_event_calendar,
        weights=weights,
        top_n=3,
    )

    for match in top_matches:
        _render_match_card(
            match=match,
            event=pd.Series({
                "Category": "",
                "Volunteer Roles (fit)": "Guest speaker",
                "Primary Audience": "Students",
            }),
        )


def _render_match_card(
    match: dict,
    event: pd.Series,
) -> None:
    """Render a single match card with radar chart and on-demand explanation."""
    score_pct = f"{match['total_score']:.0%}"
    rank = match["rank"]

    with st.container():
        st.markdown("---")

        col_rank, col_info, col_score = st.columns([1, 6, 2])
        with col_rank:
            st.markdown(f"### #{rank}")
        with col_info:
            st.markdown(f"**{match['speaker_name']}**")
            st.caption(
                f"{match['speaker_title']} | {match['speaker_company']}  \n"
                f"{match['speaker_metro_region']} | {match['speaker_board_role']}"
            )
        with col_score:
            st.metric(label="Match Score", value=score_pct)

        col_chart, col_explain = st.columns([1, 1])

        with col_chart:
            fig = _create_radar_chart(match["factor_scores"])
            st.plotly_chart(fig, use_container_width=True, key=f"radar_{rank}_{match['speaker_name']}")

        with col_explain:
            _render_match_explanation(match=match, event=event)

        col_email, col_ics, col_spacer = st.columns([2, 2, 4])
        with col_email:
            st.button(
                "Generate Email",
                key=f"email_{rank}_{match['speaker_name']}",
                on_click=lambda m=match: st.session_state.update(
                    {"pending_email_match": m}
                ),
            )
        with col_ics:
            st.button(
                "Generate .ics",
                key=f"ics_{rank}_{match['speaker_name']}",
                disabled=True,
            )


def _render_match_explanation(match: dict, event: pd.Series) -> None:
    """Render an explanation without blocking slider reruns on new API calls."""
    event_category = str(event.get("Category", ""))
    event_volunteer_roles = str(event.get("Volunteer Roles (fit)", ""))
    event_audience = str(event.get("Primary Audience", ""))

    cached_explanation = load_cached_explanation(
        match,
        event_category=event_category,
        event_volunteer_roles=event_volunteer_roles,
        event_audience=event_audience,
    )
    explanation = cached_explanation or fallback_match_explanation(match)
    button_label = "Refresh AI Explanation" if cached_explanation else "Generate AI Explanation"
    button_key = f"explain::{match.get('speaker_name', '')}::{match.get('event_name', '')}"

    if st.button(button_label, key=button_key):
        with st.spinner("Generating AI explanation..."):
            explanation = generate_match_explanation(
                match_result=match,
                event_category=event_category,
                event_volunteer_roles=event_volunteer_roles,
                event_audience=event_audience,
            )

    st.markdown("**Why this match?**")
    st.caption("AI wording is generated on demand to keep weight tuning responsive.")
    st.info(explanation)


def _create_radar_chart(factor_scores: dict[str, float]) -> go.Figure:
    """Create a Plotly radar chart for the 6 match factors."""
    factor_order = [
        "topic_relevance",
        "role_fit",
        "geographic_proximity",
        "calendar_fit",
        "historical_conversion",
        "student_interest",
    ]
    display_labels = [
        "Topic",
        "Role Fit",
        "Proximity",
        "Calendar",
        "History",
        "Student Int.",
    ]

    values = [factor_scores.get(f, 0.0) for f in factor_order]
    values_closed = values + [values[0]]
    labels_closed = display_labels + [display_labels[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(49, 130, 189, 0.3)",
        line=dict(color="rgba(49, 130, 189, 1.0)", width=2),
        marker=dict(size=6, color="rgba(49, 130, 189, 1.0)"),
        name="Match Factors",
        hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickvals=[0.0, 0.25, 0.50, 0.75, 1.0],
                ticktext=["0", "0.25", "0.50", "0.75", "1.0"],
                tickfont=dict(size=9),
            ),
            angularaxis=dict(
                tickfont=dict(size=11),
            ),
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=280,
    )

    return fig
