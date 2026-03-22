"""
Volunteer Dashboard View (A3.3)

Speaker-centric complement to the event-centric Matches tab.
Select a board member -> see their top-5 events, utilization rate,
and a mini bar chart of engagement metrics.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List

from src.config import FACTOR_KEYS, FACTOR_SHORT_LABELS


# Simulated downstream metrics (percentages applied to matched count)
CONVERSION_RATES: Dict[str, float] = {
    "matched":  1.00,   # 100% of top-5 are "matched"
    "accepted": 0.60,   # 60% acceptance rate (target KPI)
    "attended": 0.75,   # 75% of accepted attend (target KPI)
}


def _resolve_match_columns(match_results: pd.DataFrame) -> tuple[str, str]:
    """Resolve speaker and event identifier columns across tolerated schemas."""
    speaker_col = "speaker_id" if "speaker_id" in match_results.columns else "speaker_name"
    event_col = "event_id" if "event_id" in match_results.columns else "event_name"
    return speaker_col, event_col


def compute_speaker_matches(
    speaker_name: str,
    match_results: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:
    """Filter match results to a specific speaker and return top-N by score.

    Args:
        speaker_name: Name of the board member.
        match_results: DataFrame with columns:
            [event_id, speaker_id, total_score, topic_relevance,
             role_fit, geographic_proximity, calendar_fit,
             historical_conversion, student_interest]
        top_n: Number of top events to return.

    Returns:
        DataFrame of top-N matched events for this speaker, sorted descending.
    """
    speaker_col, _ = _resolve_match_columns(match_results)
    speaker_matches = match_results[
        match_results[speaker_col] == speaker_name
    ].copy()
    speaker_matches = speaker_matches.sort_values(
        "total_score", ascending=False
    ).head(top_n)
    return speaker_matches


def compute_utilization_metrics(
    speaker_name: str,
    match_results: pd.DataFrame,
    total_events: int,
    feedback_log: List[Dict],
) -> Dict:
    """Calculate utilization metrics for a speaker.

    Returns:
        Dictionary with keys: events_available, events_matched,
        events_accepted, events_attended, utilization_rate, avg_match_score.
    """
    speaker_col, event_col = _resolve_match_columns(match_results)
    speaker_matches = match_results[
        match_results[speaker_col] == speaker_name
    ]

    # Count times this speaker appears in top-3 matches for any event
    top3_count = 0
    for event_id in match_results[event_col].unique():
        event_matches = match_results[
            match_results[event_col] == event_id
        ].nlargest(3, "total_score")
        if speaker_name in event_matches[speaker_col].values:
            top3_count += 1

    # Check feedback log for real accept/decline data
    accepted_from_feedback = sum(
        1 for f in feedback_log
        if f.get("speaker_id") == speaker_name
        and f.get("decision") == "accept"
    )
    # If no feedback data, simulate using conversion rates
    events_accepted = (
        accepted_from_feedback
        if accepted_from_feedback > 0
        else int(top3_count * CONVERSION_RATES["accepted"])
    )
    events_attended = int(events_accepted * CONVERSION_RATES["attended"])

    avg_score = (
        speaker_matches["total_score"].mean()
        if not speaker_matches.empty else 0.0
    )

    return {
        "events_available": total_events,
        "events_matched": top3_count,
        "events_accepted": events_accepted,
        "events_attended": events_attended,
        "utilization_rate": (
            top3_count / total_events if total_events > 0 else 0.0
        ),
        "avg_match_score": round(avg_score, 3),
    }


def render_utilization_bar_chart(
    metrics: Dict, speaker_name: str
) -> go.Figure:
    """Mini bar chart showing Matched, Accepted, Attended counts."""
    categories = ["Matched", "Accepted", "Attended"]
    values = [
        metrics["events_matched"],
        metrics["events_accepted"],
        metrics["events_attended"],
    ]
    colors = ["#2563EB", "#059669", "#7C3AED"]

    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=values,
            textposition="auto",
            textfont=dict(size=14, color="white"),
        )
    ])

    fig.update_layout(
        title=dict(
            text=f"{speaker_name} -- Engagement Funnel",
            font=dict(size=14, color="#1E3A5F"),
        ),
        xaxis_title=None,
        yaxis_title="Events",
        yaxis=dict(
            dtick=1,
            range=[0, max(values) + 2] if values else [0, 2],
        ),
        height=300,
        margin=dict(l=40, r=20, t=40, b=30),
        plot_bgcolor="#F9FAFB",
    )

    return fig


def render_volunteer_dashboard(
    speakers_df: pd.DataFrame,
    match_results: pd.DataFrame,
    events_df: pd.DataFrame,
    feedback_log: List[Dict],
) -> None:
    """Render the full volunteer dashboard view.

    Called as a tab or section in the Streamlit app.
    """
    st.subheader("Volunteer Dashboard")
    st.caption(
        "Speaker-centric view: select a board member to see their "
        "top matched events and utilization metrics."
    )

    # Speaker selector
    speaker_names = sorted(speakers_df["Name"].unique().tolist())
    selected_speaker = st.selectbox(
        "Select Board Member:",
        speaker_names,
        key="volunteer_dashboard_speaker",
    )

    if not selected_speaker:
        return

    # Compute metrics
    total_events = len(events_df)
    metrics = compute_utilization_metrics(
        selected_speaker, match_results, total_events, feedback_log
    )

    # Metric cards row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Events Matched", metrics["events_matched"])
    col2.metric("Events Accepted", metrics["events_accepted"])
    col3.metric("Events Attended", metrics["events_attended"])
    col4.metric(
        "Utilization Rate",
        f"{metrics['utilization_rate']:.0%}",
    )

    # Average match score
    st.metric("Avg Match Score", f"{metrics['avg_match_score']:.1%}")

    # Mini bar chart
    chart = render_utilization_bar_chart(metrics, selected_speaker)
    st.plotly_chart(chart, use_container_width=True)

    # Top-5 matched events table
    st.markdown("---")
    st.markdown(f"**Top 5 Event Matches for {selected_speaker}:**")

    top_matches = compute_speaker_matches(
        selected_speaker, match_results, top_n=5
    )

    if top_matches.empty:
        st.info("No matches found for this speaker.")
        return

    for idx, row in top_matches.iterrows():
        with st.expander(
            f"{row.get('event_id', row.get('event_name', 'Event'))} -- Score: {row['total_score']:.0%}",
            expanded=(idx == top_matches.index[0]),
        ):
            _display_factors = list(FACTOR_KEYS)[:3]  # Show top 3 factors in compact view
            factor_cols = st.columns(len(_display_factors))
            for _col, _fk in zip(factor_cols, _display_factors):
                _col.metric(
                    FACTOR_SHORT_LABELS[_fk],
                    f"{row.get(_fk, 0):.0%}",
                )
