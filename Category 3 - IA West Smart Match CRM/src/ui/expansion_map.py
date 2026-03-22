"""
Board-to-Campus Expansion Map

Renders a Plotly scatter_geo figure with three layers:
1. Speaker metro locations (circles, colored by expertise cluster)
2. University campus locations (diamonds)
3. Connection lines (opacity proportional to geographic_proximity score)
"""

import plotly.graph_objects as go
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, List, Tuple

from src.config import REGION_COORDINATES, UNIVERSITY_COORDINATES

# ---------- Coordinate Lookup Tables ----------
# Coordinates are now sourced from config.py (single source of truth).
# Local aliases maintain backward compatibility for this module.
SPEAKER_METRO_COORDS = REGION_COORDINATES
UNIVERSITY_COORDS = UNIVERSITY_COORDINATES

# Expertise cluster color mapping (6 clusters)
EXPERTISE_CLUSTER_COLORS: Dict[str, str] = {
    "Data & Analytics":       "#2563EB",
    "Qualitative Research":   "#7C3AED",
    "Sales & Client Dev":     "#059669",
    "Marketing & Brand":      "#D97706",
    "Operations & Events":    "#DC2626",
    "Innovation & AI":        "#0891B2",
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
    connections: List[Dict] = []
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
    added_clusters: set = set()
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
            text=[name.split()[0]],
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
