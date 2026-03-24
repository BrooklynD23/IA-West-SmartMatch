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
    _mock_st.text = MagicMock()  # type: ignore[attr-defined]
    _mock_st.code = MagicMock()  # type: ignore[attr-defined]
    _mock_st.set_page_config = MagicMock()  # type: ignore[attr-defined]
    _mock_st.sidebar = MagicMock()  # type: ignore[attr-defined]
    # columns() returns a list of MagicMocks so callers can unpack: a, b = st.columns(2)
    def _fake_columns(n, *args, **kwargs):
        count = n if isinstance(n, int) else len(n)
        return [MagicMock() for _ in range(count)]
    _mock_st.columns = MagicMock(side_effect=_fake_columns)  # type: ignore[attr-defined]
    _mock_st.tabs = MagicMock()  # type: ignore[attr-defined]
    _mock_st.metric = MagicMock()  # type: ignore[attr-defined]
    @contextmanager
    def _fake_expander(*args, **kwargs):
        yield MagicMock()
    _mock_st.expander = MagicMock(side_effect=_fake_expander)  # type: ignore[attr-defined]
    _mock_st.selectbox = MagicMock()  # type: ignore[attr-defined]
    _mock_st.text_input = MagicMock()  # type: ignore[attr-defined]
    _mock_st.button = MagicMock(return_value=False)  # type: ignore[attr-defined]
    _mock_st.download_button = MagicMock()  # type: ignore[attr-defined]
    _mock_st.radio = MagicMock()  # type: ignore[attr-defined]
    _mock_st.session_state = {}  # type: ignore[attr-defined]
    _mock_st.rerun = MagicMock()  # type: ignore[attr-defined]
    _mock_st.caption = MagicMock()  # type: ignore[attr-defined]
    _mock_st.subheader = MagicMock()  # type: ignore[attr-defined]
    _mock_st.header = MagicMock()  # type: ignore[attr-defined]
    _mock_st.slider = MagicMock()  # type: ignore[attr-defined]
    _mock_st.checkbox = MagicMock()  # type: ignore[attr-defined]
    # container() and expander() must support 'with' context manager usage
    @contextmanager
    def _fake_container(*args, **kwargs):
        yield MagicMock()
    _mock_st.container = MagicMock(side_effect=_fake_container)  # type: ignore[attr-defined]
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
    _mock_st.audio = MagicMock()  # type: ignore[attr-defined]
    _mock_st.chat_input = MagicMock()  # type: ignore[attr-defined]
    _mock_st.chat_message = MagicMock()  # type: ignore[attr-defined]

    sys.modules["streamlit"] = _mock_st

# Mock voice I/O libraries (not installed in CI)
for mod_name in ("kittentts", "faster_whisper", "streamlit_webrtc", "soundfile", "av"):
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)
