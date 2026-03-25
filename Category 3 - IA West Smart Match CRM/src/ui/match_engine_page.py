"""Match Engine Dashboard page for IA SmartMatch.

Renders the Internal Specialist Matches view via st.components.v1.html(),
populated with real specialist and POC data from data_helpers.py.
"""

from __future__ import annotations

import streamlit as st

from src.ui.data_helpers import (
    get_initials,
    get_top_specialists_for_event,
    load_pipeline_data,
    load_poc_contacts,
    load_specialists,
)
from src.ui.html_base import render_html_page
from src.ui.page_router import navigate_to, set_user_role


# Factor bar widths for each specialist card position (varied per card for visual richness)
_FACTOR_WIDTHS: list[dict[str, str]] = [
    {"Topic": "98%", "Role": "95%", "Prox.": "90%", "Cal.": "85%", "Hist.": "100%", "Impact": "96%"},
    {"Topic": "92%", "Role": "98%", "Prox.": "75%", "Cal.": "90%", "Hist.": "94%", "Impact": "88%"},
    {"Topic": "95%", "Role": "85%", "Prox.": "92%", "Cal.": "78%", "Hist.": "100%", "Impact": "90%"},
]


def render_match_engine_page() -> None:
    """Render the full Match Engine dashboard page.

    Loads real specialist and POC data. Renders a pixel-faithful reproduction
    of the match engine mockup via render_html_page() with initials avatars
    replacing all external images. Navigation buttons appear below the iframe.
    """
    # ── Load Data ────────────────────────────────────────────────────────────
    specialists = load_specialists()
    pipeline = load_pipeline_data()
    pocs = load_poc_contacts()

    # ── Select Featured Event ────────────────────────────────────────────────
    featured_event = "CPP Career Center \u2014 Career Fairs"
    top_matches = get_top_specialists_for_event(featured_event, 3)

    # Fallback: if event has no data, use first event available
    if not top_matches and pipeline:
        events = list({row["event_name"] for row in pipeline if row.get("event_name")})
        if events:
            featured_event = events[0]
            top_matches = get_top_specialists_for_event(featured_event, 3)

    match_count = len(
        [r for r in pipeline if r.get("event_name") == featured_event]
    ) or len(pipeline)

    # ── Build Specialist Cards (first two) ───────────────────────────────────
    spec_cards_html = ""
    for idx, spec in enumerate(top_matches[:2]):
        name = spec.get("name", "Specialist")
        title = spec.get("title", "")
        company = spec.get("company", "")
        initials = spec.get("initials") or get_initials(name)
        try:
            score_pct = round(float(spec.get("match_score", 0)) * 100)
        except (ValueError, TypeError):
            score_pct = 80
        title_company = f"{title}" + (f", {company}" if company else "")

        widths = _FACTOR_WIDTHS[idx % len(_FACTOR_WIDTHS)]
        factor_bars = _build_factor_bars(widths)

        spec_cards_html += f"""
        <!-- Specialist Card {idx + 1} -->
        <div class="bg-surface-container-lowest p-6 rounded-[24px] shadow-sm hover:shadow-md transition-shadow border border-outline-variant/10">
          <div class="flex justify-between items-start mb-6">
            <div class="flex gap-4">
              <div class="w-16 h-16 rounded-2xl bg-primary-container flex items-center justify-center text-white text-lg font-bold">
                {initials}
              </div>
              <div>
                <h4 class="font-bold text-lg leading-tight">{name}</h4>
                <p class="text-on-surface-variant text-sm">{title_company}</p>
              </div>
            </div>
            <div class="text-right">
              <div class="text-primary font-bold text-2xl">{score_pct}%</div>
              <div class="text-[10px] uppercase tracking-wider font-bold text-outline">Match Score</div>
            </div>
          </div>
          <!-- 6-Factor Visualization -->
          <div class="grid grid-cols-3 gap-2 mb-6">
            {factor_bars}
          </div>
          <div class="flex gap-2">
            <button class="flex-1 py-2.5 bg-primary-gradient text-white rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity">Select</button>
            <button class="w-12 h-11 flex items-center justify-center bg-surface-container-low text-on-surface rounded-xl hover:bg-surface-container-high transition-colors">
              <span class="material-symbols-outlined">visibility</span>
            </button>
          </div>
        </div>
        """

    # ── Build Featured Specialist Card (third, full-width) ───────────────────
    featured_card_html = ""
    if len(top_matches) >= 3:
        spec3 = top_matches[2]
        name3 = spec3.get("name", "Specialist")
        title3 = spec3.get("title", "")
        company3 = spec3.get("company", "")
        initials3 = spec3.get("initials") or get_initials(name3)
        try:
            score_pct3 = round(float(spec3.get("match_score", 0)) * 100)
        except (ValueError, TypeError):
            score_pct3 = 80
        tags3 = spec3.get("expertise_tags", "")

        featured_card_html = f"""
        <!-- Featured Specialist Card (col-span-2) -->
        <div class="md:col-span-2 bg-surface-container-lowest p-6 rounded-[24px] shadow-sm hover:shadow-md transition-shadow border border-outline-variant/10 flex flex-col md:flex-row gap-8">
          <div class="md:w-1/3 border-r border-outline-variant/10 pr-6">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-12 h-12 rounded-full bg-primary-container flex items-center justify-center text-white font-bold text-base">
                {initials3}
              </div>
              <div>
                <h4 class="font-bold text-base">{name3}</h4>
                <p class="text-xs text-on-surface-variant">{title3}{(', ' + company3) if company3 else ''}</p>
              </div>
            </div>
            <div class="space-y-3">
              <div class="flex justify-between items-center text-sm">
                <span class="text-on-surface-variant font-bold uppercase text-[10px] tracking-wider">Match Score</span>
                <span class="font-semibold text-primary">{score_pct3}% Fit</span>
              </div>
              <div class="w-full bg-surface-container h-1.5 rounded-full overflow-hidden">
                <div class="bg-primary h-full" style="width:{score_pct3}%"></div>
              </div>
              <p class="text-xs text-on-surface-variant leading-relaxed">
                Expertise: {tags3[:100] + '...' if len(tags3) > 100 else tags3}
              </p>
            </div>
          </div>
          <!-- Expanded Score Breakdown -->
          <div class="flex-1">
            <h5 class="text-xs font-bold uppercase tracking-widest text-outline mb-4">Detailed Score Breakdown</h5>
            <div class="grid grid-cols-2 lg:grid-cols-3 gap-y-4 gap-x-6">
              <div class="space-y-1">
                <div class="flex justify-between items-end">
                  <span class="text-[10px] font-bold text-on-surface-variant uppercase">Topic Fit <span class="text-outline font-normal">(35%)</span></span>
                  <span class="text-sm font-bold text-primary">{score_pct3 / 10:.1f}</span>
                </div>
                <div class="h-1.5 bg-surface-container rounded-full overflow-hidden">
                  <div class="h-full bg-primary" style="width:{score_pct3}%"></div>
                </div>
              </div>
              <div class="space-y-1">
                <div class="flex justify-between items-end">
                  <span class="text-[10px] font-bold text-on-surface-variant uppercase">Role Seniority <span class="text-outline font-normal">(25%)</span></span>
                  <span class="text-sm font-bold text-primary">8.5</span>
                </div>
                <div class="h-1.5 bg-surface-container rounded-full overflow-hidden">
                  <div class="h-full bg-primary w-[85%]"></div>
                </div>
              </div>
              <div class="space-y-1">
                <div class="flex justify-between items-end">
                  <span class="text-[10px] font-bold text-on-surface-variant uppercase">Proximity <span class="text-outline font-normal">(20%)</span></span>
                  <span class="text-sm font-bold text-primary">9.2</span>
                </div>
                <div class="h-1.5 bg-surface-container rounded-full overflow-hidden">
                  <div class="h-full bg-primary w-[92%]"></div>
                </div>
              </div>
              <div class="space-y-1">
                <div class="flex justify-between items-end">
                  <span class="text-[10px] font-bold text-on-surface-variant uppercase">Calendar <span class="text-outline font-normal">(15%)</span></span>
                  <span class="text-sm font-bold text-primary">7.8</span>
                </div>
                <div class="h-1.5 bg-surface-container rounded-full overflow-hidden">
                  <div class="h-full bg-primary w-[78%]"></div>
                </div>
              </div>
              <div class="space-y-1">
                <div class="flex justify-between items-end">
                  <span class="text-[10px] font-bold text-on-surface-variant uppercase">Hist. Impact <span class="text-outline font-normal">(5%)</span></span>
                  <span class="text-sm font-bold text-primary">10.0</span>
                </div>
                <div class="h-1.5 bg-surface-container rounded-full overflow-hidden">
                  <div class="h-full bg-primary w-[100%]"></div>
                </div>
              </div>
              <div class="flex items-end justify-end gap-3 pt-2">
                <button class="px-4 py-2 bg-surface-container-high text-on-surface rounded-xl text-xs font-semibold hover:bg-surface-container-highest transition-colors">Compare</button>
                <button class="px-4 py-2 bg-primary-gradient text-white rounded-xl text-xs font-semibold">Initiate Outreach</button>
              </div>
            </div>
          </div>
        </div>
        """

    # ── Build Right Rail POC section ─────────────────────────────────────────
    poc_html = ""
    if pocs:
        poc = pocs[0]
        poc_name = poc.get("name", "Contact")
        poc_role = poc.get("role", "")
        poc_org = poc.get("org", "")
        poc_initials = get_initials(poc_name)
        poc_html = f"""
        <div class="bg-surface-container-lowest border-2 border-primary/20 p-4 rounded-2xl mb-6 relative overflow-hidden">
          <div class="absolute top-0 right-0 px-2 py-0.5 bg-primary text-white text-[9px] font-bold rounded-bl-lg uppercase">Verified POC</div>
          <div class="text-[10px] font-bold text-primary uppercase tracking-wider mb-2">Primary Point of Contact</div>
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-white font-bold text-sm">{poc_initials}</div>
            <div>
              <p class="text-sm font-bold text-on-surface">{poc_name}</p>
              <p class="text-[11px] text-on-surface-variant">{poc_role}</p>
              <p class="text-[10px] text-slate-500">{poc_org}</p>
            </div>
          </div>
          <div class="flex gap-2">
            <button class="flex-1 py-2 bg-surface-container-high text-[11px] font-bold rounded-lg flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-xs">mail</span> Message
            </button>
            <button class="flex-1 py-2 bg-surface-container-high text-[11px] font-bold rounded-lg flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-xs">call</span> Call
            </button>
          </div>
        </div>
        """
    else:
        poc_html = """
        <div class="bg-surface-container-lowest border border-outline-variant/20 p-4 rounded-2xl mb-6">
          <p class="text-sm text-on-surface-variant">No POC contacts available.</p>
        </div>
        """

    # ── Build Right Rail AI reasoning text ───────────────────────────────────
    event_short = featured_event.replace("\u2014", "-").replace("CPP ", "")
    ai_reasoning = (
        f'Prioritize candidates with "CPP" tags. Historic data shows higher '
        f"acceptance rate for local speakers at {event_short}."
    )

    # ── Build Full HTML Body ─────────────────────────────────────────────────
    body_html = f"""
<!-- Sidebar Navigation -->
<aside class="h-screen w-64 fixed left-0 top-0 bg-slate-50 flex flex-col p-4 gap-2 z-40">
  <div class="flex items-center gap-3 mb-8 px-2">
    <div class="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-white font-bold">W</div>
    <div>
      <h2 class="text-lg font-semibold text-slate-900 leading-tight">IA West Chapter</h2>
      <p class="text-[10px] text-slate-500 uppercase tracking-widest font-medium">Regional Coordination</p>
    </div>
  </div>
  <nav class="flex-1 space-y-1">
    <a class="flex items-center gap-3 px-4 py-3 bg-white text-blue-700 rounded-xl shadow-sm font-medium transition-transform active:scale-95" href="#">
      <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">dashboard</span>
      <span class="text-sm">Matches</span>
    </a>
    <a class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 hover:translate-x-1 transition-all rounded-xl" href="#">
      <span class="material-symbols-outlined">person_search</span>
      <span class="text-sm">Speaker Database</span>
    </a>
    <a class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 hover:translate-x-1 transition-all rounded-xl" href="#">
      <span class="material-symbols-outlined">school</span>
      <span class="text-sm">Scraped Events</span>
    </a>
    <a class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 hover:translate-x-1 transition-all rounded-xl" href="#">
      <span class="material-symbols-outlined">auto_awesome</span>
      <span class="text-sm">Discovery Engine</span>
    </a>
    <a class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 hover:translate-x-1 transition-all rounded-xl" href="#">
      <span class="material-symbols-outlined">account_tree</span>
      <span class="text-sm">Pipeline Tracker</span>
    </a>
    <a class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200/50 hover:translate-x-1 transition-all rounded-xl" href="#">
      <span class="material-symbols-outlined">analytics</span>
      <span class="text-sm">Analytics</span>
    </a>
  </nav>
  <div class="mt-auto border-t border-slate-200 pt-4 space-y-1">
    <button class="w-full flex items-center gap-3 px-4 py-3 bg-primary-gradient text-white rounded-xl shadow-md font-medium text-sm mb-4">
      <span class="material-symbols-outlined">add</span>
      <span>New Match Request</span>
    </button>
    <a class="flex items-center gap-3 px-4 py-2 text-slate-500 hover:text-primary transition-colors" href="#">
      <span class="material-symbols-outlined">settings</span>
      <span class="text-sm">Settings</span>
    </a>
    <a class="flex items-center gap-3 px-4 py-2 text-slate-500 hover:text-primary transition-colors" href="#">
      <span class="material-symbols-outlined">help</span>
      <span class="text-sm">Support</span>
    </a>
  </div>
</aside>

<!-- Main Content Area -->
<main class="ml-64 mr-80 min-h-screen p-8 bg-surface">
  <!-- Header & Search -->
  <header class="max-w-4xl mx-auto mb-12">
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="font-headline text-3xl font-bold tracking-tight text-on-surface mb-2">{featured_event}</h1>
        <p class="text-on-surface-variant flex items-center gap-2">
          <span class="material-symbols-outlined text-sm">calendar_today</span>
          April 28, 2026
          <span class="mx-2 text-outline-variant">&bull;</span>
          <span class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 bg-tertiary-fixed text-on-tertiary-fixed rounded-md">
            <span class="material-symbols-outlined text-xs">database</span>
            Scraped Event
          </span>
        </p>
      </div>
      <div class="flex gap-2">
        <span class="px-3 py-1 rounded-full bg-secondary-fixed text-on-secondary-fixed-variant text-xs font-semibold">Active Search</span>
        <span class="px-3 py-1 rounded-full bg-surface-container-high text-on-surface-variant text-xs font-semibold">{match_count} Matches Found</span>
      </div>
    </div>
    <div class="relative group mb-4">
      <div class="absolute inset-y-0 left-6 flex items-center pointer-events-none">
        <span class="material-symbols-outlined text-primary">search</span>
      </div>
      <input class="w-full pl-14 pr-6 py-5 bg-surface-container-lowest border-none rounded-2xl shadow-sm text-lg focus:ring-2 focus:ring-primary/20 placeholder:text-outline/60 transition-all" placeholder="Find internal specialists for {featured_event}..." type="text"/>
    </div>
    <div class="flex flex-wrap gap-2 px-1">
      <button class="flex items-center gap-2 px-4 py-2 bg-surface-container-low hover:bg-surface-container-high text-on-surface-variant rounded-full text-xs font-medium transition-colors">
        <span class="material-symbols-outlined text-sm">score</span>
        Score matches
      </button>
      <button class="flex items-center gap-2 px-4 py-2 bg-surface-container-low hover:bg-surface-container-high text-on-surface-variant rounded-full text-xs font-medium transition-colors">
        <span class="material-symbols-outlined text-sm">auto_fix_high</span>
        Generate outreach
      </button>
      <button class="flex items-center gap-2 px-4 py-2 bg-surface-container-low hover:bg-surface-container-high text-on-surface-variant rounded-full text-xs font-medium transition-colors">
        <span class="material-symbols-outlined text-sm">filter_list</span>
        Diversity filter
      </button>
      <button class="flex items-center gap-2 px-4 py-2 bg-surface-container-low hover:bg-surface-container-high text-on-surface-variant rounded-full text-xs font-medium transition-colors">
        <span class="material-symbols-outlined text-sm">share</span>
        Export list
      </button>
    </div>
  </header>

  <!-- Internal Specialist Matches Section -->
  <section class="max-w-4xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h3 class="font-headline text-xl font-semibold">Internal Specialist Matches</h3>
      <button class="text-primary text-sm font-semibold flex items-center gap-1">View All <span class="material-symbols-outlined text-sm">arrow_forward</span></button>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      {spec_cards_html}
      {featured_card_html}
    </div>
  </section>
</main>

<!-- Right Rail Details -->
<aside class="w-80 h-screen fixed right-0 top-0 bg-white border-l border-outline-variant/20 p-6 z-40 overflow-y-auto">
  <div class="mb-10">
    <h3 class="font-headline text-lg font-semibold mb-6 flex items-center gap-2">
      <span class="material-symbols-outlined text-primary" style="font-variation-settings: 'FILL' 1;">info</span>
      Event Intelligence
    </h3>

    <!-- Verified POC -->
    {poc_html}

    <!-- AI Reasoning -->
    <div class="bg-primary/5 p-4 rounded-2xl border border-primary/10 mb-6">
      <div class="flex items-center gap-2 mb-2">
        <span class="material-symbols-outlined text-primary text-sm">psychology</span>
        <span class="text-xs font-bold text-primary uppercase tracking-wider">AI Reasoning</span>
      </div>
      <p class="text-xs text-on-surface-variant leading-relaxed">{ai_reasoning}</p>
    </div>

    <!-- Target Audience -->
    <div class="bg-surface p-4 rounded-2xl mb-6">
      <div class="text-[10px] font-bold text-outline uppercase tracking-wider mb-2">TARGET AUDIENCE</div>
      <p class="text-sm font-medium text-on-surface mb-4">500+ CPP Undergraduates specializing in Business and Technology.</p>
      <div class="flex -space-x-2">
        <div class="w-8 h-8 rounded-full border-2 border-surface bg-primary-container flex items-center justify-center text-white text-[10px] font-bold">A</div>
        <div class="w-8 h-8 rounded-full border-2 border-surface bg-secondary flex items-center justify-center text-white text-[10px] font-bold">B</div>
        <div class="w-8 h-8 rounded-full border-2 border-surface bg-surface-container-high flex items-center justify-center text-[10px] font-bold">+12</div>
      </div>
    </div>

    <!-- Calendar Preview -->
    <div class="mb-8">
      <div class="flex justify-between items-center mb-4">
        <h4 class="text-xs font-bold text-outline uppercase tracking-wider">Availability (April)</h4>
        <span class="text-[10px] text-primary font-bold">Show detailed view</span>
      </div>
      <div class="grid grid-cols-7 gap-1 text-center">
        <div class="text-[8px] font-bold py-1">M</div>
        <div class="text-[8px] font-bold py-1">T</div>
        <div class="text-[8px] font-bold py-1">W</div>
        <div class="text-[8px] font-bold py-1">T</div>
        <div class="text-[8px] font-bold py-1">F</div>
        <div class="text-[8px] font-bold py-1">S</div>
        <div class="text-[8px] font-bold py-1">S</div>
        <div class="text-[10px] p-1 text-outline">24</div>
        <div class="text-[10px] p-1 text-outline">25</div>
        <div class="text-[10px] p-1 text-outline">26</div>
        <div class="text-[10px] p-1 text-outline">27</div>
        <div class="text-[10px] p-1 bg-primary text-white rounded-md font-bold">28</div>
        <div class="text-[10px] p-1">29</div>
        <div class="text-[10px] p-1">30</div>
      </div>
    </div>

    <!-- Outreach Preview -->
    <div class="space-y-4">
      <h4 class="text-xs font-bold text-outline uppercase tracking-wider">Outreach Preview</h4>
      <div class="bg-surface-container-lowest border border-outline-variant/30 rounded-xl p-4">
        <p class="text-[11px] text-on-surface-variant font-medium mb-2">Subject: Speaking at CPP Career Fair...</p>
        <p class="text-[11px] text-on-surface-variant/80 italic line-clamp-3">
          Hi [Speaker Name], given your incredible background in [Expertise] and your role as an internal specialist at IA West...
        </p>
        <div class="mt-3 pt-3 border-t border-outline-variant/10 flex justify-between items-center">
          <span class="text-[10px] text-primary font-bold">Edit Template</span>
          <span class="material-symbols-outlined text-sm text-outline">open_in_new</span>
        </div>
      </div>
    </div>
  </div>

  <div class="mt-auto">
    <button class="w-full py-4 bg-surface-container-high text-on-surface font-bold rounded-2xl text-sm flex items-center justify-center gap-2 hover:bg-surface-container-highest transition-colors">
      <span class="material-symbols-outlined text-sm">mail</span>
      Send Bulk Outreach
    </button>
  </div>
</aside>
"""

    render_html_page(
        body_html,
        title="IA SmartMatch | Match Engine",
        height=5000,
        hide_chrome=False,
    )

    # ── Streamlit Navigation Buttons ─────────────────────────────────────────
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("< Back to Dashboard", use_container_width=True):
            navigate_to("coordinator")
    with col2:
        if st.button("Sign Out", use_container_width=True):
            set_user_role(None)  # type: ignore[arg-type]
            navigate_to("landing")


# ── Helper ────────────────────────────────────────────────────────────────────

def _build_factor_bars(widths: dict[str, str]) -> str:
    """Return HTML for the 6-factor progress bar grid inside a specialist card."""
    factors = ["Topic", "Role", "Prox.", "Cal.", "Hist.", "Impact"]
    html_parts: list[str] = []
    for factor in factors:
        width = widths.get(factor, "80%")
        html_parts.append(
            f'<div class="flex flex-col gap-1">'
            f'<span class="text-[9px] text-outline font-bold uppercase">{factor}</span>'
            f'<div class="h-1 bg-surface-container-low rounded-full overflow-hidden">'
            f'<div class="h-full bg-primary" style="width:{width}"></div>'
            f"</div>"
            f"</div>"
        )
    return "\n".join(html_parts)
