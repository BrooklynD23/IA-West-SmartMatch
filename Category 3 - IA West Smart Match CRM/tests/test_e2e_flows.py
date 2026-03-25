"""Playwright E2E coverage for the routed IA SmartMatch demo workspace."""

from __future__ import annotations

import os
import time
from urllib.parse import parse_qs, urlparse

import pytest
from playwright.sync_api import Page, sync_playwright

pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_E2E") == "1",
    reason="E2E tests skipped (SKIP_E2E=1). Requires a running Streamlit app on port 8501.",
)

BASE_URL = "http://localhost:8501"
TIMEOUT_MS = 60_000


@pytest.fixture(scope="module")
def browser():
    """Launch a shared browser for the routed workspace checks."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture()
def page(browser):
    """Provide an isolated page/context per test to avoid session-state leakage."""
    context = browser.new_context(viewport={"width": 1440, "height": 1600})
    page = context.new_page()
    yield page
    context.close()


def _route(page: Page) -> str | None:
    return parse_qs(urlparse(page.url).query).get("route", [None])[0]


def _wait_for_body_contains(page: Page, substrings: list[str], timeout_ms: int = TIMEOUT_MS) -> str:
    deadline = time.time() + timeout_ms / 1000
    last_text = ""
    while time.time() < deadline:
        last_text = page.locator("body").inner_text(timeout=10_000)
        if all(part in last_text for part in substrings):
            return last_text
        page.wait_for_timeout(1000)
    raise AssertionError(f"Missing text {substrings!r}. Last body sample: {last_text[:1200]!r}")


def _wait_for_route(page: Page, expected: str, timeout_ms: int = TIMEOUT_MS) -> str:
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        if _route(page) == expected:
            return page.url
        page.wait_for_timeout(500)
    raise AssertionError(f"Expected route={expected!r}, got url={page.url!r}")


def _open(page: Page, url: str) -> None:
    page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)


def _open_landing(page: Page) -> None:
    _open(page, f"{BASE_URL}/?route=landing")
    _wait_for_body_contains(page, ["Sign In", "View Demo"])
    _wait_for_route(page, "landing")


def _open_dashboard(page: Page) -> None:
    _open(page, f"{BASE_URL}/?route=dashboard&role=coordinator&demo=1")
    _wait_for_body_contains(page, ["Dashboard", "Matches", "Show Jarvis Command Center", "Campus Coverage Map"])
    _wait_for_route(page, "dashboard")


def test_landing_page_loads(page: Page) -> None:
    """Landing should render the routed CTA buttons."""
    _open_landing(page)

    assert _route(page) == "landing"
    assert page.get_by_role("button", name="Sign In").first.is_visible()
    assert page.get_by_role("button", name="View Demo").first.is_visible()


def test_sign_in_navigates_to_login(page: Page) -> None:
    """Landing Sign In should route to the login selector page."""
    _open_landing(page)

    page.get_by_role("button", name="Sign In").first.click()
    _wait_for_body_contains(page, ["Coordinator Demo Login", "Volunteer (Coming Soon)"])

    assert _route(page) == "login"
    assert "Coordinator Demo Login" in page.locator("body").inner_text()


def test_view_demo_navigates_to_dashboard(page: Page) -> None:
    """View Demo should seed coordinator demo routing and open the dashboard."""
    _open_landing(page)

    page.get_by_role("button", name="View Demo").first.click()
    body = _wait_for_body_contains(
        page,
        ["Dashboard", "Matches", "Discovery", "Show Jarvis Command Center", "Campus Coverage Map"],
    )
    final_url = _wait_for_route(page, "dashboard")

    assert "role=coordinator" in final_url
    assert "demo=1" in final_url
    assert "View Match Engine" in body


def test_workspace_navigation_reaches_all_routed_pages(page: Page) -> None:
    """The authenticated workspace row should reach every routed page."""
    _open_dashboard(page)

    nav_expectations = [
        ("Matches", "matches", ["Matches", "Select an Event"]),
        ("Discovery", "discovery", ["University Event Discovery"]),
        ("Pipeline", "pipeline", ["Engagement Pipeline"]),
        ("Analytics", "analytics", ["Analytics", "Coverage, expansion readiness, and volunteer engagement analytics."]),
        ("Match Engine", "match_engine", ["Internal Specialist Matches", "< Back to Dashboard"]),
    ]

    for button_name, expected_route, expected_text in nav_expectations:
        page.get_by_role("button", name=button_name).first.click()
        _wait_for_body_contains(page, expected_text)
        assert _route(page) == expected_route


def test_deep_link_matches_renders_matches_workspace(page: Page) -> None:
    """Direct route=matches should land on the Matches workspace."""
    _open(page, f"{BASE_URL}/?route=matches")
    body = _wait_for_body_contains(page, ["Matches", "Select an Event"])

    assert _route(page) == "matches"
    assert "Match Weights" in body


def test_deep_link_coordinator_alias_normalizes_to_dashboard(page: Page) -> None:
    """Coordinator alias routes should normalize to dashboard and keep demo=1."""
    _open(page, f"{BASE_URL}/?route=coordinator&demo=1")
    body = _wait_for_body_contains(page, ["Show Jarvis Command Center", "Campus Coverage Map"])
    final_url = _wait_for_route(page, "dashboard")

    assert "demo=1" in final_url
    assert "Campus Coverage Map" in body


def test_unknown_route_normalizes_to_landing(page: Page) -> None:
    """Unknown routes should be rewritten back to landing."""
    _open(page, f"{BASE_URL}/?route=unknown")
    _wait_for_body_contains(page, ["Sign In", "View Demo"])

    assert _route(page) == "landing"


def test_jarvis_command_center_supports_text_commands(page: Page) -> None:
    """Jarvis should open from the dashboard checkbox and produce a discovery proposal."""
    _open_dashboard(page)

    page.locator(
        "label[data-baseweb='checkbox']",
        has_text="Show Jarvis Command Center",
    ).first.click(timeout=10_000)
    _wait_for_body_contains(page, ["Jarvis -- Voice Command Center", "Send Command"])

    page.get_by_role("textbox", name="Command").fill("Find new events")
    page.get_by_role("button", name="Send Command").click()
    body = _wait_for_body_contains(page, ["Scrape universities for new events", "Approve", "Reject"])

    assert "Discovery Agent" in body


def test_sign_out_returns_to_landing(page: Page) -> None:
    """Workspace sign-out should clear demo routing without a Streamlit widget-state error."""
    _open_dashboard(page)

    page.get_by_role("button", name="Sign Out").first.click()
    body = _wait_for_body_contains(page, ["Sign In", "View Demo"])

    assert _route(page) == "landing"
    assert "StreamlitAPIException" not in body
