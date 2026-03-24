"""
Custom CSS for IA SmartMatch — Academic Curator Design System.

Design tokens extracted from Stitch mockups (docs/mockup/).
Inject at the top of the main app file via st.markdown(..., unsafe_allow_html=True).
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

import streamlit as st

logger = logging.getLogger(__name__)

# ── Academic Curator Brand Colors ─────────────────────────────────────
BRAND_PRIMARY: str = "#005394"
BRAND_PRIMARY_CONTAINER: str = "#2b6cb0"
BRAND_ON_PRIMARY: str = "#ffffff"
BRAND_ON_SURFACE: str = "#191c1e"

# ── Custom CSS ──────────────────────────────────────────────────────
CUSTOM_CSS: str = """
<style>
/* ---------- Google Fonts ---------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Tight:wght@600;700;800&display=swap');

/* ---------- Academic Curator Design Tokens ---------- */
:root {
    /* Surface Hierarchy (tonal layering, NO borders) */
    --surface:                  #f7f9fc;
    --surface-container-low:    #f2f4f7;
    --surface-container:        #eceef1;
    --surface-container-lowest: #ffffff;
    --surface-container-high:   #e6e8eb;
    --surface-container-highest:#e0e3e6;

    /* Brand Colors */
    --primary:                  #005394;
    --primary-container:        #2b6cb0;
    --on-primary:               #ffffff;
    --on-surface:               #191c1e;
    --on-surface-variant:       #414750;
    --outline-variant:          #c1c7d2;
    --secondary:                #545f72;
    --secondary-fixed:          #d8e3fa;

    /* Semantic */
    --success:                  #059669;
    --danger:                   #DC2626;
    --accent:                   #F59E0B;
    --intent-badge-color:       #F59E0B;

    /* Typography */
    --font-headline:            'Inter Tight', sans-serif;
    --font-body:                'Inter', sans-serif;

    /* Radii */
    --radius-card:              24px;
    --radius-button:            12px;
    --radius-pill:              9999px;

    /* Signature Effects */
    --hero-gradient:            linear-gradient(135deg, #005394, #2b6cb0);
    --ambient-shadow:           0 12px 40px rgba(25, 28, 30, 0.06);
}

/* ---------- Global Typography ---------- */
html, body, [class*="stApp"] {
    font-family: var(--font-body) !important;
    color: var(--on-surface);
}

h1, h2, h3 {
    font-family: var(--font-headline) !important;
    color: var(--on-surface) !important;
}

/* ---------- Match Card Styling ---------- */
div[data-testid="stExpander"] {
    background-color: var(--surface-container-lowest);
    border: none;
    border-radius: var(--radius-card);
    margin-bottom: 12px;
    box-shadow: var(--ambient-shadow);
}

div[data-testid="stExpander"] summary {
    font-weight: 600;
    font-family: var(--font-headline);
    color: var(--primary);
}

/* ---------- Metric Card Enhancement ---------- */
div[data-testid="stMetric"] {
    background-color: var(--surface-container-lowest);
    border-radius: 16px;
    padding: 12px 16px;
    border-left: 4px solid var(--primary);
    box-shadow: var(--ambient-shadow);
}

div[data-testid="stMetric"] label {
    color: var(--on-surface-variant);
    font-family: var(--font-body);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--primary);
    font-family: var(--font-headline);
    font-size: 1.5rem;
    font-weight: 700;
}

/* ---------- Sidebar Branding ---------- */
section[data-testid="stSidebar"] {
    background-color: var(--surface-container-low);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--primary) !important;
    font-family: var(--font-headline) !important;
}

/* ---------- Tab Styling ---------- */
button[data-baseweb="tab"] {
    font-weight: 600;
    font-family: var(--font-body);
    color: var(--on-surface-variant);
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary);
    border-bottom: 3px solid var(--primary);
}

/* ---------- Button Styling ---------- */
button[kind="primary"] {
    background: var(--hero-gradient);
    border: none;
    border-radius: var(--radius-button);
}

button[kind="primary"]:hover {
    opacity: 0.9;
}

/* ---------- Email Preview Card ---------- */
.email-preview {
    background-color: var(--surface-container-lowest);
    border-radius: var(--radius-card);
    padding: 16px;
    font-family: Georgia, serif;
    line-height: 1.6;
    box-shadow: var(--ambient-shadow);
}

.email-preview .subject-line {
    font-weight: 700;
    color: var(--primary);
    font-family: var(--font-headline);
    font-size: 1.1rem;
    margin-bottom: 8px;
    padding-bottom: 8px;
}

/* ---------- Score Badge ---------- */
.score-badge {
    display: inline-block;
    background: var(--hero-gradient);
    color: var(--on-primary);
    font-size: 1.8rem;
    font-weight: 800;
    font-family: var(--font-headline);
    padding: 8px 16px;
    border-radius: var(--radius-button);
    text-align: center;
    min-width: 80px;
}

.score-badge.high   { background: var(--success); }
.score-badge.medium { background: var(--accent);  }
.score-badge.low    { background: var(--danger);  }

/* ---------- Explanation Card ---------- */
.explanation-card {
    background-color: var(--surface-container-lowest);
    border-left: 4px solid var(--primary);
    border-radius: 0 var(--radius-card) var(--radius-card) 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-style: italic;
    color: var(--on-surface-variant);
    line-height: 1.5;
    box-shadow: var(--ambient-shadow);
}

/* ---------- Loading State ---------- */
.stSpinner {
    color: var(--primary);
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

/* ---------- Command Center: Voice Panel ---------- */
.voice-panel {
    background: var(--surface-container-lowest);
    border-radius: var(--radius-card);
    padding: 16px;
    margin-bottom: 24px;
    box-shadow: var(--ambient-shadow);
}

/* ---------- Command Center: Chat Bubbles ---------- */
.chat-container {
    max-height: 480px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 16px;
    background: var(--surface);
}

.chat-bubble {
    max-width: 72%;
    padding: 8px 16px;
    border-radius: 16px;
    background: var(--surface-container-lowest);
    box-shadow: var(--ambient-shadow);
    font-family: var(--font-body);
    font-size: 16px;
    line-height: 1.5;
}

.chat-bubble.coordinator {
    align-self: flex-start;
    border: 1px solid var(--outline-variant);
}

.chat-bubble.jarvis {
    align-self: flex-end;
    border-left: 3px solid var(--primary);
}

.chat-meta {
    font-size: 13px;
    font-weight: 400;
    color: var(--secondary);
    margin-top: 4px;
    font-family: var(--font-body);
}

.intent-badge {
    display: inline-block;
    background: var(--intent-badge-color);
    color: #ffffff;
    font-size: 13px;
    font-weight: 400;
    padding: 4px 8px;
    border-radius: var(--radius-pill);
    margin-left: 8px;
}

/* ---------- Command Center: Mic Button ---------- */
@keyframes mic-pulse {
    0% { box-shadow: 0 0 0 0 rgba(0, 83, 148, 0.4); }
    100% { box-shadow: 0 0 0 12px transparent; }
}

.mic-button-active {
    animation: mic-pulse 1.5s ease-out infinite;
    border: 2px solid var(--primary);
}

/* ---------- Swimlane Dashboard ---------- */
.swimlane-card {
    border: 1px solid var(--outline-variant);
    border-radius: 8px;
    padding: 8px;
    background-color: var(--surface-container-lowest);
    box-shadow: var(--ambient-shadow);
    min-height: 80px;
}

.swimlane-card.status-running  { border-color: var(--primary); }
.swimlane-card.status-awaiting { border-color: var(--accent); }
.swimlane-card.status-completed { border-color: var(--success); }
.swimlane-card.status-failed    { border-color: var(--danger); }

.swimlane-status {
    font-family: var(--font-body);
    font-size: 13px;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.swimlane-compact {
    font-family: var(--font-body);
    font-size: 13px;
    color: var(--success);
    padding: 4px 8px;
}
</style>
"""


def inject_custom_css() -> None:
    """Inject the CUSTOM_CSS into the Streamlit app via st.markdown."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@contextmanager
def api_call_spinner(message: str = "Processing...") -> Generator[None, None, None]:
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
            logger.error("API call failed: %s", e)
            st.error(
                "An error occurred. Please try again or switch to Demo Mode."
            )
            raise


def render_error_card(title: str, message: str, suggestion: str = "") -> None:
    """Display a styled error card with optional recovery suggestion."""
    st.error(f"**{title}**")
    st.markdown(f"> {message}")
    if suggestion:
        st.info(f"Suggestion: {suggestion}")
