"""Discovery tab UI component for IA SmartMatch CRM.

Provides university event discovery via web scraping + LLM extraction,
results display, and integration with the Matches tab.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import pandas as pd
import streamlit as st

from src.demo_mode import demo_or_live
from src.extraction.llm_extractor import extract_events
from src.runtime_state import init_runtime_state
from src.scraping.scraper import (
    UNIVERSITY_TARGETS,
    load_from_cache,
    scrape_university,
    validate_public_demo_url,
)

logger = logging.getLogger(__name__)

MATCHING_POOL_FLASH_KEY = "matching_pool_flash"


# ---------------------------------------------------------------------------
# Pure helpers (testable without Streamlit)
# ---------------------------------------------------------------------------


def transform_event_for_matching(
    extracted: dict[str, Any],
    university: str,
) -> dict[str, Any]:
    """Convert an extracted event dict into the format used by the Matches tab.

    Parameters
    ----------
    extracted:
        Event dict from the LLM extractor.
    university:
        Name of the source university.

    Returns
    -------
    dict compatible with the matching engine's event row expectations.
    """
    roles = extracted.get("volunteer_roles", [])
    roles_str = ", ".join(roles) if isinstance(roles, list) else str(roles)
    date_or_recurrence = extracted.get("date_or_recurrence", "")
    contact_name = extracted.get("contact_name")
    contact_email = extracted.get("contact_email")
    url = extracted.get("url", "")
    event_name = extracted.get("event_name", "Unknown Event")
    event_id = _build_discovered_event_id(extracted, university=university)

    return {
        "event_id": event_id,
        "Event / Program": event_name,
        "Category": extracted.get("category", "other"),
        "Volunteer Roles (fit)": roles_str,
        "Primary Audience": extracted.get("primary_audience", ""),
        "Host / Unit": university,
        "Event Region": _discovered_event_region(university),
        "Recurrence (typical)": date_or_recurrence,
        "Public URL": url,
        "Point(s) of Contact (published)": contact_name,
        "Contact Email / Phone (published)": contact_email,
        "Date": date_or_recurrence,
        "Contact Name": contact_name,
        "Contact Email": contact_email,
        "URL": url,
        "Event Text": _compose_discovered_event_text(extracted),
        "Discovery University": university,
        "source": "discovery",
    }


def _compose_discovered_event_text(extracted: dict[str, Any]) -> str:
    """Compose fallback topic-scoring text for a discovered event."""
    roles = extracted.get("volunteer_roles", [])
    role_text = ", ".join(roles) if isinstance(roles, list) else str(roles)
    parts = [
        str(extracted.get("event_name", "") or ""),
        str(extracted.get("category", "") or ""),
        role_text,
        str(extracted.get("primary_audience", "") or ""),
    ]
    return " ".join(part for part in parts if part.strip())


def _build_discovered_event_id(
    extracted: dict[str, Any],
    university: str,
) -> str:
    """Return a stable ID for a discovered event."""
    payload = "|".join(
        [
            university.strip().lower(),
            str(extracted.get("event_name", "") or "").strip().lower(),
            str(extracted.get("date_or_recurrence", "") or "").strip().lower(),
            str(extracted.get("url", "") or "").strip().lower(),
        ]
    )
    return f"disc-{hashlib.sha1(payload.encode('utf-8')).hexdigest()[:12]}"


def _discovered_event_region(university: str) -> str:
    """Return the best-known metro region for a discovered university source."""
    return UNIVERSITY_TARGETS.get(university, {}).get("region", university)


def _merge_discovered_events(
    existing: list[dict[str, Any]],
    new_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Merge discovered rows by stable ID while preserving order."""
    merged = [row for row in existing if isinstance(row, dict)]
    index_by_id = {
        str(row.get("event_id") or row.get("Event / Program") or ""): index
        for index, row in enumerate(merged)
    }
    added_count = 0

    for row in new_rows:
        event_id = str(row.get("event_id") or row.get("Event / Program") or "")
        if not event_id:
            continue
        if event_id in index_by_id:
            merged[index_by_id[event_id]] = row
            continue
        index_by_id[event_id] = len(merged)
        merged.append(row)
        added_count += 1

    return merged, added_count


def add_discovered_events_to_matching_pool(
    discovered: list[dict[str, Any]],
    university: str,
) -> int:
    """Persist discovered events for the Matches tab and queue a flash message."""
    matching_events = [
        transform_event_for_matching(event, university=university)
        for event in discovered
    ]
    existing = st.session_state.get("matching_discovered_events", [])
    merged_events, added_count = _merge_discovered_events(existing, matching_events)
    st.session_state["matching_discovered_events"] = merged_events
    st.session_state[MATCHING_POOL_FLASH_KEY] = (
        f"Added {added_count} event(s) to matching pool."
    )
    return added_count


def validate_custom_url(url: str) -> str | None:
    """Validate a custom URL for scraping.

    Returns
    -------
    None if valid, or an error message string if invalid.
    """
    try:
        validate_public_demo_url(url)
        return None
    except ValueError as exc:
        return str(exc)


@st.cache_data(ttl=300, show_spinner=False)
def _cached_validate_custom_url(url: str) -> str | None:
    """Cache-wrapped URL validation to avoid DNS lookup on every keystroke."""
    return validate_custom_url(url)


def format_events_for_dataframe(
    events: list[dict[str, Any]],
) -> pd.DataFrame:
    """Format extracted event dicts into a display-friendly DataFrame.

    Parameters
    ----------
    events:
        List of event dicts from the LLM extractor.

    Returns
    -------
    DataFrame with human-readable columns for display.
    """
    if not events:
        return pd.DataFrame(
            columns=["Event Name", "Category", "Date", "Roles Needed",
                     "Audience", "Contact", "URL"]
        )

    rows: list[dict[str, str]] = []
    for ev in events:
        roles = ev.get("volunteer_roles", [])
        roles_str = ", ".join(roles) if isinstance(roles, list) else str(roles)
        contact_parts = [
            p for p in [ev.get("contact_name"), ev.get("contact_email")]
            if p
        ]
        contact_str = " / ".join(contact_parts) if contact_parts else ""

        rows.append({
            "Event Name": ev.get("event_name", ""),
            "Category": ev.get("category", ""),
            "Date": ev.get("date_or_recurrence", ""),
            "Roles Needed": roles_str,
            "Audience": ev.get("primary_audience", ""),
            "Contact": contact_str,
            "URL": ev.get("url", ""),
        })

    return pd.DataFrame(rows)


def discovery_cache_status(url: str) -> tuple[str, str]:
    """Return the status label and user-facing message for a discovery URL."""
    cached = load_from_cache(url, allow_expired=True)
    if cached is None:
        return "Ready", "No cache yet. A live scrape will run."
    if cached.get("is_stale"):
        return "Stale Cache", f"Cached scrape from {cached.get('scraped_at', 'unknown time')}."
    return "Cached", f"Fresh cache from {cached.get('scraped_at', 'unknown time')}."


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------


def _run_discovery(
    url: str,
    method: str,
    university: str,
) -> tuple[str, list[dict[str, Any]]]:
    """Scrape a URL and extract events, showing progress in Streamlit."""
    def _live_discovery() -> dict[str, Any]:
        with st.spinner(f"Scraping {university}..."):
            try:
                result = scrape_university(url=url, method=method)
            except PermissionError as exc:
                st.error(f"Blocked by robots.txt: {exc}")
                return {"university": university, "events": []}
            except Exception as exc:
                st.error(f"Scraping failed: {exc}")
                logger.error("Scrape error for %s: %s", url, exc)
                return {"university": university, "events": []}

        html = result.get("html", "")
        source = result.get("source", "live")
        if source == "cache":
            st.info("Using cached scrape result.")
        elif source == "stale_cache":
            st.warning(
                result.get(
                    "message",
                    "Live scrape unavailable. Showing cached results.",
                )
            )
        elif result.get("message"):
            st.info(str(result["message"]))

        with st.spinner("Extracting events with AI..."):
            try:
                events = extract_events(
                    raw_html=html,
                    university=university,
                    url=url,
                    prefer_cache=True,
                )
            except Exception as exc:
                st.error(f"Extraction failed: {exc}")
                logger.error("Extraction error for %s: %s", url, exc)
                return {"university": university, "events": []}
        return {"university": university, "events": events}

    payload = demo_or_live(
        _live_discovery,
        fixture_key="discovery_scan",
    )
    if st.session_state.get("demo_mode", False):
        st.info("Demo Mode is using cached discovery results.")

    discovered_university = university
    events: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        discovered_university = str(payload.get("university", university))
        raw_events = payload.get("events", [])
        if isinstance(raw_events, list):
            events = raw_events

    if events:
        st.success(f"Found {len(events)} event(s).")
    else:
        st.warning(
            "Could not extract events from this page. The page may not contain "
            "recognizable event listings."
        )

    return discovered_university, events


def render_discovery_tab(datasets: Any) -> None:
    """Render the Discovery tab for university event scanning.

    Parameters
    ----------
    datasets:
        The loaded datasets object (must have a `calendar` attribute).
    """
    st.header("University Event Discovery")
    init_runtime_state()
    flash_message = st.session_state.pop(MATCHING_POOL_FLASH_KEY, None)
    if flash_message:
        st.success(str(flash_message))

    # --- University selector ---
    uni_names = list(UNIVERSITY_TARGETS.keys())
    selected_uni = st.selectbox(
        "Select University",
        options=uni_names,
        index=0,
        key="discovery_university",
    )
    uni_cfg = UNIVERSITY_TARGETS[selected_uni]

    col_discover, col_status = st.columns([2, 4])
    with col_discover:
        discover_clicked = st.button(
            "Discover Events",
            key="discover_events_btn",
        )
    with col_status:
        status_label, status_message = discovery_cache_status(uni_cfg["url"])
        st.caption(f"Status: {status_label}")
        st.caption(status_message)

    # --- Run discovery on button click ---
    if discover_clicked:
        discovered_university, events = _run_discovery(
            url=uni_cfg["url"],
            method=uni_cfg["method"],
            university=selected_uni,
        )
        st.session_state["discovered_events"] = events
        st.session_state["discovered_university"] = discovered_university
        st.session_state["scraped_events"] = [
            {**event, "university": discovered_university}
            for event in events
        ]

    # --- Display results ---
    discovered = st.session_state.get("discovered_events", [])
    if discovered:
        st.subheader(
            f"Discovered Events — "
            f"{st.session_state.get('discovered_university', '')}"
        )
        df = format_events_for_dataframe(discovered)
        st.dataframe(df, use_container_width=True, hide_index=True)

        if st.button("Add to Matching", key="add_to_matching_btn"):
            uni = st.session_state.get("discovered_university", "")
            add_discovered_events_to_matching_pool(discovered, university=uni)
            st.rerun()

    # --- Custom URL input ---
    st.divider()
    st.subheader("Custom University URL")
    custom_url = st.text_input(
        "Enter a .edu URL to scan",
        placeholder="https://example.edu/events",
        key="custom_discovery_url",
    )
    if custom_url:
        error = _cached_validate_custom_url(custom_url)
        if error:
            st.error(f"Invalid URL: {error}")
        else:
            st.success("URL is valid.")
            if st.button("Scan Custom URL", key="scan_custom_url_btn"):
                discovered_university, events = _run_discovery(
                    url=custom_url,
                    method="bs4",
                    university="Custom",
                )
                st.session_state["discovered_events"] = events
                st.session_state["discovered_university"] = discovered_university
                st.session_state["scraped_events"] = [
                    {**event, "university": discovered_university}
                    for event in events
                ]
                st.rerun()

    # --- IA West Event Calendar ---
    st.divider()
    st.subheader("IA West Event Calendar")
    st.dataframe(
        datasets.calendar,
        use_container_width=True,
        hide_index=True,
    )
