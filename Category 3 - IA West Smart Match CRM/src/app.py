"""IA SmartMatch CRM — Streamlit application entry point."""

import logging
import pickle  # noqa: S403

import numpy as np
import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="IA SmartMatch CRM",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.config import CACHE_DIR, validate_config  # noqa: E402
from src.data_loader import load_all  # noqa: E402
from src.ui.matches_tab import render_matches_tab as render_matches_tab_ui  # noqa: E402
from src.utils import format_course_identifier, summarize_missing_keys  # noqa: E402

logger = logging.getLogger(__name__)

_REQUIRED_EMBEDDING_CACHE_FILES = (
    "speaker_embeddings.npy",
    "speaker_metadata.pkl",
    "event_embeddings.npy",
    "event_metadata.pkl",
    "course_embeddings.npy",
    "course_metadata.pkl",
)


# ── Embedding loader ─────────────────────────────────────────────────────────

def _load_embedding_dicts() -> tuple[dict, dict, dict]:
    """
    Load cached embeddings from disk and build name->embedding lookup dicts.

    Missing or incomplete caches are validated separately before the Matches
    tab is rendered so matching does not silently degrade.
    """
    speaker_embs: dict[str, np.ndarray] = {}
    event_embs: dict[str, np.ndarray] = {}
    course_embs: dict[str, np.ndarray] = {}

    # Speaker embeddings
    speaker_emb_path = CACHE_DIR / "speaker_embeddings.npy"
    speaker_meta_path = CACHE_DIR / "speaker_metadata.pkl"
    if speaker_emb_path.exists() and speaker_meta_path.exists():
        try:
            embeddings = np.load(speaker_emb_path)
            with open(speaker_meta_path, "rb") as f:
                metadata = pickle.load(f)  # noqa: S301
            for i, meta in enumerate(metadata):
                speaker_embs[meta["name"]] = embeddings[i]
            logger.info("Loaded %d speaker embeddings.", len(speaker_embs))
        except Exception:
            logger.exception("Failed to load speaker embeddings from cache.")

    # Event embeddings
    event_emb_path = CACHE_DIR / "event_embeddings.npy"
    event_meta_path = CACHE_DIR / "event_metadata.pkl"
    if event_emb_path.exists() and event_meta_path.exists():
        try:
            embeddings = np.load(event_emb_path)
            with open(event_meta_path, "rb") as f:
                metadata = pickle.load(f)  # noqa: S301
            for i, meta in enumerate(metadata):
                event_embs[meta["event_name"]] = embeddings[i]
            logger.info("Loaded %d event embeddings.", len(event_embs))
        except Exception:
            logger.exception("Failed to load event embeddings from cache.")

    # Course embeddings
    course_emb_path = CACHE_DIR / "course_embeddings.npy"
    course_meta_path = CACHE_DIR / "course_metadata.pkl"
    if course_emb_path.exists() and course_meta_path.exists():
        try:
            embeddings = np.load(course_emb_path)
            with open(course_meta_path, "rb") as f:
                metadata = pickle.load(f)  # noqa: S301
            for i, meta in enumerate(metadata):
                key = format_course_identifier(
                    meta.get("course"),
                    meta.get("section"),
                )
                course_embs[key] = embeddings[i]
            logger.info("Loaded %d course embeddings.", len(course_embs))
        except Exception:
            logger.exception("Failed to load course embeddings from cache.")

    return speaker_embs, event_embs, course_embs


def _embedding_cache_issues(
    datasets,
    speaker_embeddings: dict[str, np.ndarray],
    event_embeddings: dict[str, np.ndarray],
    course_embeddings: dict[str, np.ndarray],
) -> list[str]:
    """Return human-readable validation issues for the on-disk embedding cache."""
    issues: list[str] = []

    missing_files = [
        file_name for file_name in _REQUIRED_EMBEDDING_CACHE_FILES
        if not (CACHE_DIR / file_name).exists()
    ]
    if missing_files:
        issues.append(f"Missing cache files: {', '.join(missing_files)}.")

    speaker_missing_count, speaker_examples = summarize_missing_keys(
        datasets.speakers["Name"],
        speaker_embeddings.keys(),
    )
    if speaker_missing_count:
        issues.append(
            "Speaker embedding coverage is incomplete: "
            f"{speaker_missing_count} missing"
            f"{' (examples: ' + ', '.join(speaker_examples) + ')' if speaker_examples else ''}."
        )

    event_missing_count, event_examples = summarize_missing_keys(
        datasets.events["Event / Program"],
        event_embeddings.keys(),
    )
    if event_missing_count:
        issues.append(
            "Event embedding coverage is incomplete: "
            f"{event_missing_count} missing"
            f"{' (examples: ' + ', '.join(event_examples) + ')' if event_examples else ''}."
        )

    expected_course_keys = (
        format_course_identifier(row.get("Course"), row.get("Section"))
        for _, row in datasets.courses.iterrows()
    )
    course_missing_count, course_examples = summarize_missing_keys(
        expected_course_keys,
        course_embeddings.keys(),
    )
    if course_missing_count:
        issues.append(
            "Course embedding coverage is incomplete: "
            f"{course_missing_count} missing"
            f"{' (examples: ' + ', '.join(course_examples) + ')' if course_examples else ''}."
        )

    return issues


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
            logger.exception("Failed to load datasets.")
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

    speaker_embeddings, event_embeddings, course_embeddings = _load_embedding_dicts()
    embedding_issues = _embedding_cache_issues(
        datasets=datasets,
        speaker_embeddings=speaker_embeddings,
        event_embeddings=event_embeddings,
        course_embeddings=course_embeddings,
    )
    if embedding_issues:
        logger.error("Embedding cache validation failed: %s", "; ".join(embedding_issues))
        with st.sidebar:
            st.error("Embedding cache missing or incomplete. Matching is disabled until the cache is regenerated.")

    tab_matches, tab_discovery, tab_pipeline = st.tabs([
        "🎯 Matches",
        "🔍 Discovery",
        "📊 Pipeline",
    ])

    with tab_matches:
        if embedding_issues:
            st.error(
                "Embedding cache missing or incomplete. Regenerate and ship the "
                "speaker, event, and course embeddings before using Matches."
            )
            with st.expander("Embedding cache validation details", expanded=True):
                for issue in embedding_issues:
                    st.write(f"- {issue}")
        else:
            render_matches_tab_ui(
                events=datasets.events,
                courses=datasets.courses,
                speakers=datasets.speakers,
                speaker_embeddings=speaker_embeddings,
                event_embeddings=event_embeddings,
                course_embeddings=course_embeddings,
                ia_event_calendar=datasets.calendar,
            )

    with tab_discovery:
        render_discovery_tab(datasets)

    with tab_pipeline:
        render_pipeline_tab(datasets)


if __name__ == "__main__":
    main()
