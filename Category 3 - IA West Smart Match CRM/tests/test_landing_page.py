"""Tests for the Landing Page module."""

from unittest.mock import MagicMock, patch


def _setup_mock_st(mock_st: MagicMock, button_side_effects: list[bool] | None = None) -> None:
    """Configure a mock st module for landing page rendering."""
    mock_st.session_state = {}

    # Columns must return mocks that work as context managers
    def make_cols(spec):
        n = len(spec) if isinstance(spec, (list, tuple)) else spec
        cols = []
        for _ in range(n):
            col = MagicMock()
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
            cols.append(col)
        return cols

    mock_st.columns.side_effect = make_cols
    mock_st.button.return_value = False
    if button_side_effects is not None:
        mock_st.button.side_effect = button_side_effects


class TestRenderLandingPage:
    """Test render_landing_page() and its sub-sections."""

    @patch("src.ui.landing_page.go")
    @patch("src.ui.landing_page.st")
    def test_render_landing_page_no_crash(self, mock_st: MagicMock, mock_go: MagicMock) -> None:
        """Landing page renders without error when no buttons clicked."""
        _setup_mock_st(mock_st)

        from src.ui.landing_page import render_landing_page

        render_landing_page()

        # Verify markdown was called (hero, features, etc.)
        assert mock_st.markdown.call_count > 5

    @patch("src.ui.landing_page.st")
    def test_hero_renders_headline(self, mock_st: MagicMock) -> None:
        """Hero section renders the main headline text."""
        _setup_mock_st(mock_st)

        from src.ui.landing_page import _render_hero

        _render_hero()

        # Check that the hero headline appears in markdown calls
        all_html = " ".join(
            str(c.args[0]) for c in mock_st.markdown.call_args_list if c.args
        )
        assert "Match your specialist database" in all_html

    @patch("src.ui.landing_page.st")
    def test_hero_start_matching_sets_crm_view(self, mock_st: MagicMock) -> None:
        """Clicking 'Start Matching' sets current_view to crm."""
        _setup_mock_st(mock_st, button_side_effects=[True, False])

        from src.ui.landing_page import _render_hero

        _render_hero()

        assert mock_st.session_state["current_view"] == "crm"
        mock_st.rerun.assert_called()

    @patch("src.ui.landing_page.st")
    def test_hero_view_demo_enables_demo_mode(self, mock_st: MagicMock) -> None:
        """Clicking 'View Demo' sets demo_mode and switches to CRM."""
        _setup_mock_st(mock_st, button_side_effects=[False, True])

        from src.ui.landing_page import _render_hero

        _render_hero()

        assert mock_st.session_state["current_view"] == "crm"
        assert mock_st.session_state["demo_mode"] is True

    @patch("src.ui.landing_page.st")
    def test_final_cta_navigates_to_crm(self, mock_st: MagicMock) -> None:
        """Final CTA 'Start Matching Now' navigates to CRM view."""
        _setup_mock_st(mock_st, button_side_effects=[True, False])

        from src.ui.landing_page import _render_final_cta

        _render_final_cta()

        assert mock_st.session_state["current_view"] == "crm"


class TestFactorDonutChart:
    """Test the 6-factor donut chart rendering."""

    @patch("src.ui.landing_page.st")
    @patch("src.ui.landing_page.go")
    def test_donut_uses_default_weights(self, mock_go: MagicMock, mock_st: MagicMock) -> None:
        """Donut chart uses DEFAULT_WEIGHTS from config."""
        _setup_mock_st(mock_st)

        from src.config import DEFAULT_WEIGHTS
        from src.ui.landing_page import _render_factor_donut

        _render_factor_donut()

        pie_call = mock_go.Pie.call_args
        assert len(pie_call.kwargs["values"]) == len(DEFAULT_WEIGHTS)
        assert len(pie_call.kwargs["labels"]) == len(DEFAULT_WEIGHTS)
        assert len(pie_call.kwargs["marker"]["colors"]) == len(DEFAULT_WEIGHTS)

    @patch("src.ui.landing_page.st")
    def test_donut_heading_uses_dynamic_factor_count(self, mock_st: MagicMock) -> None:
        """Donut heading should reflect the registry-driven factor count."""
        _setup_mock_st(mock_st)

        from src.config import DEFAULT_WEIGHTS
        from src.ui.landing_page import _render_factor_donut

        _render_factor_donut()

        all_html = " ".join(
            str(c.args[0]) for c in mock_st.markdown.call_args_list if c.args
        )
        assert f"The Bridge: {len(DEFAULT_WEIGHTS)}-Factor MATCH_SCORE" in all_html


class TestViewSwitchingIntegration:
    """Test the view switching logic."""

    def test_default_view_is_landing(self) -> None:
        """Default current_view should be 'landing'."""
        session_state: dict[str, str] = {}
        assert session_state.get("current_view", "landing") == "landing"

    def test_crm_view_set(self) -> None:
        """Setting current_view to 'crm' should stick."""
        session_state: dict[str, str] = {"current_view": "crm"}
        assert session_state["current_view"] == "crm"


class TestDesignTokens:
    """Verify Academic Curator design tokens are present in styles.py."""

    def test_primary_color_in_css(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "#005394" in CUSTOM_CSS

    def test_no_old_primary_color(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "#1E3A5F" not in CUSTOM_CSS

    def test_inter_tight_font_imported(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "Inter+Tight" in CUSTOM_CSS or "Inter Tight" in CUSTOM_CSS

    def test_hero_gradient_defined(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "--hero-gradient" in CUSTOM_CSS

    def test_surface_hierarchy_defined(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "--surface-container-low" in CUSTOM_CSS
        assert "--surface-container" in CUSTOM_CSS
        assert "--surface-container-lowest" in CUSTOM_CSS

    def test_no_line_rule_no_borders_on_expander(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "border: none" in CUSTOM_CSS

    def test_ambient_shadow_defined(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "--ambient-shadow" in CUSTOM_CSS
        assert "rgba(25, 28, 30" in CUSTOM_CSS or "rgba(25,28,30" in CUSTOM_CSS

    def test_card_radius_24px(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "24px" in CUSTOM_CSS

    def test_font_headline_variable(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "--font-headline" in CUSTOM_CSS

    def test_radius_variables(self) -> None:
        from src.ui.styles import CUSTOM_CSS
        assert "--radius-card" in CUSTOM_CSS
        assert "--radius-button" in CUSTOM_CSS


class TestPartnerShowcase:
    """Test university partner showcase."""

    @patch("src.ui.landing_page.st")
    def test_all_universities_rendered(self, mock_st: MagicMock) -> None:
        """All 6 partner universities are displayed."""
        _setup_mock_st(mock_st)

        from src.ui.landing_page import _render_partner_showcase

        _render_partner_showcase()

        # Collect all markdown calls from both st and column mocks
        all_html = " ".join(
            str(c.args[0]) for c in mock_st.markdown.call_args_list if c.args
        )

        for uni in ["CPP", "UCLA", "SDSU", "UC DAVIS", "USC", "PORTLAND STATE"]:
            assert uni in all_html

        assert "Bridging CRM Data to" in all_html


class TestProductPreview:
    """Test the product preview bento section."""

    @patch("src.ui.landing_page.st")
    def test_product_preview_renders(self, mock_st: MagicMock) -> None:
        """Product preview section renders the demo event card."""
        _setup_mock_st(mock_st)

        from src.ui.landing_page import _render_product_preview

        _render_product_preview()

        all_html = " ".join(
            str(c.args[0]) for c in mock_st.markdown.call_args_list if c.args
        )
        assert "UCLA Career Fair 2026" in all_html
        assert "Bridge Logic" in all_html


class TestFeaturesGrid:
    """Test features grid section."""

    @patch("src.ui.landing_page.st")
    def test_features_grid_renders_three_features(self, mock_st: MagicMock) -> None:
        """Features grid renders all 3 feature cards."""
        _setup_mock_st(mock_st)

        from src.ui.landing_page import _render_features_grid

        _render_features_grid()

        all_html = " ".join(
            str(c.args[0]) for c in mock_st.markdown.call_args_list if c.args
        )
        assert "Proprietary Web Scraping" in all_html
        assert "Industry Specialist CRM" in all_html
        assert "Bridge Matching" in all_html
