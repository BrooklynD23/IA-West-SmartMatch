"""Tests for the Match Engine page (native Streamlit widget version)."""

from unittest.mock import MagicMock, patch, call


def _setup_mock_st(mock_st: MagicMock) -> None:
    """Provide Streamlit context-manager columns / expanders for page rendering."""

    def make_cols(spec):
        count = len(spec) if isinstance(spec, (list, tuple)) else spec
        cols = []
        for _ in range(count):
            col = MagicMock()
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
            cols.append(col)
        return cols

    mock_st.columns.side_effect = make_cols
    mock_st.button.return_value = False

    expander = MagicMock()
    expander.__enter__ = MagicMock(return_value=expander)
    expander.__exit__ = MagicMock(return_value=False)
    mock_st.expander.return_value = expander


def test_render_match_engine_page_shows_empty_state() -> None:
    """An empty pipeline should show the 'no ranked specialists' info message."""
    from src.ui import match_engine_page as page

    mock_st = MagicMock()
    _setup_mock_st(mock_st)

    with (
        patch.object(page, "st", mock_st),
        patch.object(page, "load_specialists", return_value=[]),
        patch.object(page, "load_pipeline_data", return_value=[]),
        patch.object(page, "load_poc_contacts", return_value=[]),
        patch.object(page, "get_top_specialists_for_event", return_value=[]),
        patch.object(page, "navigate_to"),
        patch.object(page, "set_user_role"),
    ):
        page.render_match_engine_page()

    # Should show the empty-state info message
    info_calls = [c for c in mock_st.info.call_args_list if c.args]
    assert any("No ranked specialists" in str(c) for c in info_calls), (
        f"Expected 'No ranked specialists' info message, got: {mock_st.info.call_args_list}"
    )
    # Should still render Internal Specialist Matches heading
    markdown_texts = [str(c) for c in mock_st.markdown.call_args_list]
    assert any("Internal Specialist Matches" in t for t in markdown_texts)


def test_render_match_engine_page_renders_specialist_cards() -> None:
    """A populated pipeline should render specialist cards with metric scores."""
    from src.ui import match_engine_page as page

    mock_st = MagicMock()
    _setup_mock_st(mock_st)

    shortlist = [
        {
            "name": "Alex Rivera",
            "title": "VP Insights",
            "company": "Acme Research",
            "match_score": 0.91,
            "initials": "AR",
            "expertise_tags": "market research, analytics",
        }
    ]

    with (
        patch.object(page, "st", mock_st),
        patch.object(page, "load_specialists", return_value=[]),
        patch.object(page, "load_pipeline_data", return_value=[
            {
                "event_name": "CPP Career Center \u2014 Career Fairs",
                "speaker_name": "Alex Rivera",
                "match_score": "0.91",
            }
        ]),
        patch.object(page, "load_poc_contacts", return_value=[]),
        patch.object(page, "get_top_specialists_for_event", return_value=shortlist),
        patch.object(page, "navigate_to"),
        patch.object(page, "set_user_role"),
    ):
        page.render_match_engine_page()

    # Should NOT show the empty-state message
    info_calls = [str(c) for c in mock_st.info.call_args_list]
    assert not any("No ranked specialists" in t for t in info_calls)

    # Should render the specialist name
    markdown_texts = [str(c) for c in mock_st.markdown.call_args_list]
    assert any("Alex Rivera" in t for t in markdown_texts)

    # Should render a Match Score metric
    metric_calls = [str(c) for c in mock_st.metric.call_args_list]
    assert any("91%" in t for t in metric_calls)
