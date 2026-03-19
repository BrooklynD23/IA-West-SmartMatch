"""Shared test fixtures and mocks for the test suite."""

import sys
import types
from contextlib import contextmanager
from unittest.mock import MagicMock

# Mock streamlit before any src module can import it
if "streamlit" not in sys.modules:
    _mock_st = types.ModuleType("streamlit")
    _mock_st.markdown = MagicMock()  # type: ignore[attr-defined]
    _mock_st.error = MagicMock()  # type: ignore[attr-defined]
    _mock_st.info = MagicMock()  # type: ignore[attr-defined]
    _mock_st.warning = MagicMock()  # type: ignore[attr-defined]
    _mock_st.success = MagicMock()  # type: ignore[attr-defined]
    _mock_st.write = MagicMock()  # type: ignore[attr-defined]
    _mock_st.set_page_config = MagicMock()  # type: ignore[attr-defined]
    _mock_st.sidebar = MagicMock()  # type: ignore[attr-defined]
    _mock_st.columns = MagicMock()  # type: ignore[attr-defined]
    _mock_st.tabs = MagicMock()  # type: ignore[attr-defined]
    _mock_st.metric = MagicMock()  # type: ignore[attr-defined]
    _mock_st.expander = MagicMock()  # type: ignore[attr-defined]
    _mock_st.selectbox = MagicMock()  # type: ignore[attr-defined]
    _mock_st.text_input = MagicMock()  # type: ignore[attr-defined]
    _mock_st.button = MagicMock()  # type: ignore[attr-defined]
    _mock_st.radio = MagicMock()  # type: ignore[attr-defined]
    _mock_st.session_state = {}  # type: ignore[attr-defined]
    _mock_st.rerun = MagicMock()  # type: ignore[attr-defined]
    _mock_st.caption = MagicMock()  # type: ignore[attr-defined]
    _mock_st.subheader = MagicMock()  # type: ignore[attr-defined]
    _mock_st.header = MagicMock()  # type: ignore[attr-defined]
    _mock_st.slider = MagicMock()  # type: ignore[attr-defined]
    _mock_st.checkbox = MagicMock()  # type: ignore[attr-defined]
    _mock_st.container = MagicMock()  # type: ignore[attr-defined]
    _mock_st.divider = MagicMock()  # type: ignore[attr-defined]
    _mock_st.stop = MagicMock()  # type: ignore[attr-defined]
    _mock_st.dataframe = MagicMock()  # type: ignore[attr-defined]
    _mock_st.plotly_chart = MagicMock()  # type: ignore[attr-defined]
    _mock_st.cache_data = lambda f=None, **kw: f if f else (lambda fn: fn)  # type: ignore[attr-defined]
    _mock_st.cache_resource = lambda f=None, **kw: f if f else (lambda fn: fn)  # type: ignore[attr-defined]

    @contextmanager
    def _fake_spinner(msg: str = ""):
        yield

    _mock_st.spinner = _fake_spinner  # type: ignore[attr-defined]

    sys.modules["streamlit"] = _mock_st
