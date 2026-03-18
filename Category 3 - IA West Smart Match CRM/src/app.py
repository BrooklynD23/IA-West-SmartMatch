"""IA SmartMatch CRM — Streamlit application entry point."""

import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="IA SmartMatch CRM",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.config import validate_config  # noqa: E402
from src.data_loader import load_all  # noqa: E402


# ── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar():
    """Render the sidebar with IA West branding and navigation."""
    with st.sidebar:
        st.markdown("## IA SmartMatch")
        st.markdown("**AI-Orchestrated Speaker-Event Matching**")
        st.markdown("*Insights Association — West Chapter*")
        st.divider()

        st.markdown("### About")
        st.markdown(
            "SmartMatch uses AI to discover university engagement "
            "opportunities, match them with the right IA West board "
            "member volunteers, and track the engagement-to-membership pipeline."
        )
        st.divider()

        st.markdown("### Data Summary")
        return st.container()


# ── Tab: Matches ────────────────────────────────────────────────────────────

def render_matches_tab(datasets) -> None:
    """Render the Matches tab with speaker-event matching interface."""
    st.header("Speaker-Event Matches")
    st.info(
        "Select an event to see the top recommended speakers. "
        "Matching engine will be activated in Sprint 1."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Speaker Profiles")
        st.dataframe(
            datasets.speakers,
            use_container_width=True,
            hide_index=True,
        )

    with col2:
        st.subheader("CPP Events")
        display_cols = ["Event / Program", "Category", "Volunteer Roles (fit)", "Primary Audience"]
        available_cols = [c for c in display_cols if c in datasets.events.columns]
        st.dataframe(
            datasets.events[available_cols],
            use_container_width=True,
            hide_index=True,
        )


# ── Tab: Discovery ──────────────────────────────────────────────────────────

def render_discovery_tab(datasets) -> None:
    """Render the Discovery tab for university event scanning."""
    st.header("University Event Discovery")
    st.info(
        "Automated university event discovery will be activated in Sprint 2. "
        "Web scraping + LLM extraction pipeline."
    )

    st.subheader("IA West Event Calendar")
    st.dataframe(
        datasets.calendar,
        use_container_width=True,
        hide_index=True,
    )


# ── Tab: Pipeline ───────────────────────────────────────────────────────────

def render_pipeline_tab(datasets) -> None:
    """Render the Pipeline tab with engagement funnel tracking."""
    st.header("Engagement Pipeline")
    st.info(
        "Pipeline funnel visualization will be activated in Sprint 2. "
        "Tracks: Discovered -> Matched -> Contacted -> Confirmed -> Attended -> Member Inquiry."
    )

    st.subheader("Course Schedule (Guest Lecture Opportunities)")
    st.dataframe(
        datasets.courses,
        use_container_width=True,
        hide_index=True,
    )


# ── Main App ────────────────────────────────────────────────────────────────

def main() -> None:
    """Main application entry point."""
    config_errors = validate_config()
    if config_errors:
        st.error("Configuration errors detected:")
        for error in config_errors:
            st.error(f"  - {error}")
        st.stop()

    sidebar_container = render_sidebar()

    with st.spinner("Loading data..."):
        try:
            datasets = load_all()
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            st.stop()
            return

    with sidebar_container:
        st.metric("Speakers", len(datasets.speakers))
        st.metric("Events", len(datasets.events))
        st.metric("Courses", len(datasets.courses))
        st.metric("Calendar Entries", len(datasets.calendar))
        total = sum(len(df) for df in [
            datasets.speakers, datasets.events,
            datasets.courses, datasets.calendar,
        ])
        st.metric("Total Records", total)

    all_issues = []
    for qr in datasets.quality_results:
        all_issues.extend(qr.issues)
    if all_issues:
        with st.sidebar:
            with st.expander("Data Quality Warnings", expanded=False):
                for issue in all_issues:
                    st.warning(issue)

    tab_matches, tab_discovery, tab_pipeline = st.tabs([
        "🎯 Matches",
        "🔍 Discovery",
        "📊 Pipeline",
    ])

    with tab_matches:
        render_matches_tab(datasets)

    with tab_discovery:
        render_discovery_tab(datasets)

    with tab_pipeline:
        render_pipeline_tab(datasets)


if __name__ == "__main__":
    main()
