"""
Login/role-selection page for IA SmartMatch.

Renders two role cards side by side — Coordinator (functional demo login) and
Volunteer (placeholder with "Coming Soon" badge) — using the Academic Curator
design system via st.components.v1.html().

Exports:
    render_login_page: Entry point for the login page.
"""

from __future__ import annotations

import streamlit as st

from src.ui.html_base import render_html_page
from src.ui.page_router import navigate_to, set_user_role

# ── HTML Body ─────────────────────────────────────────────────────────────────

_LOGIN_BODY: str = """
<!-- Glass Nav Bar -->
<nav class="bg-white/80 backdrop-blur-xl shadow-sm fixed top-0 w-full z-50 flex justify-between items-center px-8 py-4">
  <span class="text-xl font-bold tracking-tight text-on-surface font-headline">IA SmartMatch</span>
  <a href="#" class="text-primary font-semibold text-sm">Back to Home</a>
</nav>

<!-- Main Content -->
<main class="pt-24 min-h-screen flex flex-col items-center justify-center bg-surface px-8">
  <h1 class="text-4xl font-headline font-bold text-on-surface mb-2">Welcome Back</h1>
  <p class="text-on-surface-variant mb-12 text-lg">Select your role to continue</p>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl w-full">

    <!-- Coordinator Card -->
    <div class="bg-surface-container-lowest rounded-[24px] p-8 shadow-sm hover:shadow-md transition-shadow">
      <div class="w-14 h-14 rounded-2xl bg-primary flex items-center justify-center text-white mb-6">
        <span class="material-symbols-outlined text-3xl">school</span>
      </div>
      <h2 class="text-2xl font-headline font-bold text-on-surface mb-2">Coordinator</h2>
      <p class="text-on-surface-variant mb-6">
        Access the institutional dashboard, manage matches, and oversee the specialist
        engagement pipeline.
      </p>
      <div class="space-y-3">
        <button
          id="demo-login-btn"
          class="w-full py-3 hero-gradient text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all"
        >
          Demo Login
        </button>
        <p class="text-xs text-on-surface-variant text-center">No credentials needed for demo</p>
      </div>
    </div>

    <!-- Volunteer Card -->
    <div class="bg-surface-container-lowest rounded-[24px] p-8 shadow-sm relative overflow-hidden opacity-80">
      <div class="absolute top-4 right-4 px-3 py-1 bg-tertiary-fixed text-on-tertiary-fixed rounded-full text-[10px] font-bold uppercase tracking-wide">
        Coming Soon
      </div>
      <div class="w-14 h-14 rounded-2xl bg-secondary flex items-center justify-center text-white mb-6">
        <span class="material-symbols-outlined text-3xl">person</span>
      </div>
      <h2 class="text-2xl font-headline font-bold text-on-surface mb-2">Volunteer</h2>
      <p class="text-on-surface-variant mb-6">
        View your speaking assignments, update availability, and connect with engagement
        opportunities.
      </p>
      <button
        class="w-full py-3 bg-surface-container-high text-on-surface-variant rounded-xl font-semibold text-sm cursor-not-allowed"
        disabled
      >
        Connect with LinkedIn
      </button>
      <p class="text-xs text-on-surface-variant text-center mt-3">
        LinkedIn OAuth integration coming soon
      </p>
    </div>

  </div>
</main>
"""


# ── Public API ────────────────────────────────────────────────────────────────


def render_login_page() -> None:
    """
    Render the login/role-selection page.

    Displays two cards:
    - **Coordinator**: Demo Login button that sets user_role to "coordinator"
      and navigates to the coordinator dashboard.
    - **Volunteer**: Disabled "Connect with LinkedIn" button with a
      "Coming Soon" badge.

    The HTML component hides Streamlit chrome (sidebar, header, footer).
    Streamlit buttons below the iframe provide actual navigation via
    page_router functions.
    """
    render_html_page(
        _LOGIN_BODY,
        title="IA SmartMatch | Login",
        height=900,
        hide_chrome=True,
    )

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("< Back to Home", use_container_width=True):
            navigate_to("landing")

    with col2:
        if st.button("Coordinator Demo Login", type="primary", use_container_width=True):
            set_user_role("coordinator")
            navigate_to("coordinator")

    with col3:
        st.button("Volunteer (Coming Soon)", disabled=True, use_container_width=True)
