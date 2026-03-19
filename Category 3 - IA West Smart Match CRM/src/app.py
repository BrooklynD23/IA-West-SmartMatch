"""IA SmartMatch CRM — Streamlit application entry point."""

import logging

import numpy as np
import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="IA SmartMatch CRM",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.config import CACHE_DIR, has_gemini_api_key, validate_config  # noqa: E402
from src.data_loader import load_all  # noqa: E402
from src.embeddings import (  # noqa: E402
    EMBEDDING_CACHE_FILES,
    generate_embedding_lookup_dicts,
    load_embedding_lookup_dicts,
)
from src.ui.matches_tab import render_matches_tab as render_matches_tab_ui  # noqa: E402
from src.ui.discovery_tab import render_discovery_tab  # noqa: E402
from src.ui.pipeline_tab import render_pipeline_tab  # noqa: E402
from src.utils import format_course_identifier, summarize_missing_keys  # noqa: E402

logger = logging.getLogger(__name__)


def _embedding_cache_issues(
    datasets,
    speaker_embeddings: dict[str, np.ndarray],
    event_embeddings: dict[str, np.ndarray],
    course_embeddings: dict[str, np.ndarray],
) -> list[str]:
    """Return human-readable validation issues for the on-disk embedding cache."""
    issues: list[str] = []

    missing_files = [
        file_name for file_name in EMBEDDING_CACHE_FILES
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


def _resolve_embedding_lookup_dicts(
    datasets,
) -> tuple[
    dict[str, np.ndarray],
    dict[str, np.ndarray],
    dict[str, np.ndarray],
    list[str],
    str | None,
    bool,
]:
    """Load embedding caches and bootstrap them on demand when possible."""
    speaker_embeddings, event_embeddings, course_embeddings = load_embedding_lookup_dicts()
    embedding_issues = _embedding_cache_issues(
        datasets=datasets,
        speaker_embeddings=speaker_embeddings,
        event_embeddings=event_embeddings,
        course_embeddings=course_embeddings,
    )
    embedding_bootstrap_error = None
    cache_generated = False

    if embedding_issues and has_gemini_api_key():
        try:
            speaker_embeddings, event_embeddings, course_embeddings = generate_embedding_lookup_dicts(
                speakers_df=datasets.speakers,
                events_df=datasets.events,
                courses_df=datasets.courses,
            )
            cache_generated = True
        except Exception as exc:
            logger.exception("Failed to bootstrap embedding cache.")
            embedding_bootstrap_error = str(exc)

        embedding_issues = _embedding_cache_issues(
            datasets=datasets,
            speaker_embeddings=speaker_embeddings,
            event_embeddings=event_embeddings,
            course_embeddings=course_embeddings,
        )

    return (
        speaker_embeddings,
        event_embeddings,
        course_embeddings,
        embedding_issues,
        embedding_bootstrap_error,
        cache_generated and not embedding_issues,
    )


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

    with st.spinner("Preparing embedding cache..."):
        (
            speaker_embeddings,
            event_embeddings,
            course_embeddings,
            embedding_issues,
            embedding_bootstrap_error,
            cache_generated,
        ) = _resolve_embedding_lookup_dicts(datasets)

    if cache_generated:
        with st.sidebar:
            st.success("Embedding cache generated successfully for Matches.")

    if embedding_issues:
        logger.error("Embedding cache validation failed: %s", "; ".join(embedding_issues))
        with st.sidebar:
            if embedding_bootstrap_error:
                st.error(
                    "Embedding cache generation failed. Matching remains disabled until "
                    "the cache can be regenerated."
                )
            elif has_gemini_api_key():
                st.error(
                    "Embedding cache is still incomplete after automatic generation. "
                    "Matching remains disabled until the cache is regenerated."
                )
            else:
                st.error(
                    "Embedding cache missing or incomplete. Configure `GEMINI_API_KEY` "
                    "to let the app generate it automatically."
                )

    tab_matches, tab_discovery, tab_pipeline = st.tabs([
        "🎯 Matches",
        "🔍 Discovery",
        "📊 Pipeline",
    ])

    with tab_matches:
        if embedding_issues:
            st.error(
                "Embedding cache missing or incomplete. Matches can run after the app "
                "successfully generates speaker, event, and course embeddings."
            )
            with st.expander("Embedding cache validation details", expanded=True):
                for issue in embedding_issues:
                    st.write(f"- {issue}")
                if embedding_bootstrap_error:
                    st.write(f"- Automatic generation failed: {embedding_bootstrap_error}")
                elif not has_gemini_api_key():
                    st.write("- Automatic generation is unavailable until `GEMINI_API_KEY` is configured.")
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
