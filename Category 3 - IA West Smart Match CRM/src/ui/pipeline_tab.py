"""Pipeline funnel visualization tab for IA SmartMatch CRM."""

import logging
from collections import OrderedDict
from pathlib import Path
from typing import Final

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.config import DATA_DIR

logger = logging.getLogger(__name__)

# Ordered mapping: stage name -> minimum stage_order value that qualifies.
# "Discovered" is synthetic (all rows count); remaining stages use
# cumulative filtering: a row at stage_order >= N counts for that stage.
FUNNEL_STAGES: Final[OrderedDict[str, int]] = OrderedDict([
    ("Discovered", -1),       # all rows
    ("Matched", 0),           # stage_order >= 0
    ("Contacted", 1),         # stage_order >= 1
    ("Confirmed", 2),         # stage_order >= 2
    ("Attended", 3),          # stage_order >= 3
    ("Member Inquiry", 4),    # stage_order >= 4
])

PIPELINE_CSV: Final[str] = "pipeline_sample_data.csv"


def load_pipeline_data(csv_path: str | None = None) -> pd.DataFrame:
    """Load pipeline data from CSV, returning an empty DataFrame on error."""
    path = Path(csv_path) if csv_path else DATA_DIR / PIPELINE_CSV
    try:
        df = pd.read_csv(path)
        return df
    except (FileNotFoundError, pd.errors.ParserError, pd.errors.EmptyDataError, OSError) as exc:
        logger.warning("Could not load pipeline data from %s: %s", path, exc)
        return pd.DataFrame(
            columns=["event_name", "speaker_name", "match_score", "rank", "stage", "stage_order"]
        )


def aggregate_funnel_stages(df: pd.DataFrame) -> OrderedDict[str, int]:
    """Aggregate row counts for each funnel stage (cumulative, monotonically decreasing).

    Every row is "Discovered". A row with stage_order >= N counts toward
    stage N and all stages below N.
    """
    result: OrderedDict[str, int] = OrderedDict()
    for stage_name, min_order in FUNNEL_STAGES.items():
        if stage_name == "Discovered":
            result[stage_name] = len(df)
        else:
            if df.empty or "stage_order" not in df.columns:
                result[stage_name] = 0
            else:
                result[stage_name] = int((df["stage_order"] >= min_order).sum())
    return result


def _build_hover_text(df: pd.DataFrame, stage_name: str, min_order: int) -> str:
    """Build a hover tooltip listing speaker/event pairs for a funnel stage."""
    if df.empty or "stage_order" not in df.columns:
        return "No data"
    if stage_name == "Discovered":
        subset = df
    else:
        subset = df[df["stage_order"] >= min_order]
    if subset.empty:
        return "No records"
    lines: list[str] = []
    for _, row in subset.head(8).iterrows():
        speaker = row.get("speaker_name", "Unknown")
        event = row.get("event_name", "Unknown")
        lines.append(f"{speaker} — {event}")
    if len(subset) > 8:
        lines.append(f"... and {len(subset) - 8} more")
    return "<br>".join(lines)


def create_funnel_chart(
    df: pd.DataFrame,
    stage_counts: OrderedDict[str, int],
) -> go.Figure:
    """Create a Plotly Funnel chart for the engagement pipeline."""
    stage_names = list(stage_counts.keys())
    counts = list(stage_counts.values())

    hover_texts = [
        _build_hover_text(df, name, FUNNEL_STAGES[name])
        for name in stage_names
    ]

    fig = go.Figure()
    fig.add_trace(go.Funnel(
        y=stage_names,
        x=counts,
        text=[str(c) for c in counts],
        textposition="inside",
        hovertext=hover_texts,
        hoverinfo="text+name",
        marker=dict(
            color=[
                "#3182bd", "#6baed6", "#9ecae1",
                "#c6dbef", "#e6550d", "#fd8d3c",
            ],
        ),
        connector=dict(line=dict(color="royalblue", width=1)),
    ))

    fig.update_layout(
        title="Engagement Pipeline Funnel",
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        height=420,
    )

    return fig


def render_pipeline_tab(datasets: object) -> None:
    """Render the Pipeline tab with engagement funnel tracking."""
    st.header("Engagement Pipeline")

    df = load_pipeline_data()
    stage_counts = aggregate_funnel_stages(df)
    fig = create_funnel_chart(df, stage_counts)

    st.plotly_chart(fig, use_container_width=True, key="pipeline_funnel")

    st.subheader("Pipeline Data")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No pipeline data available. Place pipeline_sample_data.csv in the data/ directory.")
