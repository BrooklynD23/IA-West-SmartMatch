"""Tests for Board-to-Campus Expansion Map (A3.1)."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.ui.expansion_map import (
    EXPERTISE_CLUSTER_COLORS,
    SPEAKER_CLUSTERS,
    SPEAKER_METRO_COORDS,
    UNIVERSITY_COORDS,
    build_connection_data,
    compute_geographic_proximity,
    render_expansion_map,
)

# ---------- Fixtures ----------

ALL_SPEAKER_METROS = [
    "Ventura / Thousand Oaks",
    "Los Angeles — West",
    "Los Angeles",
    "Los Angeles — North",
    "Los Angeles — East",
    "Los Angeles — Long Beach",
    "Orange County / Long Beach",
    "San Francisco",
    "Portland",
    "San Diego",
    "Seattle",
]

ALL_UNIVERSITIES = [
    "UCLA", "SDSU", "UC Davis", "USC", "Portland State",
    "Cal Poly Pomona", "CSULB", "UC San Diego", "UW (Seattle)",
    "USF", "SFSU",
]

ALL_SPEAKER_NAMES = [
    "Travis Miller", "Amanda Keller-Grill", "Katrina Noelle",
    "Rob Kaiser", "Donna Flynn", "Greg Carter", "Katie Nelson",
    "Liz O'Hara", "Sean McKenna", "Calvin Friesth",
    "Ashley Le Blanc", "Monica Voss", "Molly Strawn",
    "Shana DeMarinis", "Dr. Yufan Lin", "Adam Portner",
    "Laurie Bae", "Amber Jawaid",
]


@pytest.fixture
def sample_speakers_df() -> pd.DataFrame:
    """Minimal speakers DataFrame for testing."""
    return pd.DataFrame([
        {"Name": "Travis Miller", "Metro Region": "Ventura / Thousand Oaks",
         "Title": "SVP, Sales", "Company": "PureSpectrum"},
        {"Name": "Amanda Keller-Grill", "Metro Region": "Los Angeles — West",
         "Title": "VP Events", "Company": "IA West"},
        {"Name": "Sean McKenna", "Metro Region": "San Diego",
         "Title": "Director", "Company": "Acme"},
    ])


@pytest.fixture
def full_speakers_df() -> pd.DataFrame:
    """Full 18-speaker DataFrame matching spec."""
    speakers = [
        ("Travis Miller", "Ventura / Thousand Oaks", "SVP", "PureSpectrum"),
        ("Amanda Keller-Grill", "Los Angeles — West", "VP", "IA West"),
        ("Katrina Noelle", "San Francisco", "Researcher", "KN Inc"),
        ("Rob Kaiser", "Los Angeles — Long Beach", "CTO", "Kaiser AI"),
        ("Donna Flynn", "Los Angeles", "COO", "Flynn Ops"),
        ("Greg Carter", "Seattle", "Sr Researcher", "Carter Qual"),
        ("Katie Nelson", "Portland", "CMO", "Nelson Brand"),
        ("Liz O'Hara", "San Francisco", "AI Lead", "O'Hara AI"),
        ("Sean McKenna", "San Diego", "Director", "McKenna Sales"),
        ("Calvin Friesth", "Los Angeles", "Sales Mgr", "Friesth Co"),
        ("Ashley Le Blanc", "Los Angeles — North", "Brand Dir", "LeBlanc Mkt"),
        ("Monica Voss", "San Diego", "Data Scientist", "Voss Analytics"),
        ("Molly Strawn", "Los Angeles — West", "Mkt Mgr", "Strawn Media"),
        ("Shana DeMarinis", "Ventura / Thousand Oaks", "Events Dir", "DeMarinis Ops"),
        ("Dr. Yufan Lin", "Los Angeles — East", "Prof", "Cal Poly"),
        ("Adam Portner", "San Francisco", "BD Lead", "Portner Consulting"),
        ("Laurie Bae", "San Francisco", "Ops Mgr", "Bae Events"),
        ("Amber Jawaid", "Los Angeles", "AI Strategist", "Jawaid AI"),
    ]
    return pd.DataFrame(speakers, columns=["Name", "Metro Region", "Title", "Company"])


# ---------- Coordinate lookup completeness ----------

def test_speaker_metro_coords_complete():
    """All 18 speakers have their metro region in the coordinate lookup."""
    for name in ALL_SPEAKER_NAMES:
        cluster = SPEAKER_CLUSTERS.get(name)
        assert cluster is not None, f"Speaker {name} missing from SPEAKER_CLUSTERS"
    # All metro regions used by speakers must be in SPEAKER_METRO_COORDS
    assert len(SPEAKER_METRO_COORDS) >= 11


def test_university_coords_complete():
    """All 11 universities are in the coordinate lookup."""
    for uni in ALL_UNIVERSITIES:
        assert uni in UNIVERSITY_COORDS, f"University {uni} missing from UNIVERSITY_COORDS"
    assert len(UNIVERSITY_COORDS) == 11


# ---------- Geographic proximity ----------

def test_compute_geographic_proximity_same_location_returns_1():
    """Same coordinates should return proximity 1.0."""
    result = compute_geographic_proximity((34.0, -118.0), (34.0, -118.0))
    assert result == pytest.approx(1.0, abs=1e-6)


def test_compute_geographic_proximity_max_distance_returns_0():
    """Coordinates >= max_distance_miles apart should return 0.0."""
    # Seattle to San Diego is ~1,255 miles
    seattle = SPEAKER_METRO_COORDS["Seattle"]
    san_diego = UNIVERSITY_COORDS["SDSU"]
    result = compute_geographic_proximity(seattle, san_diego, max_distance_miles=600.0)
    assert result == 0.0


def test_compute_geographic_proximity_mid_distance():
    """Mid-range distance returns a value between 0 and 1."""
    la = SPEAKER_METRO_COORDS["Los Angeles"]
    sdsu = UNIVERSITY_COORDS["SDSU"]
    result = compute_geographic_proximity(la, sdsu)
    assert 0.0 < result < 1.0


# ---------- Connection data ----------

def test_build_connection_data_filters_by_threshold(sample_speakers_df: pd.DataFrame):
    """Connections are filtered by proximity threshold."""
    connections = build_connection_data(sample_speakers_df, proximity_threshold=0.3)
    for conn in connections:
        assert conn["proximity"] >= 0.3


def test_build_connection_data_empty_when_threshold_too_high(sample_speakers_df: pd.DataFrame):
    """No connections when threshold is 1.0 (only exact same location would pass)."""
    connections = build_connection_data(sample_speakers_df, proximity_threshold=1.0)
    assert len(connections) == 0


def test_build_connection_data_skips_unknown_metros():
    """Speakers with unknown metro regions are skipped."""
    df = pd.DataFrame([
        {"Name": "Unknown Person", "Metro Region": "Narnia",
         "Title": "CEO", "Company": "Fantasy"},
    ])
    connections = build_connection_data(df, proximity_threshold=0.0)
    assert len(connections) == 0


# ---------- Render map ----------

def test_render_expansion_map_returns_figure(sample_speakers_df: pd.DataFrame):
    """render_expansion_map returns a Plotly Figure."""
    fig = render_expansion_map(sample_speakers_df)
    assert isinstance(fig, go.Figure)


def test_render_expansion_map_has_speaker_traces(sample_speakers_df: pd.DataFrame):
    """Map contains traces with speaker markers (circle symbols)."""
    fig = render_expansion_map(sample_speakers_df)
    speaker_traces = [
        t for t in fig.data
        if hasattr(t, "marker") and t.marker and t.marker.symbol == "circle"
    ]
    assert len(speaker_traces) > 0


def test_render_expansion_map_has_university_traces(sample_speakers_df: pd.DataFrame):
    """Map contains traces with university markers (diamond symbols)."""
    fig = render_expansion_map(sample_speakers_df)
    uni_traces = [
        t for t in fig.data
        if hasattr(t, "marker") and t.marker and t.marker.symbol == "diamond"
    ]
    assert len(uni_traces) > 0


# ---------- Expertise clusters ----------

def test_expertise_cluster_colors_has_six_entries():
    """There should be exactly 6 expertise cluster colors."""
    assert len(EXPERTISE_CLUSTER_COLORS) == 6
