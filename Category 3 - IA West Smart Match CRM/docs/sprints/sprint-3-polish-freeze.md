---
doc_role: canonical
authority_scope:
- category.3.sprint.3
canonical_upstreams:
- Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md
- PRD_SECTION_CAT3.md
- archived/general_project_docs/MASTER_SPRINT_PLAN.md
- archived/general_project_docs/STRATEGIC_REVIEW.md
last_reconciled: '2026-03-18'
managed_by: planning-agent
---

# Sprint 3: Polish, Integration, Feature Freeze -- "Lock and Load"

**Duration:** Days 9-10
**Track:** Both (A + B)
**Hours:** Track A 14-16h, Track B 12-16h

> **Governance notice:** This sprint spec implements `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md` and must remain aligned with `PRD_SECTION_CAT3.md`. `archived/general_project_docs/MASTER_SPRINT_PLAN.md` and `archived/general_project_docs/STRATEGIC_REVIEW.md` provide portfolio-level context only. `Category 3 - IA West Smart Match CRM/PLAN.md` is background.

> **FEATURE FREEZE: End of Day 9.** No new features after Day 9. Day 10 is integration + bug fixes only.

---

## Track A (Person B) -- Code Polish & Feature Completion

### A3.1: Board-to-Campus Expansion Map (3.0h)

**Goal:** Plotly geographic scatter map showing speaker metro locations, university campus locations, and connection lines representing geographic-proximity-based match potential.

**File:** `src/ui/expansion_map.py`

#### Specification

```python
"""
Board-to-Campus Expansion Map

Renders a Plotly scatter_geo figure with three layers:
1. Speaker metro locations (circles, colored by expertise cluster)
2. University campus locations (diamonds)
3. Connection lines (opacity proportional to geographic_proximity score)
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Tuple

# ---------- Coordinate Lookup Tables ----------

SPEAKER_METRO_COORDS: Dict[str, Tuple[float, float]] = {
    # (latitude, longitude) for each metro region
    "Ventura / Thousand Oaks": (34.2164, -119.0376),
    "Los Angeles — West":     (34.0259, -118.4965),
    "Los Angeles":            (34.0522, -118.2437),
    "Los Angeles — North":    (34.1808, -118.3090),
    "Los Angeles — East":     (34.0579, -117.8214),  # Pomona area
    "Los Angeles — Long Beach":(33.7701, -118.1937),
    "Orange County / Long Beach": (33.7701, -118.1937),  # alias fallback until separate OC centroid is needed
    "San Francisco":          (37.7749, -122.4194),
    "Portland":               (45.5152, -122.6784),
    "San Diego":              (32.7157, -117.1611),
    "Seattle":                (47.6062, -122.3321),
}

UNIVERSITY_COORDS: Dict[str, Tuple[float, float]] = {
    # (latitude, longitude) for each target campus
    "UCLA":                   (34.0689, -118.4452),
    "SDSU":                   (32.7757, -117.0719),
    "UC Davis":               (38.5382, -121.7617),
    "USC":                    (34.0224, -118.2851),
    "Portland State":         (45.5116, -122.6857),
    "Cal Poly Pomona":        (34.0565, -117.8215),
    # Extended targets from IA event calendar
    "CSULB":                  (33.7838, -118.1141),
    "UC San Diego":           (32.8801, -117.2340),
    "UW (Seattle)":           (47.6553, -122.3035),
    "USF":                    (37.7765, -122.4506),
    "SFSU":                   (37.7219, -122.4782),
}

# Expertise cluster color mapping (6 clusters)
EXPERTISE_CLUSTER_COLORS: Dict[str, str] = {
    "Data & Analytics":       "#2563EB",  # IA blue
    "Qualitative Research":   "#7C3AED",  # purple
    "Sales & Client Dev":     "#059669",  # green
    "Marketing & Brand":      "#D97706",  # amber
    "Operations & Events":    "#DC2626",  # red
    "Innovation & AI":        "#0891B2",  # cyan
}

# Speaker-to-cluster mapping (derived from expertise_tags in data)
SPEAKER_CLUSTERS: Dict[str, str] = {
    "Travis Miller":          "Sales & Client Dev",
    "Amanda Keller-Grill":    "Operations & Events",
    "Katrina Noelle":         "Qualitative Research",
    "Rob Kaiser":             "Innovation & AI",
    "Donna Flynn":            "Operations & Events",
    "Greg Carter":            "Qualitative Research",
    "Katie Nelson":           "Marketing & Brand",
    "Liz O'Hara":             "Innovation & AI",
    "Sean McKenna":           "Sales & Client Dev",
    "Calvin Friesth":         "Sales & Client Dev",
    "Ashley Le Blanc":        "Marketing & Brand",
    "Monica Voss":            "Data & Analytics",
    "Molly Strawn":           "Marketing & Brand",
    "Shana DeMarinis":        "Operations & Events",
    "Dr. Yufan Lin":          "Data & Analytics",
    "Adam Portner":           "Sales & Client Dev",
    "Laurie Bae":             "Operations & Events",
    "Amber Jawaid":           "Innovation & AI",
}


def compute_geographic_proximity(
    speaker_coords: Tuple[float, float],
    university_coords: Tuple[float, float],
    max_distance_miles: float = 600.0,
) -> float:
    """
    Haversine distance -> proximity score [0.0, 1.0].
    Score = max(0, 1 - (distance / max_distance_miles)).
    Anything >= max_distance_miles returns 0.0.
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 3959.0  # Earth radius in miles
    lat1, lon1 = map(radians, speaker_coords)
    lat2, lon2 = map(radians, university_coords)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return max(0.0, 1.0 - (distance / max_distance_miles))


def build_connection_data(
    speakers_df: pd.DataFrame,
    proximity_threshold: float = 0.3,
) -> List[Dict]:
    """
    Build connection lines between speakers and universities
    where geographic_proximity >= proximity_threshold.

    Returns list of dicts: {speaker, university, proximity, cluster, lats, lons}
    """
    connections = []
    for _, speaker in speakers_df.iterrows():
        metro = speaker["Metro Region"]
        name = speaker["Name"]
        if metro not in SPEAKER_METRO_COORDS:
            continue
        s_lat, s_lon = SPEAKER_METRO_COORDS[metro]
        cluster = SPEAKER_CLUSTERS.get(name, "Data & Analytics")
        for uni_name, (u_lat, u_lon) in UNIVERSITY_COORDS.items():
            prox = compute_geographic_proximity(
                (s_lat, s_lon), (u_lat, u_lon)
            )
            if prox >= proximity_threshold:
                connections.append({
                    "speaker": name,
                    "university": uni_name,
                    "proximity": round(prox, 3),
                    "cluster": cluster,
                    "lats": [s_lat, u_lat, None],
                    "lons": [s_lon, u_lon, None],
                })
    return connections


def render_expansion_map(
    speakers_df: pd.DataFrame,
    proximity_threshold: float = 0.3,
) -> go.Figure:
    """
    Render the 3-layer Plotly scatter_geo map.

    Layer 1: Speaker metro locations (circles)
    Layer 2: University locations (diamonds)
    Layer 3: Connection lines (opacity = proximity score)
    """
    fig = go.Figure()

    # --- Layer 3 (bottom): Connection lines ---
    connections = build_connection_data(speakers_df, proximity_threshold)
    for conn in connections:
        fig.add_trace(go.Scattergeo(
            lat=conn["lats"],
            lon=conn["lons"],
            mode="lines",
            line=dict(
                width=1.5,
                color=EXPERTISE_CLUSTER_COLORS.get(conn["cluster"], "#6B7280"),
            ),
            opacity=min(1.0, conn["proximity"] * 1.2),
            name=f'{conn["speaker"]} -> {conn["university"]}',
            hoverinfo="text",
            text=f'{conn["speaker"]} -> {conn["university"]}<br>'
                 f'Proximity: {conn["proximity"]:.0%}',
            showlegend=False,
        ))

    # --- Layer 1: Speaker metros ---
    added_clusters = set()
    for _, speaker in speakers_df.iterrows():
        metro = speaker["Metro Region"]
        name = speaker["Name"]
        if metro not in SPEAKER_METRO_COORDS:
            continue
        lat, lon = SPEAKER_METRO_COORDS[metro]
        cluster = SPEAKER_CLUSTERS.get(name, "Data & Analytics")
        color = EXPERTISE_CLUSTER_COLORS.get(cluster, "#6B7280")
        show_legend = cluster not in added_clusters
        added_clusters.add(cluster)
        fig.add_trace(go.Scattergeo(
            lat=[lat],
            lon=[lon],
            mode="markers+text",
            marker=dict(size=12, color=color, symbol="circle",
                        line=dict(width=1, color="white")),
            text=[name.split()[0]],  # first name only for compactness
            textposition="top center",
            textfont=dict(size=9, color=color),
            name=cluster if show_legend else None,
            legendgroup=cluster,
            showlegend=show_legend,
            hoverinfo="text",
            hovertext=f"<b>{name}</b><br>{speaker['Title']}<br>"
                      f"{speaker['Company']}<br>{metro}<br>"
                      f"Cluster: {cluster}",
        ))

    # --- Layer 2: University campuses ---
    uni_legend_shown = False
    for uni_name, (lat, lon) in UNIVERSITY_COORDS.items():
        fig.add_trace(go.Scattergeo(
            lat=[lat],
            lon=[lon],
            mode="markers+text",
            marker=dict(size=10, color="#1E3A5F", symbol="diamond",
                        line=dict(width=1.5, color="#F59E0B")),
            text=[uni_name],
            textposition="bottom center",
            textfont=dict(size=8, color="#1E3A5F"),
            name="University" if not uni_legend_shown else None,
            legendgroup="Universities",
            showlegend=not uni_legend_shown,
            hoverinfo="text",
            hovertext=f"<b>{uni_name}</b>",
        ))
        uni_legend_shown = True

    # --- Layout ---
    fig.update_layout(
        title=dict(
            text="IA West Board-to-Campus Expansion Map",
            font=dict(size=18, color="#1E3A5F"),
        ),
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="#F3F4F6",
            showlakes=True,
            lakecolor="#DBEAFE",
            showcountries=False,
            showsubunits=True,
            subunitcolor="#D1D5DB",
            lonaxis=dict(range=[-125, -115]),
            lataxis=dict(range=[31, 49]),
            center=dict(lat=38.5, lon=-120.5),
        ),
        legend=dict(
            title="Expertise Cluster",
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=0, r=0, t=50, b=80),
        height=600,
    )

    return fig
```

#### UI Wireframe

```
+------------------------------------------------------------------+
|  [Pipeline Tab]  [Expansion Tab]  [...]                          |
+------------------------------------------------------------------+
|                                                                   |
|  IA West Board-to-Campus Expansion Map                           |
|  +---------------------------------------------------------+    |
|  |                                                          |    |
|  |    * Seattle (Greg)                                      |    |
|  |       \                                                  |    |
|  |    * Portland (Katie)---<> Portland State                |    |
|  |        |                                                 |    |
|  |    * SF (Katrina, Liz, Adam, Laurie)                     |    |
|  |        |       <> UC Davis                               |    |
|  |        |                                                 |    |
|  |    * Ventura (Travis, Shana)                             |    |
|  |    * LA West (Amanda)---<> UCLA                          |    |
|  |    * LA (Donna, Calvin, Amber)---<> USC                  |    |
|  |    * LA East (Dr. Lin)---<> Cal Poly Pomona              |    |
|  |    * Long Beach (Rob)---<> CSULB                         |    |
|  |        |                                                 |    |
|  |    * San Diego (Sean, Monica)---<> SDSU  <> UC San Diego |    |
|  |                                                          |    |
|  +---------------------------------------------------------+    |
|                                                                   |
|  Proximity Threshold: [====O=========] 0.30                      |
|                                                                   |
|  Legend: * Speaker (color = cluster)  <> University               |
|  [Data & Analytics] [Qualitative] [Sales] [Marketing]            |
|  [Operations] [Innovation & AI]                                   |
|                                                                   |
|  Connection Summary:                                              |
|  - 18 speakers across 10 metro regions                            |
|  - 11 university campuses mapped                                  |
|  - XX connections above threshold (proximity >= 0.30)             |
+------------------------------------------------------------------+
```

#### Acceptance Criteria

- [ ] Map renders within 2 seconds of tab selection
- [ ] All 18 speakers plotted at correct metro coordinates (spot-check 5 speakers manually)
- [ ] All 11 university campuses plotted at correct coordinates (spot-check 3 universities manually)
- [ ] Connection lines drawn only where `geographic_proximity >= threshold` (default 0.30)
- [ ] Connection line opacity visually correlates with proximity score (higher score = more opaque)
- [ ] Speaker markers colored by expertise cluster (6 distinct colors)
- [ ] University markers use diamond symbol, distinct from speaker circles
- [ ] Hover tooltip on speaker shows: Name, Title, Company, Metro Region, Cluster
- [ ] Hover tooltip on university shows: University name
- [ ] Hover tooltip on connection line shows: Speaker name, University name, Proximity score
- [ ] Legend displays all 6 expertise clusters + "University" entry
- [ ] Map geo scope focuses on West Coast US (lat 31-49, lon -125 to -115)
- [ ] Proximity threshold slider in sidebar adjusts map in real time (range 0.0-1.0, step 0.05)
- [ ] Connection summary stats update when threshold changes

#### Harness Guidelines

- File location: `src/ui/expansion_map.py`
- Import in main app: `from src.ui.expansion_map import render_expansion_map`
- Streamlit integration: `st.plotly_chart(render_expansion_map(speakers_df, threshold), use_container_width=True)`
- Sidebar slider: `threshold = st.sidebar.slider("Proximity Threshold", 0.0, 1.0, 0.30, 0.05)`
- Must load speaker data from `data/data_speaker_profiles.csv` via shared data loader
- No external API calls required (pure computation + Plotly rendering)

#### Steer Guidelines

- This is a **cut candidate** if time runs short (third priority to cut after Volunteer Dashboard and Feedback Loop)
- If Plotly scatter_geo rendering is too slow, switch to a static `px.scatter_mapbox` with OpenStreetMap tiles (no API key needed)
- If geo scope focus does not work with `albers usa` projection, fall back to `natural earth` projection with manual center/zoom
- Connection lines may overlap heavily in the LA metro area -- consider adding a "Zoom to LA" button or using jitter offsets for dense areas

---

### A3.2: Match Acceptance Feedback Loop (3.0h)

**Goal:** Add accept/decline buttons to match cards, capture decline reasons, aggregate feedback, and suggest weight adjustments based on patterns.

**File:** `src/feedback/acceptance.py`

#### Specification

```python
"""
Match Acceptance Feedback Loop

Captures accept/decline decisions on match cards, stores in session state,
optionally persists to CSV, and generates weight adjustment suggestions
based on aggregated feedback patterns.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
import json
import os

# ---------- Data Structures ----------

DECLINE_REASONS = [
    "Too far (geographic distance)",
    "Schedule conflict",
    "Topic mismatch",
    "Speaker already committed",
    "Other",
]

@dataclass
class FeedbackEntry:
    """Single accept/decline decision."""
    timestamp: str              # ISO format
    event_id: str               # Event name or ID
    speaker_id: str             # Speaker name
    match_score: float          # Composite MATCH_SCORE at time of decision
    decision: str               # "accept" or "decline"
    decline_reason: Optional[str] = None  # One of DECLINE_REASONS
    decline_notes: Optional[str] = None   # Free-text for "Other"
    factor_scores: Dict[str, float] = field(default_factory=dict)
    # factor_scores keys: topic_relevance, role_fit, geographic_proximity,
    #                     calendar_fit, historical_conversion, student_interest


def init_feedback_state() -> None:
    """Initialize session state for feedback tracking."""
    if "feedback_log" not in st.session_state:
        st.session_state.feedback_log: List[Dict] = []
    if "feedback_decisions" not in st.session_state:
        # Quick lookup: {(event_id, speaker_id): "accept"|"decline"}
        st.session_state.feedback_decisions: Dict[tuple, str] = {}


def record_feedback(entry: FeedbackEntry) -> None:
    """
    Record a feedback decision in session state and optionally persist to CSV.
    """
    init_feedback_state()
    entry_dict = asdict(entry)
    # Convert factor_scores dict to JSON string for CSV storage
    entry_dict["factor_scores"] = json.dumps(entry_dict["factor_scores"])
    st.session_state.feedback_log.append(entry_dict)
    st.session_state.feedback_decisions[
        (entry.event_id, entry.speaker_id)
    ] = entry.decision
    # Persist to CSV
    _persist_to_csv(entry_dict)


def _persist_to_csv(entry_dict: Dict) -> None:
    """Append feedback entry to CSV file."""
    csv_path = "data/feedback_log.csv"
    df_new = pd.DataFrame([entry_dict])
    if os.path.exists(csv_path):
        df_new.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        df_new.to_csv(csv_path, index=False)


def get_decision(event_id: str, speaker_id: str) -> Optional[str]:
    """Check if a decision has already been made for this match."""
    init_feedback_state()
    return st.session_state.feedback_decisions.get(
        (event_id, speaker_id), None
    )


# ---------- Feedback UI Components ----------

def render_feedback_buttons(
    event_id: str,
    speaker_id: str,
    match_score: float,
    factor_scores: Dict[str, float],
) -> None:
    """
    Render accept/decline buttons on a match card.
    If already decided, show the decision badge instead.
    """
    init_feedback_state()
    existing = get_decision(event_id, speaker_id)
    card_key = f"fb_{event_id}_{speaker_id}".replace(" ", "_")

    if existing == "accept":
        st.success("Accepted", icon="\u2705")
        return
    elif existing == "decline":
        st.error("Declined", icon="\u274C")
        return

    col_accept, col_decline = st.columns(2)
    with col_accept:
        if st.button("Accept Match", key=f"{card_key}_accept",
                      type="primary", use_container_width=True):
            entry = FeedbackEntry(
                timestamp=datetime.now().isoformat(),
                event_id=event_id,
                speaker_id=speaker_id,
                match_score=match_score,
                decision="accept",
                factor_scores=factor_scores,
            )
            record_feedback(entry)
            st.rerun()

    with col_decline:
        if st.button("Decline Match", key=f"{card_key}_decline",
                      use_container_width=True):
            st.session_state[f"{card_key}_show_reason"] = True
            st.rerun()

    # Decline reason prompt
    if st.session_state.get(f"{card_key}_show_reason", False):
        st.markdown("**Why are you declining this match?**")
        reason = st.radio(
            "Select reason:",
            DECLINE_REASONS,
            key=f"{card_key}_reason_radio",
            label_visibility="collapsed",
        )
        notes = ""
        if reason == "Other":
            notes = st.text_input(
                "Please specify:",
                key=f"{card_key}_other_notes",
            )
        if st.button("Submit Decline", key=f"{card_key}_submit_decline"):
            entry = FeedbackEntry(
                timestamp=datetime.now().isoformat(),
                event_id=event_id,
                speaker_id=speaker_id,
                match_score=match_score,
                decision="decline",
                decline_reason=reason,
                decline_notes=notes if reason == "Other" else None,
                factor_scores=factor_scores,
            )
            record_feedback(entry)
            del st.session_state[f"{card_key}_show_reason"]
            st.rerun()


# ---------- Feedback Aggregation & Weight Suggestions ----------

def aggregate_feedback() -> Dict:
    """
    Aggregate all feedback entries into summary statistics.

    Returns:
        {
            "total": int,
            "accepted": int,
            "declined": int,
            "acceptance_rate": float,
            "decline_reasons": {reason: count},
            "avg_score_accepted": float,
            "avg_score_declined": float,
        }
    """
    init_feedback_state()
    log = st.session_state.feedback_log
    if not log:
        return {
            "total": 0, "accepted": 0, "declined": 0,
            "acceptance_rate": 0.0,
            "decline_reasons": {},
            "avg_score_accepted": 0.0,
            "avg_score_declined": 0.0,
        }

    df = pd.DataFrame(log)
    total = len(df)
    accepted = len(df[df["decision"] == "accept"])
    declined = len(df[df["decision"] == "decline"])
    acceptance_rate = accepted / total if total > 0 else 0.0

    decline_reasons = {}
    declined_df = df[df["decision"] == "decline"]
    if not declined_df.empty and "decline_reason" in declined_df.columns:
        decline_reasons = declined_df["decline_reason"].value_counts().to_dict()

    avg_accepted = (
        df[df["decision"] == "accept"]["match_score"].mean()
        if accepted > 0 else 0.0
    )
    avg_declined = (
        df[df["decision"] == "decline"]["match_score"].mean()
        if declined > 0 else 0.0
    )

    return {
        "total": total,
        "accepted": accepted,
        "declined": declined,
        "acceptance_rate": acceptance_rate,
        "decline_reasons": decline_reasons,
        "avg_score_accepted": round(avg_accepted, 3),
        "avg_score_declined": round(avg_declined, 3),
    }


# Weight factor mapping: decline reason -> scoring factor to adjust
from src.config import DEFAULT_WEIGHTS

REASON_TO_FACTOR = {
    "Too far (geographic distance)":  "geographic_proximity",
    "Schedule conflict":              "calendar_fit",
    "Topic mismatch":                 "topic_relevance",
    "Speaker already committed":      "historical_conversion",
}


def generate_weight_suggestions(
    min_declines_for_suggestion: int = 3,
    weight_bump: float = 0.05,
) -> List[str]:
    """
    Analyze decline reasons and suggest weight adjustments.

    Rule: If a decline reason appears >= min_declines_for_suggestion times,
    suggest increasing the corresponding scoring factor weight.

    Returns list of human-readable suggestion strings.
    """
    summary = aggregate_feedback()
    suggestions = []

    for reason, count in summary["decline_reasons"].items():
        if count >= min_declines_for_suggestion and reason in REASON_TO_FACTOR:
            factor = REASON_TO_FACTOR[reason]
            current_w = DEFAULT_WEIGHTS.get(factor, 0.0)
            suggested_w = round(current_w + weight_bump, 2)
            suggestions.append(
                f"Based on {count} declines citing "
                f'"{reason}", consider increasing '
                f"`{factor}` weight from {current_w:.2f} to "
                f"{suggested_w:.2f}."
            )

    if (summary["accepted"] > 0 and summary["declined"] > 0
            and summary["avg_score_declined"] > summary["avg_score_accepted"]):
        suggestions.append(
            "Note: Declined matches have a higher average score "
            f"({summary['avg_score_declined']:.3f}) than accepted matches "
            f"({summary['avg_score_accepted']:.3f}). The scoring formula "
            "may not be capturing the decision criteria that matter most "
            "to chapter leadership."
        )

    return suggestions


# ---------- Sidebar Feedback Summary ----------

def render_feedback_sidebar() -> None:
    """Render feedback summary in the Streamlit sidebar."""
    init_feedback_state()
    summary = aggregate_feedback()

    if summary["total"] == 0:
        st.sidebar.markdown("---")
        st.sidebar.caption("No match feedback recorded yet.")
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("Match Feedback Summary")

    col1, col2, col3 = st.sidebar.columns(3)
    col1.metric("Total", summary["total"])
    col2.metric("Accepted", summary["accepted"])
    col3.metric("Declined", summary["declined"])

    st.sidebar.metric(
        "Acceptance Rate",
        f"{summary['acceptance_rate']:.0%}",
    )

    if summary["decline_reasons"]:
        st.sidebar.markdown("**Decline Reasons:**")
        for reason, count in sorted(
            summary["decline_reasons"].items(),
            key=lambda x: x[1], reverse=True,
        ):
            st.sidebar.markdown(f"- {reason}: **{count}**")

    suggestions = generate_weight_suggestions()
    if suggestions:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Weight Adjustment Suggestions:**")
        for s in suggestions:
            st.sidebar.info(s)
```

#### UI Wireframe

```
+------------------------------------------------------------------+
|  Match Card: Travis Miller -> AI Hackathon                       |
|  +------------------------------------------------------------+ |
|  | [Photo]  Travis Miller                                      | |
|  |          SVP, Sales & Client Development                    | |
|  |          PureSpectrum                                       | |
|  |          Match Score: 87%                                   | |
|  |                                                             | |
|  |  [Radar Chart]  [Explanation Card]                          | |
|  |                                                             | |
|  |  +---------------------+  +---------------------+          | |
|  |  | [Accept Match]      |  | [Decline Match]     |          | |
|  |  +---------------------+  +---------------------+          | |
|  +------------------------------------------------------------+ |
|                                                                   |
|  (After clicking Decline:)                                        |
|  +------------------------------------------------------------+ |
|  | Why are you declining this match?                           | |
|  |  ( ) Too far (geographic distance)                          | |
|  |  (*) Schedule conflict                                      | |
|  |  ( ) Topic mismatch                                         | |
|  |  ( ) Speaker already committed                              | |
|  |  ( ) Other                                                  | |
|  |                                                             | |
|  |  [Submit Decline]                                           | |
|  +------------------------------------------------------------+ |
|                                                                   |
|  SIDEBAR:                                                         |
|  +-----------------------------+                                  |
|  | Match Feedback Summary      |                                  |
|  | Total: 8  Accepted: 5       |                                  |
|  | Declined: 3                 |                                  |
|  | Acceptance Rate: 63%        |                                  |
|  |                             |                                  |
|  | Decline Reasons:            |                                  |
|  | - Too far: 2                |                                  |
|  | - Schedule conflict: 1     |                                  |
|  |                             |                                  |
|  | (no suggestions yet --     |                                  |
|  |  need 3+ of same reason)   |                                  |
|  +-----------------------------+                                  |
+------------------------------------------------------------------+
```

#### Acceptance Criteria

- [ ] Accept button records decision with timestamp, scores, and factor breakdown
- [ ] Decline button shows reason prompt before recording
- [ ] All 5 decline reasons selectable via radio buttons
- [ ] "Other" reason shows a free-text input field
- [ ] After decision, buttons replaced with "Accepted" or "Declined" badge (no double-submit)
- [ ] Decisions persist across Streamlit reruns via `st.session_state`
- [ ] Feedback log appended to `data/feedback_log.csv` on each decision
- [ ] Sidebar summary shows: total, accepted, declined counts + acceptance rate
- [ ] Sidebar shows decline reason breakdown (sorted by frequency)
- [ ] Weight adjustment suggestion appears when any decline reason reaches 3+ occurrences
- [ ] Suggestion text includes: reason count, factor name, current weight, suggested new weight
- [ ] Anomaly detection: if avg declined score > avg accepted score, show warning in sidebar
- [ ] CSV file created on first feedback entry (not at app startup)

#### Harness Guidelines

- File location: `src/feedback/acceptance.py`
- Integration point: Call `render_feedback_buttons(event_id, speaker_id, score, factors)` inside each match card in the Matches tab
- Sidebar integration: Call `render_feedback_sidebar()` in the main app's sidebar section
- Session state keys: `feedback_log`, `feedback_decisions`, `fb_{event}_{speaker}_show_reason`
- CSV output: `data/feedback_log.csv` with columns: `timestamp, event_id, speaker_id, match_score, decision, decline_reason, decline_notes, factor_scores`
- Ensure `init_feedback_state()` is called at app startup (or lazily on first use)

#### Steer Guidelines

- This is the **second priority to cut** if time runs short (after Volunteer Dashboard)
- If session state complexity causes Streamlit rerun loops, simplify: remove the animated transitions and use a single-step decline (dropdown + submit in one view instead of two-step radio + submit)
- If CSV persistence causes permission errors on Streamlit Cloud, degrade to session-state-only mode with a warning
- The `min_declines_for_suggestion` threshold (default 3) is low for demo purposes -- in production this should be higher (10+)

---

### A3.3: Volunteer Dashboard View (2.5h)

**Goal:** Speaker-centric view where a user selects a board member and sees their top-5 matched events, utilization metrics, and a mini bar chart.

**File:** `src/ui/volunteer_dashboard.py`

#### Specification

```python
"""
Volunteer Dashboard View

Speaker-centric complement to the event-centric Matches tab.
Select a board member -> see their top-5 events, utilization rate,
and a mini bar chart of engagement metrics.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Tuple

# Simulated downstream metrics (percentages applied to matched count)
CONVERSION_RATES = {
    "matched":  1.00,   # 100% of top-5 are "matched"
    "accepted": 0.60,   # 60% acceptance rate (target KPI)
    "attended": 0.75,   # 75% of accepted attend (target KPI)
}


def compute_speaker_matches(
    speaker_name: str,
    match_results: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:
    """
    Given all match results, filter to a specific speaker and return
    their top-N events sorted by descending match score.

    Args:
        speaker_name: Name of the board member
        match_results: DataFrame with columns:
            [event_id, speaker_id, total_score, topic_relevance,
             role_fit, geographic_proximity, calendar_fit,
             historical_conversion, student_interest]
        top_n: Number of top events to return

    Returns:
        DataFrame of top-N matched events for this speaker
    """
    speaker_matches = match_results[
        match_results["speaker_id"] == speaker_name
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
    """
    Calculate utilization metrics for a speaker.

    Returns:
        {
            "events_available": int,
            "events_matched": int,    # times in top-3 for any event
            "events_accepted": int,   # from feedback log or simulated
            "events_attended": int,   # simulated
            "utilization_rate": float, # matched / available
            "avg_match_score": float,
        }
    """
    # Count times this speaker appears in top-3 matches for any event
    speaker_matches = match_results[
        match_results["speaker_id"] == speaker_name
    ]
    top3_count = 0
    for event_id in match_results["event_id"].unique():
        event_matches = match_results[
            match_results["event_id"] == event_id
        ].nlargest(3, "total_score")
        if speaker_name in event_matches["speaker_id"].values:
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


def render_utilization_bar_chart(metrics: Dict, speaker_name: str) -> go.Figure:
    """
    Mini bar chart showing: Matched, Accepted, Attended counts
    for a single speaker.
    """
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
            range=[0, max(values) + 2],
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
    """
    Render the full volunteer dashboard view.

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
            f"{row['event_id']} -- Score: {row['total_score']:.0%}",
            expanded=(idx == top_matches.index[0]),
        ):
            factor_col1, factor_col2, factor_col3 = st.columns(3)
            factor_col1.metric(
                "Topic", f"{row.get('topic_relevance', 0):.0%}"
            )
            factor_col2.metric(
                "Role Fit", f"{row.get('role_fit', 0):.0%}"
            )
            factor_col3.metric(
                "Proximity", f"{row.get('geographic_proximity', 0):.0%}"
            )
```

#### UI Wireframe

```
+------------------------------------------------------------------+
|  Volunteer Dashboard                                              |
|  Speaker-centric view: select a board member to see their         |
|  top matched events and utilization metrics.                      |
|                                                                   |
|  Select Board Member: [Travis Miller          v]                  |
|                                                                   |
|  +----------+  +----------+  +----------+  +-----------+         |
|  | Events   |  | Events   |  | Events   |  | Utiliz.   |         |
|  | Matched  |  | Accepted |  | Attended |  | Rate      |         |
|  |    4     |  |    2     |  |    1     |  |   27%     |         |
|  +----------+  +----------+  +----------+  +-----------+         |
|                                                                   |
|  Avg Match Score: 78%                                             |
|                                                                   |
|  +---------------------------------------------------+           |
|  | Travis Miller -- Engagement Funnel                 |           |
|  |                                                    |           |
|  |   ||||                                             |           |
|  |   ||||   ||||                                      |           |
|  |   ||||   ||||   ||||                               |           |
|  |    4       2      1                                |           |
|  |  Matched  Accepted  Attended                       |           |
|  +---------------------------------------------------+           |
|                                                                   |
|  ---------------------------------------------------------------  |
|  Top 5 Event Matches for Travis Miller:                           |
|                                                                   |
|  > AI for a Better Future Hackathon -- Score: 87%      [expanded] |
|  |  Topic: 85%   Role Fit: 90%   Proximity: 92%                  |
|                                                                   |
|  > SWIFT Tech Symposium -- Score: 72%                 [collapsed] |
|  > Information Technology Competition -- Score: 68%   [collapsed] |
|  > Bronco Startup Challenge -- Score: 65%             [collapsed] |
|  > CPP Career Center -- Score: 61%                    [collapsed] |
+------------------------------------------------------------------+
```

#### Acceptance Criteria

- [ ] Dropdown lists all 18 speakers sorted alphabetically
- [ ] Selecting a speaker displays their utilization metrics within 1 second
- [ ] Metric cards show: Events Matched, Events Accepted, Events Attended, Utilization Rate
- [ ] Bar chart renders with 3 bars (Matched, Accepted, Attended) in distinct colors
- [ ] Top-5 matched events listed in descending score order
- [ ] First event expander is open by default; remaining are collapsed
- [ ] Each event expander shows factor scores (at minimum: topic, role fit, proximity)
- [ ] Utilization rate = events_matched / total_events (expressed as percentage)
- [ ] If feedback data exists in session state, use real accepted counts instead of simulated
- [ ] If no matches found for a speaker, show informational message (not error)

#### Harness Guidelines

- File location: `src/ui/volunteer_dashboard.py`
- Integration: Add as a new tab or sub-section within the app (e.g., `tabs = st.tabs(["Matches", "Discovery", "Pipeline", "Volunteers"])`)
- Requires `match_results` DataFrame from the matching engine (Sprint 1 output)
- Requires `feedback_log` from `st.session_state.feedback_log` (can be empty list)
- Import: `from src.ui.volunteer_dashboard import render_volunteer_dashboard`

#### Steer Guidelines

- This is the **first priority to cut** if time runs short (saves 2.5h, minimal demo impact)
- If cut, remove the "Volunteers" tab entirely -- do not leave a broken/empty tab
- If the match_results DataFrame is not available in the expected format, add a lightweight adapter function rather than restructuring the matching engine output
- Simulated acceptance/attendance rates are acceptable for the hackathon demo -- do not spend time building a real tracking system

---

### A3.4: UI Polish + Custom CSS (2.5h)

**Goal:** Consistent visual styling using IA West brand colors, loading spinners, error handling, and mobile layout considerations.

#### Specification

**CSS injection via `st.markdown()`:**

```python
"""
Custom CSS for IA SmartMatch.
Inject at the top of the main app file via st.markdown(..., unsafe_allow_html=True).
"""

CUSTOM_CSS = """
<style>
/* ---------- IA West Brand Colors ---------- */
:root {
    --ia-primary:    #1E3A5F;   /* Dark navy */
    --ia-secondary:  #2563EB;   /* Bright blue */
    --ia-accent:     #F59E0B;   /* Amber accent */
    --ia-success:    #059669;   /* Green */
    --ia-danger:     #DC2626;   /* Red */
    --ia-gray-100:   #F3F4F6;
    --ia-gray-200:   #E5E7EB;
    --ia-gray-500:   #6B7280;
    --ia-gray-700:   #374151;
    --ia-gray-900:   #111827;
}

/* ---------- Match Card Styling ---------- */
div[data-testid="stExpander"] {
    border: 1px solid var(--ia-gray-200);
    border-radius: 8px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

div[data-testid="stExpander"] summary {
    font-weight: 600;
    color: var(--ia-primary);
}

/* ---------- Metric Card Enhancement ---------- */
div[data-testid="stMetric"] {
    background-color: var(--ia-gray-100);
    border-radius: 8px;
    padding: 12px 16px;
    border-left: 4px solid var(--ia-secondary);
}

div[data-testid="stMetric"] label {
    color: var(--ia-gray-500);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--ia-primary);
    font-size: 1.5rem;
    font-weight: 700;
}

/* ---------- Sidebar Branding ---------- */
section[data-testid="stSidebar"] {
    background-color: #F8FAFC;
    border-right: 2px solid var(--ia-secondary);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--ia-primary);
}

/* ---------- Tab Styling ---------- */
button[data-baseweb="tab"] {
    font-weight: 600;
    color: var(--ia-gray-500);
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--ia-secondary);
    border-bottom: 3px solid var(--ia-secondary);
}

/* ---------- Button Styling ---------- */
button[kind="primary"] {
    background-color: var(--ia-secondary);
    border-color: var(--ia-secondary);
}

button[kind="primary"]:hover {
    background-color: var(--ia-primary);
    border-color: var(--ia-primary);
}

/* ---------- Email Preview Card ---------- */
.email-preview {
    background-color: #FFFBEB;
    border: 1px solid var(--ia-accent);
    border-radius: 8px;
    padding: 16px;
    font-family: Georgia, serif;
    line-height: 1.6;
}

.email-preview .subject-line {
    font-weight: 700;
    color: var(--ia-primary);
    font-size: 1.1rem;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--ia-gray-200);
    padding-bottom: 8px;
}

/* ---------- Score Badge ---------- */
.score-badge {
    display: inline-block;
    background-color: var(--ia-secondary);
    color: white;
    font-size: 1.8rem;
    font-weight: 800;
    padding: 8px 16px;
    border-radius: 12px;
    text-align: center;
    min-width: 80px;
}

.score-badge.high   { background-color: var(--ia-success); }
.score-badge.medium { background-color: var(--ia-accent);  }
.score-badge.low    { background-color: var(--ia-danger);  }

/* ---------- Explanation Card ---------- */
.explanation-card {
    background-color: var(--ia-gray-100);
    border-left: 4px solid var(--ia-secondary);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-style: italic;
    color: var(--ia-gray-700);
    line-height: 1.5;
}

/* ---------- Loading State ---------- */
.stSpinner {
    color: var(--ia-secondary);
}

/* ---------- Mobile Responsive ---------- */
@media (max-width: 768px) {
    div[data-testid="stMetric"] {
        padding: 8px 12px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.2rem;
    }
    .score-badge {
        font-size: 1.4rem;
        padding: 6px 12px;
    }
}
</style>
"""
```

**Loading spinner wrapper function:**

```python
import streamlit as st
from contextlib import contextmanager

@contextmanager
def api_call_spinner(message: str = "Processing..."):
    """
    Wrap any API call (Gemini, scraping) with a branded spinner.

    Usage:
        with api_call_spinner("Generating match explanation..."):
            result = generate_text(...)
    """
    with st.spinner(message):
        try:
            yield
        except Exception as e:
            st.error(
                f"An error occurred: {str(e)[:200]}. "
                "Please try again or switch to Demo Mode."
            )
            raise


def render_error_card(title: str, message: str, suggestion: str = "") -> None:
    """
    Display a styled error card with optional recovery suggestion.
    """
    st.error(f"**{title}**")
    st.markdown(f"> {message}")
    if suggestion:
        st.info(f"Suggestion: {suggestion}")
```

**Streamlit theme config (`.streamlit/config.toml`):**

```toml
[theme]
primaryColor = "#2563EB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"
textColor = "#111827"
font = "sans serif"
```

#### Acceptance Criteria

- [ ] `CUSTOM_CSS` injected via `st.markdown()` at top of main app file
- [ ] `.streamlit/config.toml` created with brand colors
- [ ] Match cards have consistent border, shadow, and rounded corners
- [ ] Metric cards have left-border accent and uppercase labels
- [ ] Sidebar has distinct background color and branded header
- [ ] Active tab has blue underline indicator
- [ ] Score badges display with color coding: >= 0.75 green, 0.50-0.74 amber, < 0.50 red
- [ ] Explanation cards have left-border accent and italic text
- [ ] Email previews use serif font with amber border
- [ ] All API calls (Gemini, scraping) wrapped in `api_call_spinner`
- [ ] API errors caught and displayed as user-friendly error cards (no raw tracebacks)
- [ ] Layout renders acceptably on 1024px width (Streamlit Cloud default)

#### Harness Guidelines

- CSS injection: add `st.markdown(CUSTOM_CSS, unsafe_allow_html=True)` as the first statement in the main app after `st.set_page_config()`
- Theme config: create `.streamlit/config.toml` in project root
- The `api_call_spinner` wrapper should be used in: `src/matching/explainer.py`, `src/scraping/extractor.py`, `src/outreach/email_generator.py`
- The `render_error_card` function should be used wherever API calls can fail

#### Steer Guidelines

- Do NOT spend time on pixel-perfect CSS; aim for "noticeably polished" vs. default Streamlit theme
- Streamlit's CSS injection is fragile across versions -- test on the deployed Streamlit version before investing in complex selectors
- If CSS selectors break due to Streamlit version differences, simplify to only: metric card styling, sidebar background, and score badge colors (3 highest-impact changes)
- The `data-testid` selectors used above are stable in Streamlit 1.30+; verify the deployed version

---

### A3.5: Demo Flow Hardening (2.0h)

**Goal:** Build a demo mode toggle that uses cached/pre-generated outputs with artificial delays for a polished live-demo experience, with real API calls as fallback.

**File:** `cache/demo_fixtures/` (directory for fixture files)

#### Specification

**Demo fixture structure:**

```
cache/
  demo_fixtures/
    ucla_scrape_result.json       # Pre-scraped UCLA events
    travis_miller_explanation.json # Match explanation for Travis Miller
    top_match_email.json          # Generated outreach email
    top_match_ics.ics             # Calendar invite file
    match_results_sample.json     # Full match results for demo events
    pipeline_funnel_data.json     # Pipeline funnel numbers
    manifest.json                 # Fixture metadata + timestamps
```

**`cache/demo_fixtures/manifest.json`:**

```json
{
  "generated_at": "2026-03-17T00:00:00Z",
  "fixtures": {
    "ucla_scrape_result": {
      "file": "ucla_scrape_result.json",
      "description": "Pre-scraped and LLM-extracted UCLA career center events",
      "demo_delay_seconds": 2.0
    },
    "travis_miller_explanation": {
      "file": "travis_miller_explanation.json",
      "description": "Gemini match explanation for Travis Miller -> AI Hackathon",
      "demo_delay_seconds": 1.5
    },
    "top_match_email": {
      "file": "top_match_email.json",
      "description": "Generated outreach email for Travis Miller -> AI Hackathon",
      "demo_delay_seconds": 2.0
    },
    "top_match_ics": {
      "file": "top_match_ics.ics",
      "description": "Calendar invite for AI Hackathon",
      "demo_delay_seconds": 0.5
    },
    "match_results_sample": {
      "file": "match_results_sample.json",
      "description": "Full match results for all demo events",
      "demo_delay_seconds": 1.0
    },
    "pipeline_funnel_data": {
      "file": "pipeline_funnel_data.json",
      "description": "Pipeline funnel stage counts with real data labels",
      "demo_delay_seconds": 0.5
    }
  }
}
```

**`cache/demo_fixtures/ucla_scrape_result.json` (example fixture):**

```json
{
  "university": "UCLA",
  "url": "https://career.ucla.edu/events/",
  "scraped_at": "2026-03-17T10:00:00Z",
  "method": "playwright",
  "events": [
    {
      "event_name": "UCLA Data Analytics Hackathon",
      "category": "hackathon",
      "date_or_recurrence": "April 2026",
      "volunteer_roles": ["Judge", "Mentor"],
      "primary_audience": "Graduate and undergraduate students",
      "contact_name": "UCLA Career Center",
      "contact_email": "career@ucla.edu",
      "url": "https://career.ucla.edu/events/data-analytics-hackathon"
    },
    {
      "event_name": "Bruin Entrepreneurs Pitch Night",
      "category": "entrepreneurship",
      "date_or_recurrence": "Monthly, Spring 2026",
      "volunteer_roles": ["Judge", "Guest Speaker"],
      "primary_audience": "Entrepreneurship students",
      "contact_name": "Bruin Entrepreneurs",
      "contact_email": "entrepreneurs@ucla.edu",
      "url": "https://career.ucla.edu/events/pitch-night"
    }
  ]
}
```

**`cache/demo_fixtures/travis_miller_explanation.json`:**

```json
{
  "speaker": "Travis Miller",
  "event": "AI for a Better Future Hackathon",
  "match_score": 0.87,
  "explanation": "Travis Miller (SVP Sales & Client Development, PureSpectrum) is a strong match for the AI for a Better Future Hackathon because his expertise in data collection and MR technology innovation directly aligns with the event's focus on AI applications in business (Topic Relevance: 0.85). As IA West President, his leadership visibility enhances the chapter's brand presence at Cal Poly Pomona (Role Fit: 0.90). Ventura/Thousand Oaks is within reasonable commuting distance to Pomona (Geographic Proximity: 0.82).",
  "factor_scores": {
    "topic_relevance": 0.85,
    "role_fit": 0.90,
    "geographic_proximity": 0.82,
    "calendar_fit": 0.88,
    "historical_conversion": 0.50,
    "student_interest": 0.75
  }
}
```

**`cache/demo_fixtures/top_match_email.json`:**

```json
{
  "speaker": "Travis Miller",
  "event": "AI for a Better Future Hackathon",
  "subject": "Invitation: Judge the AI for a Better Future Hackathon at Cal Poly Pomona",
  "body": "Dear Travis,\n\nI hope this message finds you well. I'm reaching out on behalf of the Cal Poly Pomona Mitchell C. Hill Center regarding an exciting opportunity that aligns perfectly with your expertise in data collection and MR technology innovation.\n\nThe AI for a Better Future Hackathon is an annual event that brings together business and technology students to solve real-world challenges using AI. We're looking for experienced industry judges, and your background as SVP of Sales & Client Development at PureSpectrum makes you an ideal candidate.\n\nEvent Details:\n- Event: AI for a Better Future Hackathon\n- Role: Judge\n- Location: Cal Poly Pomona, Pomona, CA\n- Audience: Business and tech students\n\nAs IA West President, your participation would also strengthen the connection between the Insights Association and the next generation of market research professionals.\n\nWould you be available to participate? I'd be happy to share more details about the judging criteria and time commitment.\n\nBest regards,\n[IA West SmartMatch Platform]",
  "generated_at": "2026-03-17T10:00:00Z"
}
```

**Demo mode toggle implementation:**

```python
import streamlit as st
import json
import time
import os
from typing import Any, Optional

DEMO_FIXTURES_DIR = "cache/demo_fixtures"


def init_demo_mode() -> None:
    """Initialize demo mode toggle in sidebar."""
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False

    st.sidebar.markdown("---")
    st.session_state.demo_mode = st.sidebar.toggle(
        "Demo Mode",
        value=st.session_state.demo_mode,
        help="When ON, uses pre-generated outputs with simulated delays. "
             "When OFF, uses real API calls.",
    )

    if st.session_state.demo_mode:
        st.sidebar.success("Demo Mode: ON (cached outputs)")
    else:
        st.sidebar.caption("Demo Mode: OFF (live API calls)")


@st.cache_data
def load_demo_fixture(fixture_name: str) -> Optional[Any]:
    """
    Load a fixture from the demo fixtures directory.
    Uses @st.cache_data to avoid re-reading files on every rerun.
    """
    manifest_path = os.path.join(DEMO_FIXTURES_DIR, "manifest.json")
    if not os.path.exists(manifest_path):
        return None

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    fixture_info = manifest.get("fixtures", {}).get(fixture_name)
    if not fixture_info:
        return None

    fixture_path = os.path.join(DEMO_FIXTURES_DIR, fixture_info["file"])
    if not os.path.exists(fixture_path):
        return None

    if fixture_path.endswith(".json"):
        with open(fixture_path, "r") as f:
            return json.load(f)
    elif fixture_path.endswith(".ics"):
        with open(fixture_path, "r") as f:
            return f.read()
    return None


def demo_or_live(
    fixture_name: str,
    live_fn,
    *live_args,
    **live_kwargs,
) -> Any:
    """
    Central dispatch: return cached fixture in demo mode,
    or call live_fn in live mode.

    Adds artificial delay in demo mode for "live" feel.
    """
    if st.session_state.get("demo_mode", False):
        fixture = load_demo_fixture(fixture_name)
        if fixture is not None:
            # Load delay from manifest
            manifest_path = os.path.join(DEMO_FIXTURES_DIR, "manifest.json")
            delay = 1.5  # default
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                fixture_info = manifest.get("fixtures", {}).get(fixture_name, {})
                delay = fixture_info.get("demo_delay_seconds", 1.5)
            time.sleep(delay)
            return fixture

    # Live mode or fixture not found: call the real function
    return live_fn(*live_args, **live_kwargs)
```

#### Acceptance Criteria

- [ ] Demo Mode toggle appears in sidebar
- [ ] When ON: sidebar shows green "Demo Mode: ON (cached outputs)" indicator
- [ ] When OFF: sidebar shows gray "Demo Mode: OFF (live API calls)" caption
- [ ] All 6 fixture files exist in `cache/demo_fixtures/` with valid JSON
- [ ] `manifest.json` lists all fixtures with filenames, descriptions, and delay values
- [ ] UCLA scrape returns fixture data with 2-second artificial delay in demo mode
- [ ] Travis Miller explanation returns fixture data with 1.5-second delay
- [ ] Email generation returns fixture data with 2-second delay
- [ ] Calendar .ics returns fixture data with 0.5-second delay
- [ ] Demo mode toggle persists across Streamlit reruns via session state
- [ ] If fixture file is missing, falls through to live API call gracefully
- [ ] `@st.cache_data` prevents re-reading fixture files on every rerun
- [ ] All demo fixture content matches actual prototype output format

#### Harness Guidelines

- Directory: `cache/demo_fixtures/`
- Integration: Replace direct API calls with `demo_or_live("fixture_name", live_function, *args)`
- Sidebar: Call `init_demo_mode()` at the top of the main app's sidebar section
- Fixture generation: Run the prototype once with live API calls and capture outputs to the fixture files
- The `.ics` file should be a real iCalendar file (not JSON) -- load as raw text

#### Steer Guidelines

- Fixture files must be generated from REAL prototype outputs, not hand-written -- run the prototype once end-to-end and save the outputs
- Artificial delays should feel natural: 1.5-2.0s for API calls, 0.5s for local lookups
- If generating fixtures on Day 9, block 30 minutes specifically for this -- it requires a working internet connection and valid API key
- Demo mode should be the DEFAULT for demo day -- toggle it ON before presenting
- Do NOT forget to test the "fixture missing" fallback path -- if one fixture is corrupted, the app should not crash

---

### A3.6: Pipeline Funnel -- Real Prototype Outputs (1.5h)

**Goal:** Replace all simulated/placeholder data in the pipeline funnel with actual outputs from the matching engine, scraping pipeline, and email generation.

#### Specification

```python
"""
Pipeline Funnel with Real Data

Replaces simulated funnel numbers with actual prototype outputs.
File: src/ui/pipeline_funnel.py (update existing)
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List


def compute_real_funnel_data(
    scraped_events: List[Dict],
    match_results: pd.DataFrame,
    feedback_log: List[Dict],
    emails_generated: int,
) -> Dict:
    """
    Compute funnel stage counts from real prototype data.

    Stages:
    1. Discovered: count of all events (CPP data + scraped from universities)
    2. Matched: count of speaker-event pairs in top-3 per event
    3. Contacted: count where outreach email was generated
    4. Confirmed: simulated at 45% of contacted (or from feedback log)
    5. Attended: simulated at 75% of confirmed (or from feedback log)
    6. Member Inquiry: simulated at 15% of attended

    Returns dict with stage names, counts, and hover annotations.
    """
    # Stage 1: Discovered
    cpp_event_count = 15  # known from data
    scraped_count = len(scraped_events)
    discovered = cpp_event_count + scraped_count

    # Stage 2: Matched (top-3 per event)
    matched = 0
    match_annotations = []
    for event_id in match_results["event_id"].unique():
        event_top3 = match_results[
            match_results["event_id"] == event_id
        ].nlargest(3, "total_score")
        matched += len(event_top3)
        for _, row in event_top3.iterrows():
            match_annotations.append(
                f"{row['speaker_id']} -> {event_id} "
                f"({row['total_score']:.0%})"
            )

    # Stage 3: Contacted (emails generated)
    contacted = emails_generated if emails_generated > 0 else int(matched * 0.80)

    # Stage 4: Confirmed (from feedback or simulated)
    accepted_from_feedback = sum(
        1 for f in feedback_log if f.get("decision") == "accept"
    )
    confirmed = (
        accepted_from_feedback
        if accepted_from_feedback > 0
        else int(contacted * 0.45)
    )

    # Stage 5: Attended
    attended = int(confirmed * 0.75)

    # Stage 6: Member Inquiry
    member_inquiry = int(attended * 0.15)

    return {
        "stages": [
            "Discovered", "Matched", "Contacted",
            "Confirmed", "Attended", "Member Inquiry",
        ],
        "counts": [
            discovered, matched, contacted,
            confirmed, attended, member_inquiry,
        ],
        "hover_text": [
            f"{cpp_event_count} CPP events + {scraped_count} scraped "
            f"from {len(set(e.get('university', '') for e in scraped_events))} "
            f"universities",
            f"Top-3 matches per event<br>"
            + "<br>".join(match_annotations[:5])
            + (f"<br>...and {len(match_annotations)-5} more"
               if len(match_annotations) > 5 else ""),
            f"{contacted} outreach emails generated",
            f"{confirmed} volunteers confirmed "
            f"({'real feedback' if accepted_from_feedback > 0 else 'projected at 45%'})",
            f"{attended} events attended (projected at 75% of confirmed)",
            f"{member_inquiry} membership inquiries (projected at 15% of attended)",
        ],
        "annotations": match_annotations,
    }


def render_pipeline_funnel(funnel_data: Dict) -> go.Figure:
    """Render Plotly funnel chart from real data."""
    fig = go.Figure(go.Funnel(
        y=funnel_data["stages"],
        x=funnel_data["counts"],
        textposition="inside",
        textinfo="value+percent initial",
        textfont=dict(size=14, color="white"),
        hovertext=funnel_data["hover_text"],
        hoverinfo="text",
        marker=dict(
            color=[
                "#2563EB",  # Discovered
                "#1E3A5F",  # Matched
                "#059669",  # Contacted
                "#7C3AED",  # Confirmed
                "#D97706",  # Attended
                "#DC2626",  # Member Inquiry
            ],
            line=dict(width=1, color="white"),
        ),
        connector=dict(line=dict(color="#E5E7EB", width=1)),
    ))

    fig.update_layout(
        title=dict(
            text="IA SmartMatch Engagement Pipeline",
            font=dict(size=18, color="#1E3A5F"),
        ),
        height=500,
        margin=dict(l=80, r=40, t=60, b=40),
        plot_bgcolor="#FFFFFF",
    )

    return fig
```

#### Acceptance Criteria

- [ ] Funnel "Discovered" count = actual CPP event count (15) + actual scraped event count
- [ ] Funnel "Matched" count = actual count of top-3 matches per event from matching engine
- [ ] Funnel hover text on "Matched" stage lists real speaker-event pairings (up to 5, then "...and N more")
- [ ] Funnel hover text on "Discovered" stage shows breakdown: "15 CPP events + X scraped from Y universities"
- [ ] If feedback data exists, "Confirmed" uses real accepted count (not simulated)
- [ ] If no feedback data, "Confirmed" projected at 45% with "(projected at 45%)" annotation
- [ ] Funnel displays percentage of initial stage for each subsequent stage
- [ ] All stage bars colored distinctly (6 different colors)
- [ ] Funnel renders within 1 second
- [ ] No placeholder or hardcoded numbers remain in the funnel

#### Harness Guidelines

- File: `src/ui/pipeline_funnel.py` (update existing implementation from Sprint 2)
- Data sources: `match_results` DataFrame, `scraped_events` list, `feedback_log` from session state, `emails_generated` counter from session state
- Streamlit integration: `st.plotly_chart(render_pipeline_funnel(funnel_data), use_container_width=True)`

#### Steer Guidelines

- The critical requirement is replacing placeholder numbers with real ones -- even if the hover text annotations are simplified, the stage counts must be real
- If the matching engine output format differs from the expected DataFrame schema, add a simple adapter (do not refactor the matching engine)
- The "emails_generated" counter may need to be added to session state in the outreach module -- a 5-minute change

---

### A3.7: Data Export for Track B Screenshots (0.5h)

**Goal:** Capture high-resolution screenshots of all key prototype views for inclusion in Track B written deliverables.

#### Specification

**Screenshot capture procedure:**

```bash
# Option 1: Streamlit screenshot via browser DevTools
# 1. Launch the app: streamlit run src/app.py
# 2. Open Chrome DevTools (F12)
# 3. Toggle device toolbar (Ctrl+Shift+M)
# 4. Set resolution to 1920x1080
# 5. Use "Capture full size screenshot" from DevTools menu (...)

# Option 2: Playwright automated screenshot (preferred)
# File: scripts/capture_screenshots.py
```

```python
"""
Automated screenshot capture script.
Run AFTER the Streamlit app is running locally.

Usage: python scripts/capture_screenshots.py
"""

import asyncio
from playwright.async_api import async_playwright
import os

SCREENSHOTS_DIR = "docs/screenshots"
APP_URL = "http://localhost:8501"

SCREENSHOTS = [
    {
        "name": "match_cards.png",
        "description": "Matches tab with top-3 speaker cards and radar chart",
        "path": "/",  # Matches is default tab
        "wait_for": "[data-testid='stExpander']",
        "viewport": {"width": 1920, "height": 1080},
    },
    {
        "name": "pipeline_funnel.png",
        "description": "Pipeline tab with engagement funnel chart",
        "path": "/",  # Navigate to Pipeline tab
        "click": "button:has-text('Pipeline')",
        "wait_for": ".plotly",
        "viewport": {"width": 1920, "height": 1080},
    },
    {
        "name": "expansion_map.png",
        "description": "Board-to-campus expansion map",
        "path": "/",
        "click": "button:has-text('Expansion')",
        "wait_for": ".plotly",
        "viewport": {"width": 1920, "height": 1080},
    },
    {
        "name": "discovery_results.png",
        "description": "Discovery tab with scraped UCLA events",
        "path": "/",
        "click": "button:has-text('Discovery')",
        "wait_for": "[data-testid='stTable']",
        "viewport": {"width": 1920, "height": 1080},
    },
    {
        "name": "email_preview.png",
        "description": "Generated outreach email preview",
        "path": "/",
        "wait_for": ".email-preview",
        "viewport": {"width": 1920, "height": 1080},
    },
    {
        "name": "volunteer_dashboard.png",
        "description": "Volunteer dashboard with utilization chart",
        "path": "/",
        "click": "button:has-text('Volunteers')",
        "wait_for": ".plotly",
        "viewport": {"width": 1920, "height": 1080},
    },
]


async def capture_screenshots():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for shot in SCREENSHOTS:
            page = await browser.new_page(
                viewport=shot["viewport"]
            )
            await page.goto(APP_URL + shot.get("path", "/"))
            await page.wait_for_timeout(3000)  # wait for Streamlit to render

            if "click" in shot:
                try:
                    await page.click(shot["click"])
                    await page.wait_for_timeout(2000)
                except Exception:
                    pass  # tab may not exist

            try:
                await page.wait_for_selector(
                    shot["wait_for"], timeout=10000
                )
            except Exception:
                pass  # proceed with screenshot anyway

            filepath = os.path.join(SCREENSHOTS_DIR, shot["name"])
            await page.screenshot(path=filepath, full_page=True)
            print(f"Captured: {filepath}")
            await page.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture_screenshots())
```

**Required screenshots:**

| Filename | Content | Resolution |
|----------|---------|------------|
| `match_cards.png` | Matches tab: top-3 speaker cards with radar charts and explanation cards | 1920x1080 |
| `pipeline_funnel.png` | Pipeline tab: engagement funnel with real data labels | 1920x1080 |
| `expansion_map.png` | Expansion map: board-to-campus geographic view | 1920x1080 |
| `discovery_results.png` | Discovery tab: scraped UCLA events in results table | 1920x1080 |
| `email_preview.png` | Generated outreach email for Travis Miller | 1920x1080 |
| `volunteer_dashboard.png` | Volunteer dashboard: Travis Miller utilization view | 1920x1080 |

**Output directory:** `docs/screenshots/`

#### Acceptance Criteria

- [ ] `docs/screenshots/` directory exists with all 6 PNG files
- [ ] Each screenshot is minimum 1920x1080 resolution
- [ ] Match cards screenshot shows visible radar chart and explanation text
- [ ] Pipeline funnel screenshot shows all 6 stages with numbers
- [ ] Expansion map screenshot shows speaker and university markers
- [ ] Discovery screenshot shows at least 2 extracted event rows
- [ ] All screenshots use demo mode (cached data) for consistency
- [ ] Screenshots contain no error messages or loading spinners

#### Harness Guidelines

- Output: `docs/screenshots/` directory
- Script: `scripts/capture_screenshots.py` (optional -- manual capture is acceptable if Playwright is unavailable)
- Run after all UI features are complete and demo mode is working
- Ensure demo mode is ON when capturing screenshots for consistency

#### Steer Guidelines

- Manual browser screenshots are completely acceptable -- the Playwright script is a nice-to-have
- If Playwright is not installed or causes issues, use Chrome DevTools device toolbar at 1920x1080
- Prioritize these 4 screenshots in order: (1) match cards, (2) pipeline funnel, (3) expansion map, (4) discovery results
- Email preview and volunteer dashboard screenshots are lower priority
- Screenshots must be captured BEFORE handing off to Track B (handoff H2 deadline: Day 10 morning)

---

## Track B (Person C) -- Written Deliverables & Demo Preparation

### B3.1: Growth Strategy -- Section 4 + 5 (3.0h)

**Goal:** Write the Channel Strategy and Value Proposition + ROI sections of the Growth Strategy document.

#### Specification

**Section 4: Channel Strategy (target: 0.5 page)**

Template structure:

```markdown
## 4. Channel Strategy

### 4.1 SmartMatch Automated Outreach
SmartMatch generates personalized outreach emails for every top match,
referencing the speaker's specific expertise and the event's needs.
[Insert screenshot of email preview from prototype]

- **Mechanism:** AI-generated email drafts personalized to each speaker-event match
- **Volume:** [X] outreach emails per quarter (based on [Y] events x 3 matches each)
- **Response Rate Target:** 25%+ (benchmark: ASAE reports 20-30% response rates
  for professional association outreach)

### 4.2 IA West Event Cross-Promotion
Leverage IA West's 9 scheduled events in 2026 as engagement touchpoints:
[List 3-4 specific events from data_event_calendar.csv with dates and regions]

- **Mechanism:** Match campus contacts to nearby IA events via calendar-fit scoring
- **Example:** "Portland State students attending Katie Nelson's workshop
  are invited to the IA West Portland mixer on April 16."

### 4.3 University Career Center Partnerships
Establish formal MOUs with 3 universities in Phase 1:
- Cal Poly Pomona (existing relationship, 15 events + 35 course sections)
- UCLA (largest LA metro target, career center events page confirmed)
- SDSU (San Diego metro, 2 board members in region)

- **Mechanism:** Recurring engagement calendar shared between IA West and
  career center coordinators
- **Value Exchange:** IA provides industry speakers; university provides
  access to student audience

### 4.4 LinkedIn Targeting (Warm Pipeline)
Target CPP and UCLA alumni in market research, insights, and data analytics
on LinkedIn.

- **Mechanism:** Sponsored InMail targeting alumni of partner universities
  who work in MR-adjacent roles
- **Audience Size Estimate:** [Research needed -- LinkedIn audience builder]
- **Goal:** Convert young professionals into IA West members via
  "we spoke at your alma mater" touchpoint
```

**Section 5: Value Proposition + ROI (target: 0.5 page)**

Template structure:

```markdown
## 5. Value Proposition & ROI

### For Volunteers (Board Members)
| Metric | Manual Process | With SmartMatch | Savings |
|--------|---------------|-----------------|---------|
| Time per match cycle | ~4.5 hours | < 5 minutes | **4.42 hours** |
| Expertise alignment | Gut feel | AI-scored (6 factors) | Measurably better |
| Outreach quality | Generic template | Personalized AI draft | Higher response rates |

### For Universities
- **Qualified speakers on demand:** Match score ensures topic-relevant professionals
- **Reduced coordination overhead:** Automated outreach replaces manual recruiter emails
- **Structured engagement pipeline:** Recurring, not ad-hoc

### For IA West
| Metric | Calculation | Quarterly Value |
|--------|------------|----------------|
| Volunteer hours saved | 4.42h x 45 matches/quarter | **199 hours** |
| Opportunity cost savings | 199h x $50/hour | **$9,950/quarter** |
| Annual savings | $9,950 x 4 quarters | **$39,800/year** |
| Membership conversions | 15% of attended x [attended count] | [X] new members/quarter |
| Membership LTV | $[annual dues] x [avg retention years] | $[LTV] per converted member |

### ROI Summary
At 45 matches per quarter across 5 universities, SmartMatch delivers
an estimated **$39,800/year** in volunteer time savings alone.
Membership conversions at a 10-15% rate from engaged students represent
additional recurring revenue of $[X] per cohort.
```

#### Acceptance Criteria

- [ ] Section 4 covers all 4 channels with specific mechanisms and metrics
- [ ] At least 2 real IA West events referenced from `data_event_calendar.csv` with dates
- [ ] At least 1 specific speaker-event-university example used
- [ ] Section 5 contains ROI table with 4.42h savings calculation
- [ ] Quarterly savings calculated: 199h, $9,950
- [ ] Annual savings calculated: $39,800
- [ ] Both sections use market research language ("conversion," "pipeline," "funnel")
- [ ] Combined length: 0.75-1.0 page (not exceeding 1 page for both sections)

#### Harness Guidelines

- Write in Google Docs or Word format for Track B's workflow
- Reference data from the Track B data package (A2.7 output) for real numbers
- Leave `[X]` placeholders only for data that requires prototype output from Track A

#### Steer Guidelines

- Do NOT spend time researching LinkedIn audience sizes -- use "[Research needed]" placeholder and move on
- Membership LTV calculation should use a reasonable estimate ($200-500 annual dues, 3-5 year retention) if actual IA West dues are not available
- The ROI section is one of the highest-impact parts of the written deliverables for judges -- invest time here
- Use tables liberally -- they communicate ROI information more effectively than prose

---

### B3.2: Growth Strategy -- Integration of Real Data (2.5h)

**Goal:** Replace all placeholder text throughout the Growth Strategy with real prototype outputs, real match examples, and real screenshots.

#### Specification

**Data integration checklist:**

| Placeholder | Source | Example Replacement |
|-------------|--------|-------------------|
| "[X] matches generated" | Match results from prototype | "270 speaker-event pairs scored, 45 top-3 matches generated" |
| "[match example]" | Top match from prototype | "Travis Miller matched to CPP AI Hackathon at 87% match score" |
| "[pipeline numbers]" | Pipeline funnel data | "60+ events discovered, 45 matched, 36 contacted, 16 confirmed" |
| "[university count]" | Discovery tab results | "5 university event pages scraped, 23 new events discovered" |
| "[screenshot]" | `docs/screenshots/` | Inline image of match cards, pipeline funnel, expansion map |
| "[ROI inputs]" | Pipeline sample data | "45 matches/quarter x 4.42h savings = 199h saved" |
| "[speaker distribution]" | Speaker profiles CSV | "18 board members across 10 metro regions from Seattle to San Diego" |
| "[event categories]" | Events CSV | "15 CPP events: 3 hackathons, 4 career services, 3 research symposia, 5 other" |
| "[top-3 example]" | Match engine output | Full top-3 display for AI Hackathon with scores |

**Integration procedure:**

1. Receive screenshots from Track A (handoff H2, Day 10 morning)
2. Receive pipeline funnel numbers from Track A (handoff H3, Day 10 morning)
3. Receive bias audit results from Track A (handoff H4, Day 10 morning)
4. Replace ALL `[placeholder]` text with real values
5. Insert screenshots at appropriate locations
6. Verify all numbers are internally consistent (funnel numbers should add up)
7. Final read-through for narrative coherence

#### Acceptance Criteria

- [ ] Zero `[placeholder]` or `[X]` markers remaining in the document
- [ ] At least 3 real speaker-event match examples cited with specific scores
- [ ] Pipeline funnel numbers referenced are the same numbers displayed in the prototype
- [ ] At least 2 screenshots embedded (match cards + pipeline funnel minimum)
- [ ] All ROI calculations use consistent input numbers
- [ ] Speaker geographic distribution data matches actual CSV data (18 speakers, 10 metro regions)
- [ ] Document reads as a cohesive narrative (no "stitched together" feel)

#### Harness Guidelines

- Depends on Track A handoffs H2, H3, H4 (all due Day 10 morning)
- If screenshots are not ready, use text descriptions: "As shown in the SmartMatch prototype, Travis Miller's match card displays..."
- Keep a running list of all placeholders found and their replacement values

#### Steer Guidelines

- If Track A handoffs are late, do NOT wait -- write descriptive text that can be retroactively updated with screenshots
- Internal consistency is more important than precision -- if you say "45 matches/quarter" in the ROI section, make sure the pipeline funnel section says the same number
- Read the document aloud once after integration -- this catches narrative flow issues

---

### B3.3: Growth Strategy -- ROI Section + Finalization (2.0h)

**Goal:** Complete and polish the ROI section, add expansion map description, and perform final formatting.

#### Specification

**ROI section detail:**

```markdown
## ROI Analysis

### Immediate Impact (Quarter 1 Pilot at CPP)
| Metric | Value | Calculation |
|--------|-------|-------------|
| Events processed | 15 CPP events + 10 high-fit courses = 25 | From provided data |
| Match cycles saved | 25 events x 3 matches = 75 match cycles | Top-3 per event |
| Time saved per cycle | 4.42 hours | Manual (4.5h) - SmartMatch (0.08h) |
| Total hours saved | 332 hours | 75 x 4.42 |
| Opportunity cost savings | $16,575 | 332h x $50/h |

### Projected Impact (Year 1: 5 Universities)
| Metric | Value |
|--------|-------|
| Events per quarter | ~45 (15 CPP + 30 from 4 new universities) |
| Matches per quarter | 135 (45 x 3) |
| Hours saved per quarter | 597 hours |
| Annual savings | $119,340 (597h x $50 x 4 quarters) |
| Membership conversions (est.) | 8-12 new members/year at 10-15% conversion |
```

**Expansion map description (to accompany screenshot):**

```markdown
### Board-to-Campus Expansion Map

The SmartMatch expansion map (Figure X) visualizes the geographic
alignment between IA West's 18 board members and 11 target universities
across the West Coast corridor. Connection lines indicate viable
speaker-campus pairings based on geographic proximity scores. Key
observations:

- **LA Metro cluster:** 8 board members can serve UCLA, USC, Cal Poly
  Pomona, and CSULB with commuting distances under 50 miles
- **San Francisco cluster:** 4 board members positioned to serve USF,
  SFSU, and UC Davis
- **Regional anchors:** Portland (Katie Nelson) and Seattle (Greg Carter)
  provide coverage for Pacific Northwest campuses
- **Gap identified:** No board members in Sacramento/Central Valley --
  UC Davis engagement requires SF-based members to travel ~75 miles
```

**Final formatting checklist:**

- [ ] Consistent heading levels (H1 for title, H2 for sections, H3 for subsections)
- [ ] Professional font (e.g., Calibri 11pt or Times New Roman 12pt)
- [ ] 1-inch margins
- [ ] Page numbers
- [ ] Section numbers (1, 2, 3, 4, 5)
- [ ] All tables formatted consistently
- [ ] No orphan headings (heading at bottom of page with content on next page)
- [ ] Total length: 2.5-3 pages (hard cap at 3 pages)

#### Acceptance Criteria

- [ ] ROI section includes both "Quarter 1 Pilot" and "Year 1 Projected" tables
- [ ] All calculations are arithmetically correct
- [ ] Expansion map description references 3+ specific observations from the map
- [ ] Document formatted professionally with consistent headings, fonts, and margins
- [ ] Total document length: 2.5-3 pages
- [ ] No spelling or grammatical errors (run spellcheck)

#### Harness Guidelines

- This is a formatting and finalization task -- content should be 90%+ complete from B3.1 and B3.2
- Use Word/Google Docs formatting tools for professional layout
- Export final version as both .docx and .pdf

#### Steer Guidelines

- If the document exceeds 3 pages, cut the LinkedIn channel strategy subsection first (least impactful)
- If the expansion map screenshot is not available, replace with the text description only -- do not leave a blank space
- The ROI numbers are the single most memorable element for judges -- triple-check the arithmetic

---

### B3.4: Measurement Plan -- Revision with Real Data (1.5h)

**Goal:** Update the Measurement Plan with actual prototype performance data and refine the A/B test proposal.

#### Specification

**KPI updates with real data:**

| KPI | Target | Real Prototype Data Point |
|-----|--------|--------------------------|
| Match Acceptance Rate | 60%+ | "[X]% of matches scored above 0.70 threshold" |
| Email Response Rate | 25%+ | "[X] emails generated in demo, average quality score: [X]/5" |
| Event Attendance Rate | 70%+ | "Prototype pipeline shows [X]% conversion from Confirmed to Attended" |
| Volunteer Utilization Rate | 2+ events/speaker/quarter | "Prototype shows avg [X] top-3 appearances per speaker across 15 events" |
| Discovery Efficiency | 5+ events/university/quarter | "[X] events discovered across [Y] universities via automated scraping" |

**A/B test proposal refinement:**

```markdown
### Proposed Validation Experiment

**Design:** Randomized controlled trial across 6 IA West events in Q3-Q4 2026

**Treatment Groups:**
- **Group A (SmartMatch):** 3 events use SmartMatch-recommended speaker matches
  - Events: [Select 3 from data_event_calendar.csv by region diversity]
- **Group B (Manual):** 3 events use traditional chapter leadership matching

**Sample Size:** 15 matches per condition (3 events x 5 matches each)
- Power analysis: At alpha=0.05, this sample detects a 25+ percentage-point
  difference in acceptance rates with 80% power

**Primary Metric:** Match acceptance rate (accept/decline from feedback loop)

**Secondary Metrics:**
- Volunteer satisfaction score (post-event survey, 1-5 scale)
- Event attendance rate
- Time from match to confirmation (days)

**Duration:** 6 months (Q3-Q4 2026)
**Analysis Plan:** Two-proportion z-test for acceptance rates,
  Mann-Whitney U for satisfaction scores
```

**Feedback loop diagram (ASCII for document):**

```
+-------------------+       +-------------------+
| Match Generated   |------>| Chapter Leader    |
| (SmartMatch       |       | Reviews Match     |
|  top-3 per event) |       | (Score + Explain) |
+-------------------+       +-------------------+
                                     |
                            +--------+--------+
                            |                 |
                     +------v------+   +------v------+
                     | Accept      |   | Decline     |
                     | (proceed to |   | (capture    |
                     |  outreach)  |   |  reason)    |
                     +------+------+   +------+------+
                            |                 |
                            v                 v
                     +-------------------+-------------------+
                     |     Feedback Aggregation              |
                     |  - Accept/decline rates by factor     |
                     |  - Decline reason distribution        |
                     |  - Score threshold analysis           |
                     +-------------------+-------------------+
                                     |
                                     v
                     +-----------------------------------+
                     | Weight Adjustment Recommendations |
                     |  "5 declines for distance ->      |
                     |   increase geo_proximity weight   |
                     |   from 0.20 to 0.30"              |
                     +-------------------+---------------+
                                     |
                                     v
                     +-----------------------------------+
                     | Improved Next-Cycle Matches       |
                     | (quarterly weight refresh)        |
                     +-----------------------------------+
```

#### Acceptance Criteria

- [ ] All KPIs updated with at least one real data point from the prototype
- [ ] A/B test proposal specifies: 3 specific events from calendar data, sample size justification, analysis plan
- [ ] Feedback loop diagram included in document
- [ ] Total length: 1 page (hard cap)
- [ ] No remaining placeholder text

#### Harness Guidelines

- Requires prototype performance data from Track A (handoff H3)
- If exact prototype numbers are not available, use data from the matching engine output (e.g., "72% of matches scored above 0.70")

#### Steer Guidelines

- The A/B test proposal is the most differentiating element for judges (shows methodological rigor)
- If time is short, prioritize the KPI table and A/B test over the feedback loop diagram
- Use the ASCII diagram directly in the document if there is no time to create a polished graphic

---

### B3.5: Responsible AI Note -- Final Polish (1.0h)

**Goal:** Integrate specific bias audit results and concrete mitigations into the Responsible AI Note.

#### Specification

**Bias audit section (to add/revise):**

```markdown
## Bias Audit Results

We conducted a geographic distribution analysis across all 18 speakers
to identify potential over-matching patterns:

| Metro Region | Speakers | Top-3 Match Appearances | Match Frequency |
|-------------|----------|------------------------|----------------|
| Los Angeles (all sub-regions) | 8 | [X] | [X/total]% |
| San Francisco | 4 | [X] | [X/total]% |
| Ventura / Thousand Oaks | 2 | [X] | [X/total]% |
| San Diego | 2 | [X] | [X/total]% |
| Portland | 1 | [X] | [X/total]% |
| Seattle | 1 | [X] | [X/total]% |

**Finding:** LA-based speakers account for [X]% of all top-3 match
appearances, which is [proportional to / disproportionate to] their
share of the board (44%). This is [expected / concerning] because
[most target universities are in the LA metro area / the geographic
proximity weight amplifies LA's natural advantage].

**Mitigations Implemented:**
1. **Diversity-of-speaker rotation flag:** The matching engine tracks
   how many times each speaker has been matched in the current quarter.
   Speakers matched 3+ times receive a 10% penalty to their
   `historical_conversion` score, promoting rotation.
2. **Transparent score breakdown:** Every match card displays the
   contribution of all 6 scoring factors, making geographic bias
   visible to chapter leadership.
3. **Adjustable weights:** Chapter leaders can manually reduce the
   `geographic_proximity` weight to de-emphasize location advantage.

**Specific Example:** "[Speaker X] appeared in 12 of 15 top-3 match
lists. Investigation revealed this is due to broad expertise tags
covering 4 of 6 event categories, not algorithmic bias. No corrective
action needed -- this speaker is genuinely the best match for multiple
events."
```

#### Acceptance Criteria

- [ ] Bias audit table includes all 6 metro regions with match frequency data
- [ ] At least 1 specific finding stated (proportional or disproportionate)
- [ ] 3 concrete mitigations listed (not generic "we will address bias")
- [ ] At least 1 specific speaker example investigated
- [ ] Total length: 0.5 page (hard cap)
- [ ] Privacy, transparency, and data handling sections also present (from Sprint 2 draft)

#### Harness Guidelines

- Requires bias audit data from Track A (handoff H4, Day 10 morning)
- If bias audit data is not available, compute manually from the match results: count top-3 appearances per speaker, group by metro region

#### Steer Guidelines

- This section is worth up to 10 judging points -- it must be concrete, not generic
- The specific speaker example is the most impactful element -- judges remember concrete examples
- If time is short, prioritize the mitigations list over the geographic distribution table

---

### B3.6: Demo Script -- First Draft (2.0h)

**Goal:** Write a complete 5-minute demo script with exact click paths, talking points, timing markers, and backup plan triggers.

#### Specification

**Demo script structure:**

```markdown
# IA SmartMatch -- 5-Minute Demo Script

## Pre-Demo Checklist
- [ ] Streamlit app running locally (or on Streamlit Cloud)
- [ ] Demo Mode: ON (sidebar toggle)
- [ ] Browser at 100% zoom, fullscreen (F11)
- [ ] Matches tab selected as starting view
- [ ] Backup demo video loaded and ready (alt-tab accessible)
- [ ] Written deliverables printed and within reach
- [ ] Water nearby (5 minutes of continuous speaking)

---

## 0:00 -- 0:30 | Problem Statement (30 seconds)

**[SLIDE or VERBAL -- no app interaction yet]**

> "IA West coordinates 18 board members across 10 metro regions --
> from Seattle to San Diego -- for 8+ events per year. Today, this
> is done entirely through email chains and gut feel. There's no
> centralized system for discovering opportunities, no way to match
> the right speaker to the right event, and no measurement of whether
> campus engagement actually drives IA membership. The Stanford Social
> Innovation Review estimates volunteer-run chapters lose 30-40% of
> engagement opportunities to coordination overhead."

**Key stats to hit:** 18 speakers, 10 metros, 8+ events/year, zero infrastructure.

---

## 0:30 -- 1:15 | Solution Overview (45 seconds)

**[Show app -- overview of tabs]**

> "SmartMatch solves this with four AI-powered modules."

**CLICK:** Gesture across the tab bar: Matches, Discovery, Pipeline

> "First, we ingest all 77 data points -- speaker profiles, CPP events,
> course schedules, and the IA event calendar. Then we use Gemini
> embeddings to semantically match speaker expertise to event needs
> across six scoring dimensions."

**CLICK:** Point to sidebar weight sliders

> "Chapter leadership can tune these weights in real time. Let me
> show you how this works."

---

## 1:15 -- 2:15 | Live Demo: Discovery (60 seconds)

**[Navigate to Discovery tab]**

**CLICK:** Click "Discovery" tab
**CLICK:** Select "UCLA" from university dropdown
**CLICK:** Click "Discover Events" button

> "Let's say a new semester just started at UCLA. SmartMatch can
> automatically scan the UCLA career center events page..."

**[WAIT for 2-second demo delay -- spinner shows "Discovering events..."]**

> "...and extract structured event data using Gemini. Here we
> can see [X] events extracted, including hackathons, career fairs,
> and guest lecture opportunities."

**CLICK:** Click "Add to Matching" on the first extracted event

> "With one click, this UCLA event is now in our matching pipeline."

**BACKUP TRIGGER:** If spinner hangs > 5 seconds, say:
> "Let me show you what SmartMatch found when we ran this earlier today."
> Toggle Demo Mode ON if it's OFF.

---

## 2:15 -- 3:00 | Live Demo: Matching (45 seconds)

**[Navigate to Matches tab]**

**CLICK:** Click "Matches" tab
**CLICK:** Select "AI for a Better Future Hackathon" from event dropdown

> "Now let's look at matching. For the AI Hackathon at Cal Poly Pomona,
> SmartMatch recommends Travis Miller as the top match at 87%."

**POINT:** Gesture to radar chart

> "You can see the six scoring dimensions: topic relevance at 85%
> because his data collection expertise aligns with the hackathon's
> AI focus, role fit at 90% because they need judges and he's IA
> West President, and geographic proximity at 82% -- Ventura is
> about an hour from Pomona."

**CLICK:** Read the explanation card text aloud (first sentence only)

**CLICK:** Adjust one weight slider (e.g., increase geographic_proximity)

> "Watch what happens when we increase the geographic proximity
> weight -- the rankings shift in real time."

---

## 3:00 -- 3:30 | Live Demo: Email + Calendar (30 seconds)

**CLICK:** Click "Generate Email" button on Travis Miller's match card

> "SmartMatch generates a personalized outreach email referencing
> Travis's specific expertise and the event details."

**POINT:** Highlight the subject line and first paragraph

> "This isn't a generic template -- it mentions his data collection
> background, his role as IA West President, and the specific
> hackathon he'd be judging."

**CLICK:** Click "Download Calendar Invite"

> "And here's a calendar invite ready to send."

**BACKUP TRIGGER:** If email generation fails, say:
> "Here's an example email SmartMatch generated earlier."
> Show cached email in demo mode.

---

## 3:30 -- 4:00 | Pipeline + ROI (30 seconds)

**CLICK:** Click "Pipeline" tab

> "The pipeline tracker shows our full engagement funnel. From
> [X] discovered events across 5 universities, SmartMatch generated
> [Y] top matches. At projected conversion rates based on nonprofit
> engagement benchmarks, that translates to [Z] membership inquiries
> per quarter."

**POINT:** Hover over funnel stages to show real data labels

> "Each stage uses real speaker and event names from our prototype."

**PAUSE:** Let the numbers sink in.

> "The ROI: 4.42 hours saved per match cycle. At 45 matches per
> quarter, that's 199 volunteer hours saved -- nearly $10,000 in
> opportunity cost savings per quarter."

---

## 4:00 -- 4:30 | Written Deliverables (30 seconds -- split into two parts)

### 4:00 -- 4:15 | Growth Strategy (15 seconds)

> "Our Growth Strategy details a 3-phase rollout: starting with
> Cal Poly Pomona's 15 events and 35 course sections, expanding to
> UCLA and USC in Phase 2, then the full West Coast corridor --
> SDSU, UC Davis, Portland State -- by Q2 2027."

**[Hold up or reference the Growth Strategy document]**

### 4:15 -- 4:30 | Measurement Plan (15 seconds)

> "Our Measurement Plan defines 7 KPIs including match acceptance
> rate and volunteer utilization, plus a proposed A/B test across
> 6 IA West events to validate the matching algorithm."

---

## 4:30 -- 4:45 | Responsible AI (15 seconds)

> "Every match is explainable -- no black boxes. We conducted a
> bias audit across all 18 speakers showing geographic distribution
> of matches, and implemented a diversity-of-speaker rotation flag
> to prevent over-matching."

---

## 4:45 -- 5:00 | Close (15 seconds)

> "IA SmartMatch turns a manual, ad-hoc process into a data-driven
> engagement pipeline. One platform: discover, match, reach out,
> and track -- from campus event to IA membership. Thank you."

**[END -- prepare for Q&A]**

---

## Backup Plan Quick Reference

| Failure | Trigger | Action |
|---------|---------|--------|
| No internet | App cannot reach Gemini | Toggle Demo Mode ON (all cached) |
| Scrape hangs | Spinner > 5 seconds | "Let me show you cached results" |
| API error | Error card appears | Switch to Demo Mode, continue |
| App crash | Streamlit error page | Restart (5s), or switch to video |
| Total failure | Nothing works | Play backup video, present docs |

## Timing Check Points

| Time | You Should Be At | Behind? Action |
|------|------------------|---------------|
| 1:00 | Starting Discovery demo | Skip solution overview detail |
| 2:00 | Finishing Discovery demo | Skip "Add to Matching" click |
| 3:00 | Finishing Matching demo | Skip email generation, mention verbally |
| 4:00 | Finishing Pipeline | Skip pipeline detail, go to deliverables |
| 4:30 | Starting Responsible AI | Cut to 1 sentence and close |
```

#### Acceptance Criteria

- [ ] Script covers all 7 sections with timing markers
- [ ] Total scripted time: 4:45-5:00 (leaves 0-15 seconds of buffer)
- [ ] Pre-demo checklist included
- [ ] Exact click paths specified for each demo interaction
- [ ] Talking points include specific numbers from the prototype
- [ ] Backup plan trigger for each potential failure mode
- [ ] Timing checkpoint table for pacing during demo
- [ ] Transition phrases between each section are explicit

#### Harness Guidelines

- This document should be printed and available during demo practice (Sprint 4)
- Timing markers should be verified during rehearsals (A4.6 / B4.5)
- Click paths must match the actual app UI after all Sprint 3 changes

#### Steer Guidelines

- The demo script is a living document -- it will be revised in Sprint 4 based on rehearsal feedback
- Do NOT memorize the script word-for-word; memorize the structure and key numbers
- The backup plan section is as important as the main script -- practice the transitions
- If the demo consistently runs long in practice, cut the Solution Overview section (0:30-1:15) to 20 seconds

---

## Definition of Done

### Track A (Code)

- [ ] ALL code features complete and working (feature freeze enforced at end of Day 9)
- [ ] Board-to-campus expansion map renders with all 18 speakers and 11 universities
- [ ] Match acceptance feedback loop stores decisions and generates weight suggestions
- [ ] Volunteer dashboard shows per-speaker utilization metrics and bar chart
- [ ] Custom CSS applied: branded colors, styled cards, loading spinners
- [ ] Demo mode toggle works: cached outputs with artificial delays
- [ ] Pipeline funnel uses real prototype data (no placeholders)
- [ ] Screenshots exported to `docs/screenshots/` (minimum 4 images)
- [ ] No new features added after Day 9 (Day 10 = integration + bug fixes only)

### Track B (Writing)

- [ ] Growth Strategy complete draft (2.5-3 pages) with Sections 1-5 done
- [ ] All real data integrated: match examples, pipeline numbers, screenshots
- [ ] ROI section complete with specific calculations ($9,950/quarter, $39,800/year)
- [ ] Measurement Plan finalized: 7 KPIs, A/B test proposal, feedback loop diagram
- [ ] Responsible AI Note finalized: bias audit results, 3 concrete mitigations, specific example
- [ ] Demo script first draft complete: 7 sections, timing markers, backup plans

## Phase Closeout

- At the end of every phase in this sprint, invoke a dedicated agent in code-review mode against the completed work.
- Do not mark the phase complete until review findings are resolved.
- After the review passes with no open issues, update the affected documentation and commit the changes.

---

## Go/No-Go Gate (End of Day 10)

**PASS Criteria:**
- All code features work end-to-end (matching + discovery + email + pipeline + expansion map + feedback + volunteer dashboard)
- Written deliverables are 90%+ complete with real data integrated
- Demo mode tested and working with cached outputs
- Proceed to Sprint 4: Testing, Demo Prep, Final Polish

**PARTIAL PASS -- Feature Cut Protocol:**
If any "should-add" feature is incomplete at end of Day 9, cut in this order:
1. **First cut:** Volunteer Dashboard View (A3.3) -- saves 2.5h, minimal demo impact, remove the tab entirely
2. **Second cut:** Match Acceptance Feedback Loop (A3.2) -- saves 3.0h, no demo impact, remove buttons from cards
3. **Third cut:** Board-to-Campus Expansion Map (A3.1) -- saves 3.0h, moderate demo impact, remove from Pipeline tab

Core MVP (matching engine + discovery + email + pipeline funnel) is **never cut**.

**FAIL Criteria:**
- If any code feature is still being actively developed after Day 9 EOD, that feature is forcibly cut
- If written deliverables are below 75% at Day 10 EOD, Person B shifts 50% of Day 11-12 to writing support (code is frozen, only bug fixes)

---

## Memory Update Triggers

The following events should trigger updates to `.memory/context/` files:

| Trigger | Memory File | Content |
|---------|-------------|---------|
| Expansion map coordinate table finalized | `.memory/context/cat3-geo-data.md` | Speaker metro coords, university coords, proximity scores |
| Feedback loop session state schema defined | `.memory/context/cat3-feedback-schema.md` | Session state keys, CSV schema, decline reasons |
| Demo fixtures generated | `.memory/context/cat3-demo-fixtures.md` | List of fixture files, generation timestamps, fixture content hashes |
| Screenshots captured | `.memory/context/cat3-screenshots.md` | Screenshot filenames, descriptions, capture settings |
| CSS theme finalized | `.memory/context/cat3-theme.md` | Brand colors, CSS class names, Streamlit version compatibility notes |
| Real pipeline data computed | `.memory/context/cat3-pipeline-data.md` | Funnel stage counts, source calculations, hover text content |
| Bias audit results computed | `.memory/context/cat3-bias-audit.md` | Match frequency by speaker, geographic distribution, findings |
| Growth Strategy sections complete | `.memory/context/cat3-growth-strategy-status.md` | Section completion status, word counts, placeholder inventory |
| Demo script finalized | `.memory/context/cat3-demo-script.md` | Script version, timing adjustments, rehearsal notes |

---

## Dependencies

### Cross-Track Dependencies (Track A -> Track B)

| ID | Source Task | Target Task | Artifact | Deadline | Risk if Late |
|----|------------|-------------|----------|----------|-------------|
| H2 | A3.7 (Screenshots) | B3.2 (Data integration) | PNG files in `docs/screenshots/` | Day 10 morning | Growth Strategy lacks visual evidence. Mitigate: use text descriptions. |
| H3 | A3.6 (Pipeline data) | B3.4 (Measurement Plan) | Real funnel numbers | Day 10 morning | Measurement Plan uses estimates. Mitigate: use prototype console output. |
| H4 | A3.1/A1.2 (Match results) | B3.5 (Responsible AI) | Bias audit data: match frequency by speaker | Day 10 morning | Responsible AI Note is generic. Mitigate: compute manually from match CSV. |

### Intra-Track Dependencies (Track A)

| Source | Target | Dependency |
|--------|--------|-----------|
| A3.1 (Expansion map) | A3.7 (Screenshots) | Map must render before screenshot capture |
| A3.2 (Feedback loop) | A3.3 (Volunteer dashboard) | Feedback data feeds utilization metrics |
| A3.4 (CSS polish) | A3.7 (Screenshots) | CSS must be applied before screenshot capture |
| A3.5 (Demo fixtures) | A3.6 (Pipeline real data) | Demo fixtures include pipeline data |
| A3.1-A3.4 (All features) | A3.5 (Demo hardening) | All features must work before caching outputs |

### Intra-Track Dependencies (Track B)

| Source | Target | Dependency |
|--------|--------|-----------|
| B3.1 (Sections 4-5) | B3.3 (ROI finalization) | ROI section builds on value proposition |
| B3.2 (Data integration) | B3.3 (Finalization) | Can only finalize after data is integrated |
| B3.1-B3.3 (Growth Strategy) | B3.6 (Demo script) | Demo script references Growth Strategy content |

### External Dependencies

| Dependency | Required For | Fallback |
|------------|-------------|----------|
| Gemini API access | A3.5 (generating demo fixtures) | Use fixtures from Sprint 2 test runs |
| Working internet | A3.5 (live scraping for fixture generation) | Use cached HTML from Sprint 2 |
| Streamlit app fully functional | A3.7 (screenshots) | Manual mockup screenshots |

---

## Recommended Task Sequencing

### Day 9 (Feature Freeze Day)

**Track A -- Morning (4h):**
1. A3.4: CSS polish (2.5h) -- apply first so all subsequent work looks polished
2. A3.1: Begin expansion map (1.5h)

**Track A -- Afternoon (4h):**
3. A3.1: Finish expansion map (1.5h)
4. A3.2: Feedback loop (3.0h -- start, may extend to evening)

**Track A -- Evening (2h):**
5. A3.2: Finish feedback loop (remaining time)
6. A3.3: Volunteer dashboard (begin if time permits)

**Track B -- Full Day (6-8h):**
1. B3.1: Growth Strategy Sections 4 + 5 (3.0h)
2. B3.6: Demo script first draft (2.0h)
3. B3.5: Responsible AI Note polish (1.0h) -- partial, pending bias data

### Day 10 (Integration + Bug Fixes Only)

**Track A -- Morning (4h):**
1. A3.3: Volunteer dashboard (2.5h -- complete or cut)
2. A3.5: Demo flow hardening (2.0h -- begin fixture generation)

**Track A -- Afternoon (3-4h):**
3. A3.5: Finish demo fixtures
4. A3.6: Pipeline funnel real data (1.5h)
5. A3.7: Screenshots (0.5h) -- DELIVER TO TRACK B

**Track B -- Morning (3h):**
1. B3.4: Measurement Plan revision (1.5h)
2. B3.5: Responsible AI Note finalize (remaining 0.5h, after receiving bias data)

**Track B -- Afternoon (3-4h):**
3. B3.2: Growth Strategy data integration (2.5h -- after receiving screenshots)
4. B3.3: Growth Strategy ROI + finalization (2.0h)
