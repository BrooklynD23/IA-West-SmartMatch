"""Demo mode fixture dispatch for offline demos (A3.5).

Provides a toggle between cached fixture data and live API calls,
with artificial delays for a polished demo experience.
"""

import json
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from src.config import CACHE_DIR

DEMO_FIXTURES_DIR: Path = CACHE_DIR / "demo_fixtures"


def load_fixture(key: str) -> Any:
    """Load a JSON fixture by key from the demo fixtures directory.

    Args:
        key: Fixture name (without .json extension).

    Returns:
        Parsed JSON content (dict or list).

    Raises:
        FileNotFoundError: If the fixture file does not exist.
        ValueError: If the key resolves outside the fixtures directory.
    """
    path = (DEMO_FIXTURES_DIR / f"{key}.json").resolve()
    if not str(path).startswith(str(DEMO_FIXTURES_DIR.resolve())):
        raise ValueError(f"Invalid fixture key: {key}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def init_demo_mode() -> None:
    """Initialize demo_mode in session state if not already set."""
    if "demo_mode" not in st.session_state:
        st.session_state["demo_mode"] = False


def demo_or_live(
    func: Callable[..., Any],
    *args: Any,
    fixture_key: str,
    **kwargs: Any,
) -> Any:
    """Dispatch between cached fixture and live function call.

    In demo mode, returns the cached fixture for the given key.
    In live mode, calls func with the provided positional and keyword args.

    Args:
        func: The live function to call when not in demo mode.
        *args: Positional arguments forwarded to func.
        fixture_key: Key identifying which fixture file to load.
        **kwargs: Keyword arguments forwarded to func.

    Returns:
        Fixture data (demo mode) or result of func (live mode).
    """
    if st.session_state.get("demo_mode", False):
        return load_fixture(fixture_key)
    return func(*args, **kwargs)
