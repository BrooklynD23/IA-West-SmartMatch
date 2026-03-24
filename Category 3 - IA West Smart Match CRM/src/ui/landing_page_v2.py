"""
Landing page v2 for IA SmartMatch — pixel-faithful reproduction of the
ia_smartmatch_landing_page_updated mockup.

Renders a complete full-page HTML experience via st.components.v1.html()
with Streamlit chrome hidden. Real specialist data (Travis Miller) is pulled
from data_helpers.load_specialists() and injected into the product preview
bento section.

Public API::

    render_landing_page_v2() -> None
"""

from __future__ import annotations

import streamlit as st

from src.ui.data_helpers import load_specialists
from src.ui.html_base import render_html_page
from src.ui.page_router import navigate_to, set_user_role


def _get_travis_miller(specialists: list[dict[str, str]]) -> dict[str, str]:
    """Return the Travis Miller specialist entry, or a fallback dict.

    Args:
        specialists: List of specialist dicts from load_specialists().

    Returns:
        Dict with keys: name, title, company, initials.
    """
    for s in specialists:
        if "travis" in s.get("name", "").lower():
            return s
    # Fallback if data file is missing or name not found
    return {
        "name": "Travis Miller",
        "title": "President",
        "company": "PureSpectrum",
        "initials": "TM",
    }


def _build_body(specialist: dict[str, str]) -> str:
    """Build the full HTML body string from the mockup.

    Args:
        specialist: Dict with name, title, company, initials keys.

    Returns:
        HTML body string (nav through footer, no <html>/<head>/<body> tags).
    """
    name = specialist.get("name", "Travis Miller")
    title = specialist.get("title", "President")
    company = specialist.get("company", "PureSpectrum")
    initials = specialist.get("initials", "TM")
    specialist_subtitle = f"{title}, {company} &bull; Specialist CRM"

    return f"""
<!-- Top Navigation Shell -->
<nav class="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl shadow-sm dark:shadow-none docked full-width top-0 z-50 flex justify-between items-center w-full px-8 py-4 max-w-full mx-auto fixed">
  <div class="flex items-center gap-8">
    <span class="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-50 font-headline">IA SmartMatch</span>
    <div class="hidden md:flex gap-6">
      <a class="text-blue-700 dark:text-blue-400 font-semibold border-b-2 border-blue-700 dark:border-blue-400 pb-1" href="#">Dashboard</a>
      <a class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-300 transition-colors" href="#">Matches</a>
      <a class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-300 transition-colors" href="#">Pipeline</a>
      <a class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-300 transition-colors" href="#">Discovery</a>
      <a class="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-300 transition-colors" href="#">Analytics</a>
    </div>
  </div>
  <div class="flex gap-4">
    <button class="text-slate-600 font-medium px-4 py-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-all"
            onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'login'}}, '*')">Sign in</button>
    <button class="hero-gradient text-white px-6 py-2 rounded-xl font-semibold shadow-sm hover:opacity-90 active:scale-[0.98] transition-all">Add Specialist</button>
  </div>
</nav>

<main class="pt-24">

  <!-- Hero Section -->
  <section class="px-8 py-20 max-w-7xl mx-auto flex flex-col items-center text-center">
    <span class="text-primary font-semibold tracking-wider uppercase text-sm mb-4">AI-Driven Opportunity Matching for IA West</span>
    <h1 class="text-5xl md:text-7xl font-bold font-headline tracking-tight text-on-surface max-w-4xl leading-[1.1] mb-8">
      Match your specialist database with every university opportunity
    </h1>
    <p class="text-xl text-on-surface-variant max-w-2xl mb-12">
      Bridge the gap between your internal industry expertise and live academic needs through automated web-scraped signals and high-fidelity matching.
    </p>
    <div class="flex flex-wrap gap-4 justify-center">
      <button class="hero-gradient text-on-primary px-8 py-4 rounded-xl text-lg font-bold shadow-lg" href="#">Start Matching</button>
      <button class="bg-surface-container-high text-on-surface px-8 py-4 rounded-xl text-lg font-semibold" href="#">View Demo</button>
    </div>
  </section>

  <!-- Product Preview Mockup (Bento Style) -->
  <section class="px-8 pb-32 max-w-7xl mx-auto">
    <div class="bg-surface-container-low rounded-[2.5rem] p-4 md:p-8 shadow-sm">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">

        <!-- Main Event Card -->
        <div class="lg:col-span-8 bg-surface-container-lowest rounded-2xl p-8 shadow-sm">
          <div class="flex justify-between items-start mb-12">
            <div>
              <span class="text-primary font-bold text-xs uppercase tracking-widest mb-2 block">Scraped Opportunity</span>
              <h3 class="text-3xl font-headline font-bold">UCLA Career Fair 2026</h3>
              <p class="text-on-surface-variant mt-1">Luskin Conference Center &bull; May 14, 2026</p>
            </div>
            <div class="bg-secondary-fixed text-on-secondary-fixed px-4 py-2 rounded-full flex items-center gap-2">
              <span class="material-symbols-outlined text-sm">school</span>
              <span class="text-sm font-semibold">High Priority</span>
            </div>
          </div>
          <div class="space-y-6">
            <h4 class="text-sm font-bold text-on-surface-variant uppercase tracking-tighter">Database Specialist Recommendations</h4>
            <!-- Recommendation 1 -->
            <div class="flex items-center justify-between p-6 bg-surface-container rounded-2xl border border-primary/10">
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container font-bold">{initials}</div>
                <div>
                  <p class="font-bold text-lg">{name}</p>
                  <p class="text-sm text-on-surface-variant">{specialist_subtitle}</p>
                </div>
              </div>
              <div class="flex gap-8 items-center">
                <div class="text-center">
                  <p class="text-xs text-on-surface-variant uppercase">Match Score</p>
                  <p class="text-xl font-bold text-primary">94%</p>
                </div>
                <button class="bg-primary text-white px-4 py-2 rounded-lg text-sm font-bold">Sync CRM</button>
              </div>
            </div>
            <!-- Detail View Integration -->
            <div class="grid grid-cols-3 gap-4">
              <div class="bg-surface p-4 rounded-xl text-center">
                <p class="text-primary font-bold text-lg">35%</p>
                <p class="text-xs text-on-surface-variant uppercase font-medium">Domain Relevance</p>
              </div>
              <div class="bg-surface p-4 rounded-xl text-center">
                <p class="text-primary font-bold text-lg">25%</p>
                <p class="text-xs text-on-surface-variant uppercase font-medium">Scraped Role Fit</p>
              </div>
              <div class="bg-surface p-4 rounded-xl text-center">
                <p class="text-primary font-bold text-lg">20%</p>
                <p class="text-xs text-on-surface-variant uppercase font-medium">Location</p>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Explanation Column -->
        <div class="lg:col-span-4 space-y-8">
          <div class="bg-primary-container text-on-primary-container p-8 rounded-2xl h-full flex flex-col">
            <div class="flex items-center gap-2 mb-6">
              <span class="material-symbols-outlined" data-weight="fill">auto_awesome</span>
              <h4 class="font-headline font-bold text-xl">Bridge Logic</h4>
            </div>
            <p class="text-lg leading-relaxed mb-8 opacity-90">
              {name}'s profile in your Specialist CRM aligns with UCLA's web-scraped event data focused on "Sales Leadership in SaaS." His history suggests a high-fidelity match for this discovered opportunity.
            </p>
            <div class="mt-auto space-y-4">
              <div class="flex justify-between text-sm">
                <span>Signal Integrity</span>
                <span class="font-bold">Excellent</span>
              </div>
              <div class="w-full bg-white/20 h-1 rounded-full overflow-hidden">
                <div class="bg-white h-full w-[92%]"></div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- Features Grid -->
  <section class="bg-surface-container-low py-32">
    <div class="px-8 max-w-7xl mx-auto">
      <div class="mb-20">
        <h2 class="text-4xl font-headline font-bold mb-4">Complete Specialist Engagement Pipeline</h2>
        <p class="text-on-surface-variant max-w-xl">A unified platform to bridge your internal specialist database with external university opportunities.</p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-12">
        <div class="flex flex-col gap-6">
          <div class="w-14 h-14 rounded-2xl bg-white flex items-center justify-center shadow-sm text-primary">
            <span class="material-symbols-outlined text-3xl">language</span>
          </div>
          <h3 class="text-2xl font-headline font-bold">Proprietary Web Scraping</h3>
          <p class="text-on-surface-variant">Real-time automation monitors university portals to identify speaking slots, panels, and academic needs across the West Coast.</p>
        </div>
        <div class="flex flex-col gap-6">
          <div class="w-14 h-14 rounded-2xl bg-white flex items-center justify-center shadow-sm text-primary">
            <span class="material-symbols-outlined text-3xl">groups</span>
          </div>
          <h3 class="text-2xl font-headline font-bold">Industry Specialist CRM</h3>
          <p class="text-on-surface-variant">Centralize your internal database of volunteers with enriched profiles, expertise tracking, and availability management.</p>
        </div>
        <div class="flex flex-col gap-6">
          <div class="w-14 h-14 rounded-2xl bg-white flex items-center justify-center shadow-sm text-primary">
            <span class="material-symbols-outlined text-3xl">hub</span>
          </div>
          <h3 class="text-2xl font-headline font-bold">Bridge Matching</h3>
          <p class="text-on-surface-variant">Proprietary algorithms bridge the gap between internal CRM expertise and scraped event requirements for optimal placement.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Technical Visualization: 6-factor MATCH_SCORE -->
  <section class="py-32 px-8 max-w-7xl mx-auto overflow-hidden">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
      <div>
        <h2 class="text-4xl font-headline font-bold mb-6 leading-tight">The Bridge: 6-factor MATCH_SCORE</h2>
        <p class="text-lg text-on-surface-variant mb-10">Our engine cross-references internal specialist data with scraped event parameters to maximize the impact of every engagement.</p>
        <div class="bg-white dark:bg-slate-800 p-8 rounded-3xl shadow-sm border border-outline-variant/10">
          <div class="flex items-center gap-3 mb-6">
            <span class="material-symbols-outlined text-primary">analytics</span>
            <h3 class="text-xl font-headline font-bold">Match Verification</h3>
          </div>
          <div class="space-y-6">
            <div class="flex gap-4">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-primary text-xl">database</span>
              </div>
              <div>
                <p class="font-bold text-sm uppercase tracking-wider text-on-surface-variant mb-1">CRM Profile Sync</p>
                <p class="text-on-surface">Specialist expertise in SaaS sales leadership matches 100% of the course curriculum scraped from UCLA.</p>
              </div>
            </div>
            <div class="flex gap-4">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-primary text-xl">travel_explore</span>
              </div>
              <div>
                <p class="font-bold text-sm uppercase tracking-wider text-on-surface-variant mb-1">Scraped Calendar Match</p>
                <p class="text-on-surface">CRM availability shows 3 overlapping slots with the university's priority window discovered via scraping.</p>
              </div>
            </div>
            <div class="flex gap-4">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-primary text-xl">location_on</span>
              </div>
              <div>
                <p class="font-bold text-sm uppercase tracking-wider text-on-surface-variant mb-1">Geospatial Synergies</p>
                <p class="text-on-surface">Internal location data aligns with the scraped event venue, ensuring low-friction logistical coordination.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SVG Donut Chart -->
      <div class="relative">
        <div class="bg-surface-container rounded-3xl p-8 aspect-square flex flex-col items-center justify-center relative">
          <div class="absolute inset-0 bg-primary/5 rounded-3xl transform rotate-2 -z-10"></div>
          <div class="w-full max-w-md aspect-square relative flex items-center justify-center">
            <!-- Outer Ring (Segmented) -->
            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <!-- CRM Expertise (35%) -->
              <circle class="text-primary" cx="50" cy="50" fill="transparent" r="42"
                stroke="currentColor" stroke-dasharray="35 65" stroke-dashoffset="0"
                stroke-linecap="round" stroke-width="8"></circle>
              <!-- Scraped Event Fit (25%) -->
              <circle class="text-primary/70" cx="50" cy="50" fill="transparent" r="42"
                stroke="currentColor" stroke-dasharray="25 75" stroke-dashoffset="-36"
                stroke-linecap="round" stroke-width="8"></circle>
              <!-- Proximity (20%) -->
              <circle class="text-primary/50" cx="50" cy="50" fill="transparent" r="42"
                stroke="currentColor" stroke-dasharray="20 80" stroke-dashoffset="-62"
                stroke-linecap="round" stroke-width="8"></circle>
              <!-- Calendar Sync (15%) -->
              <circle class="text-primary/30" cx="50" cy="50" fill="transparent" r="42"
                stroke="currentColor" stroke-dasharray="15 85" stroke-dashoffset="-83"
                stroke-linecap="round" stroke-width="8"></circle>
              <!-- Engagement History (5%) -->
              <circle class="text-primary/10" cx="50" cy="50" fill="transparent" r="42"
                stroke="currentColor" stroke-dasharray="5 95" stroke-dashoffset="-99"
                stroke-linecap="round" stroke-width="8"></circle>
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <div class="w-32 h-32 bg-white dark:bg-slate-900 rounded-full shadow-2xl flex flex-col items-center justify-center border-4 border-surface">
                <span class="text-xs uppercase font-bold text-on-surface-variant opacity-60">Match Score</span>
                <span class="text-5xl font-headline font-bold text-primary">94</span>
              </div>
            </div>
            <!-- Labels -->
            <div class="absolute -top-4 -right-4 bg-white px-4 py-2 rounded-xl shadow-lg border border-outline-variant/10 text-xs font-bold">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-primary"></div>
                CRM Expertise: 35%
              </div>
            </div>
            <div class="absolute top-1/2 -right-12 bg-white px-4 py-2 rounded-xl shadow-lg border border-outline-variant/10 text-xs font-bold">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-primary/70"></div>
                Scraped Event Fit: 25%
              </div>
            </div>
            <div class="absolute -bottom-4 right-4 bg-white px-4 py-2 rounded-xl shadow-lg border border-outline-variant/10 text-xs font-bold">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-primary/50"></div>
                Proximity: 20%
              </div>
            </div>
            <div class="absolute -bottom-8 left-0 bg-white px-4 py-2 rounded-xl shadow-lg border border-outline-variant/10 text-xs font-bold">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-primary/30"></div>
                Calendar Sync: 15%
              </div>
            </div>
            <div class="absolute top-1/4 -left-12 bg-white px-4 py-2 rounded-xl shadow-lg border border-outline-variant/10 text-xs font-bold">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-primary/10"></div>
                History: 5%
              </div>
            </div>
          </div>
          <div class="mt-12 text-center">
            <p class="font-headline font-bold text-xl">CRM Specialist Profile: {name}</p>
            <p class="text-on-surface-variant">Bridged with Scraped UCLA Opportunity Data</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Automation Pipeline -->
  <section class="bg-surface-container py-32 px-8 overflow-hidden">
    <div class="max-w-7xl mx-auto">
      <div class="grid lg:grid-cols-2 gap-24 items-center">
        <div class="order-2 lg:order-1 relative">
          <div class="space-y-4">
            <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-primary">
              <p class="font-mono text-sm text-on-surface-variant flex gap-2">
                <span class="text-primary">SCRAPE</span> https://career.ucla.edu/api/events
              </p>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm ml-8 opacity-80">
              <div class="flex items-center gap-4 mb-2">
                <div class="w-3 h-3 rounded-full bg-green-500"></div>
                <span class="text-sm font-bold uppercase tracking-wider">Parsing Discovered Data...</span>
              </div>
              <div class="space-y-2">
                <div class="h-2 bg-surface-container rounded w-full"></div>
                <div class="h-2 bg-surface-container rounded w-[80%]"></div>
              </div>
            </div>
            <div class="bg-primary p-6 rounded-2xl shadow-lg ml-16 text-white flex items-center justify-between">
              <div class="flex items-center gap-4">
                <span class="material-symbols-outlined">sync</span>
                <span class="font-bold">Syncing with Specialist CRM...</span>
              </div>
              <span class="material-symbols-outlined">chevron_right</span>
            </div>
          </div>
        </div>
        <div class="order-1 lg:order-2">
          <h2 class="text-4xl font-headline font-bold mb-8">Proprietary Web Scraping</h2>
          <p class="text-lg text-on-surface-variant leading-relaxed mb-8">
            Our scraping pipeline monitors UCLA, USC, and dozens of other university sites in real-time. No more manual searching; discovered opportunities are instantly cross-referenced against your internal database of specialists.
          </p>
          <div class="flex items-center gap-6">
            <div class="flex -space-x-4">
              <div class="w-12 h-12 rounded-full border-4 border-white bg-slate-200 flex items-center justify-center text-xs font-bold">UCLA</div>
              <div class="w-12 h-12 rounded-full border-4 border-white bg-slate-200 flex items-center justify-center text-xs font-bold">USC</div>
              <div class="w-12 h-12 rounded-full border-4 border-white bg-slate-200 flex items-center justify-center text-xs font-bold">SDSU</div>
            </div>
            <p class="text-sm font-bold text-on-surface-variant">+42 Sources Monitored</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Analytics Dashboard Section -->
  <section class="py-32 px-8 max-w-7xl mx-auto">
    <h2 class="text-4xl font-headline font-bold mb-16 text-center">Engagement &amp; Scraping Analytics</h2>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div class="lg:col-span-2 bg-surface-container-lowest rounded-3xl p-8 shadow-sm">
        <div class="flex justify-between items-center mb-12">
          <h3 class="text-xl font-bold font-headline">Opportunity Density Heat Map</h3>
          <div class="flex gap-2">
            <span class="px-3 py-1 bg-surface-container rounded-lg text-xs font-bold">Scraped Leads</span>
            <span class="px-3 py-1 bg-surface-container rounded-lg text-xs font-bold">CRM Matches</span>
          </div>
        </div>
        <!-- Placeholder for heatmap (no external image) -->
        <div class="h-80 bg-surface-container rounded-2xl relative overflow-hidden flex items-center justify-center">
          <div class="absolute inset-0 bg-gradient-to-br from-primary/10 via-primary/5 to-surface-container-high"></div>
          <div class="relative flex flex-col items-center gap-2">
            <div class="w-12 h-12 bg-primary rounded-full animate-pulse opacity-50 absolute -top-8 -left-20"></div>
            <div class="w-16 h-16 bg-primary rounded-full animate-pulse opacity-70"></div>
            <p class="font-bold text-primary mt-4">High Opportunity: Los Angeles Hub</p>
          </div>
        </div>
      </div>
      <div class="bg-surface-container-lowest rounded-3xl p-8 shadow-sm">
        <h3 class="text-xl font-bold font-headline mb-12">Matching Funnel</h3>
        <div class="space-y-8">
          <div>
            <div class="flex justify-between mb-2">
              <span class="text-sm font-bold">Discovered (Scraped)</span>
              <span class="text-sm">2,481</span>
            </div>
            <div class="h-3 bg-surface-container rounded-full overflow-hidden">
              <div class="h-full bg-primary w-full"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between mb-2">
              <span class="text-sm font-bold">CRM Potential Matches</span>
              <span class="text-sm">842</span>
            </div>
            <div class="h-3 bg-surface-container rounded-full overflow-hidden">
              <div class="h-full bg-primary w-[34%]"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between mb-2">
              <span class="text-sm font-bold">Specialist Confirmed</span>
              <span class="text-sm">114</span>
            </div>
            <div class="h-3 bg-surface-container rounded-full overflow-hidden">
              <div class="h-full bg-primary w-[5%]"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Partner Showcase -->
  <section class="py-24 border-y border-surface-container">
    <div class="px-8 max-w-7xl mx-auto">
      <p class="text-center text-on-surface-variant font-bold uppercase tracking-widest text-xs mb-12">Bridging CRM Data to</p>
      <div class="flex flex-wrap justify-center gap-12 md:gap-24 grayscale opacity-60">
        <span class="text-2xl font-headline font-extrabold">CPP</span>
        <span class="text-2xl font-headline font-extrabold">UCLA</span>
        <span class="text-2xl font-headline font-extrabold">SDSU</span>
        <span class="text-2xl font-headline font-extrabold">UC DAVIS</span>
        <span class="text-2xl font-headline font-extrabold">USC</span>
        <span class="text-2xl font-headline font-extrabold">PORTLAND STATE</span>
      </div>
    </div>
  </section>

  <!-- Final CTA -->
  <section class="px-8 py-32 max-w-5xl mx-auto text-center">
    <h2 class="text-5xl font-headline font-bold mb-8">Ready to sync your database with the web?</h2>
    <p class="text-xl text-on-surface-variant mb-12 max-w-2xl mx-auto">Join the IA West network and transform how your internal specialist database interacts with real-world university opportunities.</p>
    <div class="flex flex-wrap gap-4 justify-center">
      <button class="hero-gradient text-on-primary px-10 py-5 rounded-2xl text-xl font-bold shadow-xl active:scale-95 transition-all">Connect Database</button>
      <button class="bg-surface-container-lowest text-on-surface px-10 py-5 rounded-2xl text-xl font-bold shadow-sm border border-outline-variant/20 hover:bg-surface-container transition-all">Schedule Demo</button>
    </div>
  </section>

</main>

<!-- Footer -->
<footer class="w-full border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900">
  <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 px-12 py-16 w-full max-w-7xl mx-auto">
    <div class="col-span-2">
      <span class="text-md font-bold text-slate-900 dark:text-slate-100 font-headline mb-4 block">IA SmartMatch</span>
      <p class="text-slate-500 dark:text-slate-400 max-w-xs">Connecting internal specialist CRM data with real-time scraped academic opportunities.</p>
    </div>
    <div class="space-y-4">
      <p class="font-headline font-semibold text-slate-900 dark:text-white">Product</p>
      <ul class="space-y-2">
        <li><a class="text-slate-500 dark:text-slate-400 hover:text-blue-700 transition-colors" href="#">Specialist CRM</a></li>
        <li><a class="text-slate-500 dark:text-slate-400 hover:text-blue-700 transition-colors" href="#">Scraping Engine</a></li>
      </ul>
    </div>
    <div class="space-y-4">
      <p class="font-headline font-semibold text-slate-900 dark:text-white">About</p>
      <ul class="space-y-2">
        <li><a class="text-slate-500 dark:text-slate-400 hover:text-blue-700 transition-colors" href="#">About IA West</a></li>
        <li><a class="text-slate-500 dark:text-slate-400 hover:text-blue-700 transition-colors" href="#">Contact</a></li>
      </ul>
    </div>
    <div class="space-y-4">
      <p class="font-headline font-semibold text-slate-900 dark:text-white">Legal</p>
      <ul class="space-y-2">
        <li><a class="text-slate-500 dark:text-slate-400 hover:text-blue-700 transition-colors" href="#">Privacy</a></li>
        <li><a class="text-slate-500 dark:text-slate-400 hover:text-blue-700 transition-colors" href="#">Legal</a></li>
      </ul>
    </div>
  </div>
  <div class="px-12 py-8 border-t border-slate-50 dark:border-slate-800 max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
    <p class="text-slate-400 text-sm">&copy; 2026 IA West. All rights reserved.</p>
    <div class="flex gap-6">
      <span class="material-symbols-outlined text-slate-400 cursor-pointer hover:text-blue-600 transition-colors">language</span>
      <span class="material-symbols-outlined text-slate-400 cursor-pointer hover:text-blue-600 transition-colors">public</span>
    </div>
  </div>
</footer>
"""


def render_landing_page_v2() -> None:
    """Render the IA SmartMatch landing page v2.

    Loads real specialist data, builds the full HTML body reproducing the
    ia_smartmatch_landing_page_updated mockup, and renders it via
    st.components.v1.html() with Streamlit chrome hidden.

    After the HTML component, renders Streamlit navigation buttons:
    - "Sign In" navigates to the login page.
    - "View Demo" sets user role to coordinator and navigates to that page.
    """
    specialists = load_specialists()
    specialist = _get_travis_miller(specialists)

    body_html = _build_body(specialist)

    render_html_page(
        body_html,
        title="IA SmartMatch | Specialist-to-Opportunity AI Matching",
        height=6000,
        hide_chrome=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Sign In", type="primary", use_container_width=True):
            navigate_to("login")
    with col2:
        if st.button("View Demo", use_container_width=True):
            set_user_role("coordinator")
            navigate_to("coordinator")
