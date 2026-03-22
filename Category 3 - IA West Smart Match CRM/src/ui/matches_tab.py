"""
Matches tab UI component for IA SmartMatch CRM.
"""

import logging

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.config import DEFAULT_WEIGHTS, FACTOR_DISPLAY_LABELS, FACTOR_KEYS, FACTOR_SHORT_LABELS
from src.demo_mode import demo_or_live
from src.matching.engine import rank_speakers_for_course, rank_speakers_for_event
from src.matching.explanations import (
    fallback_match_explanation,
    generate_match_explanation,
    load_cached_explanation,
)
from src.feedback.acceptance import render_feedback_buttons
from src.outreach.ics_generator import ICS_CONTENT_TYPE, generate_ics
from src.runtime_state import (
    get_matching_events_df,
    init_runtime_state,
    set_match_results,
)
from src.ui.email_panel import render_email_preview
from src.utils import format_course_display_name, format_course_identifier

logger = logging.getLogger(__name__)


def _event_option_id(event_row: pd.Series) -> str:
    """Return the stable ID used to select an event."""
    return str(event_row.get("event_id", "") or event_row.get("Event / Program", ""))


def _event_option_label(event_row: pd.Series) -> str:
    """Return a label that disambiguates same-named events."""
    event_name = str(event_row.get("Event / Program", "Event"))
    host_unit = str(event_row.get("Host / Unit", "") or "").strip()
    event_date = str(
        event_row.get("Date", event_row.get("Recurrence (typical)", "")) or ""
    ).strip()
    details = " | ".join(part for part in [host_unit, event_date] if part)
    return f"{event_name} ({details})" if details else event_name


def validate_weights(weights: dict[str, float]) -> str | None:
    """Return an error message when weights are invalid for scoring."""
    total = sum(float(value) for value in weights.values())
    if total <= 0:
        return "At least one weight must be greater than 0. Please adjust weights."
    return None


@st.cache_data(show_spinner=False)
def _cached_generate_ics(
    event_name: str,
    date_str: str | None = None,
    location: str | None = None,
    description: str | None = None,
) -> str:
    """Cache-wrapped .ics generation to avoid recomputation on every rerender."""
    return generate_ics(
        event_name=event_name,
        date_str=date_str,
        location=location,
        description=description,
    )


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
    init_runtime_state()
    available_events = get_matching_events_df(events)
    weight_error = _render_weight_sliders()
    if weight_error:
        st.error(weight_error)
        return

    view_mode = st.sidebar.radio(
        "View Mode",
        options=["Events", "Courses"],
        index=0,
        key="matches_view_mode",
    )

    if view_mode == "Events":
        _render_event_matches(
            available_events, speakers, speaker_embeddings, event_embeddings,
            ia_event_calendar,
        )
    else:
        _render_course_matches(
            courses, speakers, speaker_embeddings, course_embeddings,
            ia_event_calendar,
        )


def _render_weight_sliders() -> str | None:
    """Render 6 weight-tuning sliders in the sidebar."""
    st.sidebar.markdown("### Match Weights")
    st.sidebar.caption("Adjust weights to change ranking priorities. Weights are normalized automatically.")

    factor_labels = FACTOR_DISPLAY_LABELS

    if "match_weights" not in st.session_state:
        st.session_state["match_weights"] = dict(DEFAULT_WEIGHTS)

    updated_weights: dict[str, float] = {}
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
        updated_weights[factor_key] = new_val
    st.session_state["match_weights"] = updated_weights

    w = st.session_state["match_weights"]
    weight_error = validate_weights(w)
    total = sum(w.values())
    if weight_error is None:
        st.sidebar.markdown("---")
        st.sidebar.caption("Normalized weights:")
        for k, v in w.items():
            normalized = v / total
            st.sidebar.text(f"  {factor_labels[k]}: {normalized:.0%}")
    else:
        st.sidebar.error(weight_error)

    if st.sidebar.button("Reset to Defaults", key="reset_weights"):
        st.session_state["match_weights"] = dict(DEFAULT_WEIGHTS)
        st.rerun()

    return weight_error


def _render_event_matches(
    events: pd.DataFrame,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    event_embeddings: dict[str, np.ndarray],
    ia_event_calendar: pd.DataFrame,
) -> None:
    """Render event-based matching view."""
    event_options = {
        _event_option_id(row): _event_option_label(row)
        for _, row in events.iterrows()
    }
    selected_event_id = st.selectbox(
        "Select an Event",
        options=list(event_options),
        format_func=lambda option: event_options[option],
        index=0,
        key="selected_event",
    )

    selected_event = events[events.apply(_event_option_id, axis=1) == selected_event_id].iloc[0]
    selected_event_name = str(selected_event.get("Event / Program", selected_event_id))

    st.markdown(f"### Top 3 Matches for: *{selected_event_name}*")

    weights = st.session_state.get("match_weights", DEFAULT_WEIGHTS)
    event_emb = event_embeddings.get(selected_event_name)
    if event_emb is None:
        event_emb = event_embeddings.get(selected_event_id)

    top_matches = rank_speakers_for_event(
        event_row=selected_event,
        speakers_df=speakers,
        speaker_embeddings=speaker_embeddings,
        event_embedding=event_emb,
        ia_event_calendar=ia_event_calendar,
        weights=weights,
        top_n=3,
    )
    set_match_results(top_matches)

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
    set_match_results(top_matches)

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
            st.plotly_chart(fig, use_container_width=True, key=f"radar_{rank}")

        with col_explain:
            _render_match_explanation(match=match, event=event)

        col_email, col_ics, col_spacer = st.columns([2, 2, 4])
        with col_email:
            st.button(
                "Generate Email",
                key=f"email_{rank}",
                on_click=lambda m=match: st.session_state.update(
                    {"pending_email_match": m}
                ),
            )
        with col_ics:
            _event_name = match.get("event_name", "Event")
            _event_date = event.get("IA Event Date", event.get(
                "Date", event.get("date_or_recurrence"),
            ))
            _event_location = event.get("Host / Unit", event.get("university"))
            _event_desc = (
                f"{_event_name} — Speaker: {match.get('speaker_name', '')}"
            )
            _ics_content = _cached_generate_ics(
                event_name=_event_name,
                date_str=str(_event_date) if _event_date is not None else None,
                location=str(_event_location) if _event_location is not None else None,
                description=_event_desc,
            )
            _safe_name = _event_name.replace(" ", "_")
            st.download_button(
                label="Download .ics",
                data=_ics_content,
                file_name=f"{_safe_name}.ics",
                mime=ICS_CONTENT_TYPE,
                key=f"ics_{rank}",
            )

        # --- Feedback buttons ---
        _event_id = match.get("event_id") or match.get("event_name", "Event")
        render_feedback_buttons(
            event_id=_event_id,
            speaker_id=match.get("speaker_name", ""),
            match_score=match.get("total_score", 0.0),
            factor_scores=match.get("factor_scores", {}),
        )

        # --- Email preview panel ---
        pending = st.session_state.get("pending_email_match")
        if pending and pending.get("speaker_name") == match.get("speaker_name"):
            speaker_dict = {
                "Name": match.get("speaker_name", ""),
                "Title": match.get("speaker_title", ""),
                "Company": match.get("speaker_company", ""),
                "Board Role": match.get("speaker_board_role", ""),
                "Metro Region": match.get("speaker_metro_region", ""),
                "Expertise Tags": match.get("speaker_expertise_tags", ""),
            }
            event_dict = event.to_dict() if hasattr(event, "to_dict") else dict(event)
            render_email_preview(speaker_dict, event_dict, match)


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
    button_key = f"explain_{match.get('rank', '')}"

    if st.button(button_label, key=button_key):
        with st.spinner("Generating AI explanation..."):
            payload = demo_or_live(
                generate_match_explanation,
                match_result=match,
                event_category=event_category,
                event_volunteer_roles=event_volunteer_roles,
                event_audience=event_audience,
                fixture_key="match_explanations",
            )
            if isinstance(payload, dict):
                explanation = str(payload.get("explanation", explanation))
            else:
                explanation = str(payload)

    st.markdown("**Why this match?**")
    st.caption("AI wording is generated on demand to keep weight tuning responsive.")
    st.info(explanation)


def _create_radar_chart(factor_scores: dict[str, float]) -> go.Figure:
    """Create a Plotly radar chart for the 6 match factors."""
    factor_order = list(FACTOR_KEYS)
    display_labels = [FACTOR_SHORT_LABELS[k] for k in FACTOR_KEYS]

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
