"""
Landing Page - Academic Curator design.

Full-page marketing experience rendered INSTEAD of the CRM tab layout.
Uses st.markdown(unsafe_allow_html=True) for complex HTML sections
and standard Streamlit components where possible.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.config import DEFAULT_WEIGHTS, FACTOR_DISPLAY_LABELS


def _switch_to_crm(enable_demo: bool = False) -> None:
    """Switch from landing view to CRM view and rerun the app."""
    st.session_state["current_view"] = "crm"
    if enable_demo:
        st.session_state["demo_mode"] = True
    st.rerun()


def _render_hero_intro() -> None:
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 4rem 1rem 3rem 1rem;
        ">
            <p style="
                color: #005394;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
                letter-spacing: 0.15em;
                text-transform: uppercase;
                font-size: 0.85rem;
                margin-bottom: 1rem;
            ">AI-Driven Opportunity Matching for IA West</p>
            <h1 style="
                font-family: 'Inter Tight', sans-serif;
                font-weight: 800;
                font-size: clamp(2rem, 5vw, 3.5rem);
                line-height: 1.1;
                color: #191c1e;
                max-width: 800px;
                margin: 0 auto 1.5rem auto;
            ">Match your specialist database with every university opportunity</h1>
            <p style="
                font-family: 'Inter', sans-serif;
                color: #414750;
                font-size: 1.15rem;
                max-width: 640px;
                margin: 0 auto 2rem auto;
                line-height: 1.6;
            ">Bridge the gap between your internal industry expertise and live academic
            needs through automated web-scraped signals and high-fidelity matching.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_hero_actions() -> None:
    _spacer_l, col_start, col_demo, _spacer_r = st.columns([2, 1, 1, 2])
    with col_start:
        if st.button("Start Matching", type="primary", use_container_width=True):
            _switch_to_crm()
    with col_demo:
        if st.button("View Demo", use_container_width=True):
            _switch_to_crm(enable_demo=True)


def _render_hero() -> None:
    """Hero section with gradient headline, subtitle, and CTAs."""
    _render_hero_intro()
    _render_hero_actions()


def _render_preview_event_card() -> None:
    st.markdown(
        """
        <div style="
            background: #ffffff;
            border-radius: 24px;
            padding: 2rem;
            box-shadow: 0 12px 40px rgba(25,28,30,0.06);
        ">
            <p style="color: #005394; font-weight: 700; font-size: 0.7rem;
               text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.25rem;">
               Scraped Opportunity</p>
            <h3 style="font-family: 'Inter Tight', sans-serif; font-weight: 700;
                font-size: 1.6rem; margin-bottom: 0.25rem; color: #191c1e;">
                UCLA Career Fair 2026</h3>
            <p style="color: #414750; font-size: 0.9rem;">
                Luskin Conference Center &bull; May 14, 2026</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_preview_recommendation() -> None:
    rec_cols = st.columns([1, 3, 1, 1])
    with rec_cols[0]:
        st.markdown(
            '<div style="width:48px;height:48px;border-radius:50%;'
            "background:#2b6cb0;color:white;display:flex;align-items:center;"
            'justify-content:center;font-weight:700;font-size:1rem;">TM</div>',
            unsafe_allow_html=True,
        )
    with rec_cols[1]:
        st.markdown("**Travis Miller**")
        st.caption("SVP Sales, TechCorp")
    with rec_cols[2]:
        st.metric("Match", "94%")
    with rec_cols[3]:
        st.button("Sync CRM", key="landing_sync_btn", disabled=True)


def _render_preview_factor_tiles() -> None:
    factor_preview = st.columns(3)
    previews = [
        ("Domain Relevance", "35%"),
        ("Scraped Role Fit", "25%"),
        ("Location", "20%"),
    ]
    for idx, (label, pct) in enumerate(previews):
        with factor_preview[idx]:
            st.markdown(
                f'<div style="text-align:center;background:#f7f9fc;'
                f'border-radius:12px;padding:1rem;">'
                f'<p style="color:#005394;font-weight:700;font-size:1.1rem;'
                f'margin:0;">{pct}</p>'
                f'<p style="color:#414750;font-size:0.7rem;text-transform:uppercase;'
                f'font-weight:500;margin:0;">{label}</p></div>',
                unsafe_allow_html=True,
            )


def _render_bridge_logic_panel() -> None:
    st.markdown(
        """
        <div style="
            background: #2b6cb0;
            color: #e1ecff;
            padding: 2rem;
            border-radius: 24px;
            min-height: 320px;
            display: flex;
            flex-direction: column;
        ">
            <h4 style="font-family: 'Inter Tight', sans-serif; font-weight: 700;
                font-size: 1.2rem; margin-bottom: 1rem; color: white;">
                Bridge Logic</h4>
            <p style="font-size: 0.95rem; line-height: 1.6; opacity: 0.9;">
                Travis's profile in your Specialist CRM aligns with UCLA's
                web-scraped event data focused on "Sales Leadership in SaaS."
                His history suggests a high-fidelity match for this discovered
                opportunity.</p>
            <div style="margin-top: auto; padding-top: 1.5rem;">
                <div style="display: flex; justify-content: space-between;
                     font-size: 0.85rem; margin-bottom: 0.5rem;">
                    <span>Signal Integrity</span>
                    <span style="font-weight: 700;">Excellent</span>
                </div>
                <div style="background: rgba(255,255,255,0.2); height: 4px;
                     border-radius: 9999px; overflow: hidden;">
                    <div style="background: white; height: 100%; width: 92%;"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_product_preview() -> None:
    """Bento-style product preview with event card, speaker rec, and AI panel."""
    st.markdown(
        """
        <div style="
            background: #f2f4f7;
            border-radius: 2.5rem;
            padding: 2rem;
            margin: 0 0 3rem 0;
        ">
        """,
        unsafe_allow_html=True,
    )

    col_main, col_ai = st.columns([2, 1])
    with col_main:
        _render_preview_event_card()
        _render_preview_recommendation()
        _render_preview_factor_tiles()
    with col_ai:
        _render_bridge_logic_panel()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_features_grid() -> None:
    """Three-column features grid."""
    st.markdown(
        '<h2 style="font-family: \'Inter Tight\', sans-serif; font-weight: 700; '
        'font-size: 1.8rem; margin-bottom: 0.5rem; color: #191c1e;">'
        "Complete Specialist Engagement Pipeline</h2>"
        '<p style="color: #414750; max-width: 540px; margin-bottom: 2rem;">'
        "A unified platform to bridge your internal specialist database "
        "with external university opportunities.</p>",
        unsafe_allow_html=True,
    )

    features = [
        (
            "Proprietary Web Scraping",
            "Real-time automation monitors university portals to identify "
            "speaking slots, panels, and academic needs across the West Coast.",
        ),
        (
            "Industry Specialist CRM",
            "Centralize your internal database of volunteers with enriched "
            "profiles, expertise tracking, and availability management.",
        ),
        (
            "Bridge Matching",
            "Proprietary algorithms bridge the gap between internal CRM "
            "expertise and scraped event requirements for optimal placement.",
        ),
    ]

    cols = st.columns(3)
    for idx, (title, desc) in enumerate(features):
        with cols[idx]:
            icon = "&#127760;" if idx == 0 else "&#128101;" if idx == 1 else "&#128279;"
            st.markdown(
                f'<div style="background: #ffffff; width: 56px; height: 56px; '
                f'border-radius: 16px; display: flex; align-items: center; '
                f'justify-content: center; box-shadow: 0 4px 12px rgba(25,28,30,0.04); '
                f'margin-bottom: 1rem; color: #005394; font-size: 1.5rem;">{icon}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<h3 style="font-family: \'Inter Tight\', sans-serif; font-weight: 700; '
                f'font-size: 1.2rem; color: #191c1e; margin-bottom: 0.5rem;">{title}</h3>'
                f'<p style="color: #414750; font-size: 0.9rem; line-height: 1.5;">{desc}</p>',
                unsafe_allow_html=True,
            )


def _build_factor_donut_chart(labels: list[str], values: list[float]) -> go.Figure:
    factor_count = len(values)
    min_opacity = 0.2
    max_opacity = 1.0
    if factor_count <= 1:
        opacities = [max_opacity]
    else:
        step = (max_opacity - min_opacity) / (factor_count - 1)
        opacities = [max_opacity - (idx * step) for idx in range(factor_count)]

    base_r, base_g, base_b = 0, 83, 148
    colors = [f"rgba({base_r},{base_g},{base_b},{opacity:.3f})" for opacity in opacities]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=colors),
                textinfo="label+percent",
                textfont=dict(family="Inter, sans-serif", size=12),
                hovertemplate="%{label}: %{value:.0%}<extra></extra>",
                sort=False,
            )
        ]
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text='<b style="font-size:2rem;color:#005394;">94</b><br>'
                '<span style="font-size:0.7rem;color:#414750;">Match Score</span>',
                x=0.5,
                y=0.5,
                font_size=14,
                showarrow=False,
            )
        ],
    )
    return fig


def _render_factor_verification_panel() -> None:
    st.markdown(
        '<div style="background: #ffffff; padding: 2rem; border-radius: 24px; '
        'box-shadow: 0 12px 40px rgba(25,28,30,0.06);">',
        unsafe_allow_html=True,
    )
    verification_items = [
        (
            "CRM Profile Sync",
            "Specialist expertise matches 100% of the course curriculum scraped from UCLA.",
        ),
        (
            "Scraped Calendar Match",
            "CRM availability shows 3 overlapping slots with the university's priority window.",
        ),
        (
            "Geospatial Synergies",
            "Internal location data aligns with the scraped event venue for low-friction coordination.",
        ),
    ]
    for title, desc in verification_items:
        st.markdown(
            f'<div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">'
            f'<div style="width: 40px; height: 40px; border-radius: 50%; '
            f"background: rgba(0,83,148,0.1); flex-shrink: 0; display: flex; "
            f'align-items: center; justify-content: center; color: #005394; '
            f'font-size: 1.2rem;">&#9679;</div>'
            f"<div>"
            f'<p style="font-weight: 700; font-size: 0.75rem; text-transform: uppercase; '
            f'letter-spacing: 0.1em; color: #414750; margin-bottom: 0.25rem;">{title}</p>'
            f'<p style="color: #191c1e; font-size: 0.9rem; line-height: 1.4;">{desc}</p>'
            f"</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_factor_donut() -> None:
    """Factor weight distribution donut chart using Plotly."""
    factor_count = len(DEFAULT_WEIGHTS)
    st.markdown(
        '<h2 style="font-family: \'Inter Tight\', sans-serif; font-weight: 700; '
        'font-size: 1.8rem; margin-bottom: 0.5rem; color: #191c1e;">'
        f"The Bridge: {factor_count}-Factor MATCH_SCORE</h2>"
        '<p style="color: #414750; margin-bottom: 1.5rem; max-width: 540px;">'
        "Our engine cross-references internal specialist data with scraped "
        "event parameters to maximize the impact of every engagement.</p>",
        unsafe_allow_html=True,
    )

    labels = [FACTOR_DISPLAY_LABELS[k] for k in DEFAULT_WEIGHTS]
    values = list(DEFAULT_WEIGHTS.values())
    col_chart, col_detail = st.columns([1, 1])

    with col_chart:
        st.plotly_chart(_build_factor_donut_chart(labels, values), use_container_width=True, key="landing_donut")

    with col_detail:
        _render_factor_verification_panel()


def _render_pipeline_visual() -> None:
    st.markdown(
        """
        <div style="space-y: 1rem;">
            <div style="background: white; padding: 1.25rem; border-radius: 16px;
                 border-left: 4px solid #005394; margin-bottom: 0.75rem;
                 box-shadow: 0 4px 12px rgba(25,28,30,0.04);">
                <code style="font-size: 0.85rem; color: #414750;">
                    <span style="color: #005394; font-weight: 600;">SCRAPE</span>
                    https://career.ucla.edu/api/events
                </code>
            </div>
            <div style="background: white; padding: 1.25rem; border-radius: 16px;
                 margin-left: 2rem; opacity: 0.85; margin-bottom: 0.75rem;
                 box-shadow: 0 4px 12px rgba(25,28,30,0.04);">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="width: 10px; height: 10px; border-radius: 50%;
                         background: #059669;"></div>
                    <span style="font-size: 0.8rem; font-weight: 700;
                          text-transform: uppercase; letter-spacing: 0.1em;">
                          Parsing Discovered Data...</span>
                </div>
                <div style="height: 6px; background: #eceef1; border-radius: 9999px;
                     margin-bottom: 4px;"></div>
                <div style="height: 6px; background: #eceef1; border-radius: 9999px;
                     width: 80%;"></div>
            </div>
            <div style="background: #005394; padding: 1.25rem; border-radius: 16px;
                 margin-left: 4rem; color: white; display: flex; align-items: center;
                 justify-content: space-between;
                 box-shadow: 0 8px 24px rgba(0,83,148,0.3);">
                <span style="font-weight: 700;">Syncing with Specialist CRM...</span>
                <span style="font-size: 1.2rem;">&#8250;</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_pipeline_copy() -> None:
    st.markdown(
        '<h2 style="font-family: \'Inter Tight\', sans-serif; font-weight: 700; '
        'font-size: 1.8rem; color: #191c1e; margin-bottom: 1rem;">'
        "Proprietary Web Scraping</h2>"
        '<p style="color: #414750; font-size: 1rem; line-height: 1.6; margin-bottom: 1.5rem;">'
        "Our scraping pipeline monitors UCLA, USC, and dozens of other university "
        "sites in real-time. No more manual searching; discovered opportunities are "
        "instantly cross-referenced against your internal database of specialists.</p>",
        unsafe_allow_html=True,
    )

    badge_cols = st.columns(4)
    for idx, uni in enumerate(["UCLA", "USC", "SDSU", "+42"]):
        with badge_cols[idx]:
            st.markdown(
                f'<div style="width: 48px; height: 48px; border-radius: 50%; '
                f"background: #e6e8eb; display: flex; align-items: center; "
                f"justify-content: center; font-size: 0.65rem; font-weight: 700; "
                f'color: #414750;">{uni}</div>',
                unsafe_allow_html=True,
            )


def _render_automation_pipeline() -> None:
    """Visual showing SCRAPE -> Parse -> Sync CRM flow."""
    st.markdown(
        """
        <div style="background: #eceef1; border-radius: 24px; padding: 3rem 2rem; margin: 2rem 0;">
        """,
        unsafe_allow_html=True,
    )

    col_visual, col_text = st.columns([1, 1])
    with col_visual:
        _render_pipeline_visual()
    with col_text:
        _render_pipeline_copy()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_analytics_heatmap() -> None:
    st.markdown(
        """
        <div style="background: #ffffff; border-radius: 24px; padding: 2rem;
             box-shadow: 0 12px 40px rgba(25,28,30,0.06);">
            <h3 style="font-family: 'Inter Tight', sans-serif; font-weight: 700;
                font-size: 1.1rem; margin-bottom: 1.5rem; color: #191c1e;">
                Opportunity Density Heat Map</h3>
            <div style="height: 200px; background: #eceef1; border-radius: 16px;
                 display: flex; align-items: center; justify-content: center;
                 position: relative; overflow: hidden;">
                <div style="text-align: center;">
                    <div style="width: 48px; height: 48px; background: #005394;
                         border-radius: 50%; opacity: 0.5; margin: 0 auto 0.5rem auto;">
                    </div>
                    <p style="font-weight: 700; color: #005394; font-size: 0.85rem;">
                        High Opportunity: Los Angeles Hub</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_analytics_funnel() -> None:
    st.markdown(
        '<div style="background: #ffffff; border-radius: 24px; padding: 2rem; '
        'box-shadow: 0 12px 40px rgba(25,28,30,0.06);">'
        '<h3 style="font-family: \'Inter Tight\', sans-serif; font-weight: 700; '
        'font-size: 1.1rem; margin-bottom: 1.5rem; color: #191c1e;">'
        "Matching Funnel</h3>",
        unsafe_allow_html=True,
    )
    funnel_data = [
        ("Discovered (Scraped)", 2481, 100),
        ("CRM Potential Matches", 842, 34),
        ("Specialist Confirmed", 114, 5),
    ]
    for label, count, pct in funnel_data:
        st.markdown(
            f'<div style="margin-bottom: 1.25rem;">'
            f'<div style="display: flex; justify-content: space-between; '
            f'margin-bottom: 0.35rem;">'
            f'<span style="font-size: 0.8rem; font-weight: 700;">{label}</span>'
            f'<span style="font-size: 0.8rem; color: #414750;">{count:,}</span></div>'
            f'<div style="height: 10px; background: #eceef1; border-radius: 9999px; '
            f'overflow: hidden;">'
            f'<div style="height: 100%; background: #005394; width: {pct}%; '
            f'border-radius: 9999px;"></div></div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_analytics_preview() -> None:
    """Analytics section with heat map placeholder and matching funnel bars."""
    st.markdown(
        '<h2 style="font-family: \'Inter Tight\', sans-serif; font-weight: 700; '
        'font-size: 1.8rem; text-align: center; margin-bottom: 2rem; '
        'color: #191c1e;">Engagement & Scraping Analytics</h2>',
        unsafe_allow_html=True,
    )

    col_heatmap, col_funnel = st.columns([2, 1])
    with col_heatmap:
        _render_analytics_heatmap()
    with col_funnel:
        _render_analytics_funnel()


def _render_partner_showcase() -> None:
    """University partner logos."""
    universities = ["CPP", "UCLA", "SDSU", "UC DAVIS", "USC", "PORTLAND STATE"]
    st.markdown(
        '<p style="text-align: center; color: #414750; font-weight: 700; '
        "text-transform: uppercase; letter-spacing: 0.15em; font-size: 0.7rem; "
        'margin-bottom: 1.5rem;">Bridging CRM Data to</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(universities))
    for idx, uni in enumerate(universities):
        with cols[idx]:
            st.markdown(
                f'<p style="text-align: center; font-family: \'Inter Tight\', sans-serif; '
                f"font-weight: 800; font-size: 1.1rem; color: #191c1e; "
                f'opacity: 0.5;">{uni}</p>',
                unsafe_allow_html=True,
            )


def _render_final_cta_intro() -> None:
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 1rem;">
            <h2 style="font-family: 'Inter Tight', sans-serif; font-weight: 700;
                font-size: clamp(1.5rem, 4vw, 2.5rem); color: #191c1e;
                margin-bottom: 1rem;">
                Ready to sync your database with the web?</h2>
            <p style="color: #414750; font-size: 1.05rem; max-width: 540px;
               margin: 0 auto 2rem auto; line-height: 1.6;">
                Join the IA West network and transform how your internal specialist
                database interacts with real-world university opportunities.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_final_cta_actions() -> None:
    _spacer_l, col_connect, col_schedule, _spacer_r = st.columns([2, 1, 1, 2])
    with col_connect:
        if st.button("Start Matching Now", type="primary", use_container_width=True):
            _switch_to_crm()
    with col_schedule:
        if st.button("Schedule Demo", use_container_width=True):
            _switch_to_crm(enable_demo=True)


def _render_final_cta() -> None:
    """Final call-to-action section."""
    _render_final_cta_intro()
    _render_final_cta_actions()


def render_landing_page(datasets: object | None = None) -> None:
    """Render the full landing page. Datasets param reserved for future metric sourcing."""
    _render_hero()
    _render_product_preview()
    _render_features_grid()
    _render_factor_donut()
    _render_automation_pipeline()
    _render_analytics_preview()
    _render_partner_showcase()
    _render_final_cta()
