import { Link } from "react-router";

export function LandingPage() {
  return (
    <div className="min-h-screen bg-[#f7f9fc] font-[Inter] text-[#191c1e]">
      {/* Nav - only Sign In */}
      <nav className="bg-white/80 backdrop-blur-xl shadow-sm fixed top-0 z-50 flex justify-between items-center w-full px-8 py-4">
        <span className="text-xl font-bold tracking-tight font-[Inter_Tight]">IA SmartMatch</span>
        <Link
          to="/login"
          className="bg-gradient-to-r from-[#005394] to-[#2b6cb0] text-white px-6 py-2 rounded-xl font-semibold shadow-sm hover:opacity-90 active:scale-[0.98] transition-all"
        >
          Sign In
        </Link>
      </nav>

      <main className="pt-24">
        {/* Hero */}
        <section className="px-8 py-20 max-w-7xl mx-auto flex flex-col items-center text-center">
          <span className="text-[#005394] font-semibold tracking-wider uppercase text-sm mb-4">
            AI-Driven Opportunity Matching for IA West
          </span>
          <h1 className="text-5xl md:text-7xl font-bold font-[Inter_Tight] tracking-tight max-w-4xl leading-[1.1] mb-8">
            Match your specialist database with every university opportunity
          </h1>
          <p className="text-xl text-[#414750] max-w-2xl mb-12">
            Bridge the gap between your internal industry expertise and live academic needs through
            automated web-scraped signals and high-fidelity matching.
          </p>
          <Link
            to="/login"
            className="bg-gradient-to-r from-[#005394] to-[#2b6cb0] text-white px-8 py-4 rounded-xl text-lg font-bold shadow-lg hover:opacity-90 transition-all"
          >
            Get Started
          </Link>
        </section>

        {/* Product Preview */}
        <section className="px-8 pb-32 max-w-7xl mx-auto">
          <div className="bg-[#f2f4f7] rounded-[2.5rem] p-4 md:p-8 shadow-sm">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Main Event Card */}
              <div className="lg:col-span-8 bg-white rounded-2xl p-8 shadow-sm">
                <div className="flex justify-between items-start mb-12">
                  <div>
                    <span className="text-[#005394] font-bold text-xs uppercase tracking-widest mb-2 block">
                      Scraped Opportunity
                    </span>
                    <h3 className="text-3xl font-[Inter_Tight] font-bold">UCLA Career Fair 2026</h3>
                    <p className="text-[#414750] mt-1">Luskin Conference Center &bull; May 14, 2026</p>
                  </div>
                  <div className="bg-[#d5e0f7] text-[#111c2c] px-4 py-2 rounded-full flex items-center gap-2">
                    <span className="text-sm font-semibold">High Priority</span>
                  </div>
                </div>
                <div className="space-y-6">
                  <h4 className="text-sm font-bold text-[#414750] uppercase tracking-tighter">
                    Database Specialist Recommendations
                  </h4>
                  <div className="flex items-center justify-between p-6 bg-[#eceef1] rounded-2xl border border-[#005394]/10">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-[#2b6cb0] flex items-center justify-center text-white font-bold">
                        TM
                      </div>
                      <div>
                        <p className="font-bold text-lg">Travis Miller</p>
                        <p className="text-sm text-[#414750]">SVP Sales, TechCorp &bull; Specialist CRM</p>
                      </div>
                    </div>
                    <div className="flex gap-8 items-center">
                      <div className="text-center">
                        <p className="text-xs text-[#414750] uppercase">Match Score</p>
                        <p className="text-xl font-bold text-[#005394]">94%</p>
                      </div>
                      <button className="bg-[#005394] text-white px-4 py-2 rounded-lg text-sm font-bold">
                        Sync CRM
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { label: "Domain Relevance", value: "35%" },
                      { label: "Scraped Role Fit", value: "25%" },
                      { label: "Location", value: "20%" },
                    ].map((item) => (
                      <div key={item.label} className="bg-[#f7f9fc] p-4 rounded-xl text-center">
                        <p className="text-[#005394] font-bold text-lg">{item.value}</p>
                        <p className="text-xs text-[#414750] uppercase font-medium">{item.label}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Bridge Logic Panel */}
              <div className="lg:col-span-4">
                <div className="bg-[#2b6cb0] text-white p-8 rounded-2xl h-full flex flex-col">
                  <h4 className="font-[Inter_Tight] font-bold text-xl mb-6">Bridge Logic</h4>
                  <p className="text-lg leading-relaxed mb-8 opacity-90">
                    Travis's profile in your Specialist CRM aligns with UCLA's web-scraped event data
                    focused on "Sales Leadership in SaaS." His history suggests a high-fidelity match
                    for this discovered opportunity.
                  </p>
                  <div className="mt-auto space-y-4">
                    <div className="flex justify-between text-sm">
                      <span>Signal Integrity</span>
                      <span className="font-bold">Excellent</span>
                    </div>
                    <div className="w-full bg-white/20 h-1 rounded-full overflow-hidden">
                      <div className="bg-white h-full w-[92%]" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="bg-[#f2f4f7] py-32">
          <div className="px-8 max-w-7xl mx-auto">
            <div className="mb-20">
              <h2 className="text-4xl font-[Inter_Tight] font-bold mb-4">
                Complete Specialist Engagement Pipeline
              </h2>
              <p className="text-[#414750] max-w-xl">
                A unified platform to bridge your internal specialist database with external
                university opportunities.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              {[
                {
                  title: "Proprietary Web Scraping",
                  desc: "Real-time automation monitors university portals to identify speaking slots, panels, and academic needs across the West Coast.",
                },
                {
                  title: "Industry Specialist CRM",
                  desc: "Centralize your internal database of volunteers with enriched profiles, expertise tracking, and availability management.",
                },
                {
                  title: "Bridge Matching",
                  desc: "Proprietary algorithms bridge the gap between internal CRM expertise and scraped event requirements for optimal placement.",
                },
              ].map((feature) => (
                <div key={feature.title} className="flex flex-col gap-6">
                  <div className="w-14 h-14 rounded-2xl bg-white flex items-center justify-center shadow-sm text-[#005394]">
                    <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-[Inter_Tight] font-bold">{feature.title}</h3>
                  <p className="text-[#414750]">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Match Score Visualization */}
        <section className="py-32 px-8 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
            <div>
              <h2 className="text-4xl font-[Inter_Tight] font-bold mb-6 leading-tight">
                The Bridge: 6-factor MATCH_SCORE
              </h2>
              <p className="text-lg text-[#414750] mb-10">
                Our engine cross-references internal specialist data with scraped event parameters to
                maximize the impact of every engagement.
              </p>
              <div className="bg-white p-8 rounded-3xl shadow-sm border border-[#c1c7d2]/10">
                <h3 className="text-xl font-[Inter_Tight] font-bold mb-6">Match Verification</h3>
                <div className="space-y-6">
                  {[
                    { label: "CRM Profile Sync", desc: "Specialist expertise matches 100% of the course curriculum scraped from UCLA." },
                    { label: "Scraped Calendar Match", desc: "CRM availability shows 3 overlapping slots with the university's priority window." },
                    { label: "Geospatial Synergies", desc: "Internal location data aligns with the scraped event venue for low-friction coordination." },
                  ].map((item) => (
                    <div key={item.label} className="flex gap-4">
                      <div className="w-10 h-10 rounded-full bg-[#005394]/10 flex items-center justify-center shrink-0">
                        <svg className="w-5 h-5 text-[#005394]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-bold text-sm uppercase tracking-wider text-[#414750] mb-1">{item.label}</p>
                        <p>{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            {/* Score Circle */}
            <div className="flex items-center justify-center">
              <div className="bg-[#eceef1] rounded-3xl p-8 w-full max-w-md aspect-square flex flex-col items-center justify-center relative">
                <svg className="w-64 h-64 transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="42" fill="transparent" stroke="#005394" strokeWidth="8" strokeDasharray="35 65" strokeDashoffset="0" strokeLinecap="round" />
                  <circle cx="50" cy="50" r="42" fill="transparent" stroke="#005394" strokeWidth="8" strokeDasharray="25 75" strokeDashoffset="-36" strokeLinecap="round" opacity="0.7" />
                  <circle cx="50" cy="50" r="42" fill="transparent" stroke="#005394" strokeWidth="8" strokeDasharray="20 80" strokeDashoffset="-62" strokeLinecap="round" opacity="0.5" />
                  <circle cx="50" cy="50" r="42" fill="transparent" stroke="#005394" strokeWidth="8" strokeDasharray="15 85" strokeDashoffset="-83" strokeLinecap="round" opacity="0.3" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <div className="w-28 h-28 bg-white rounded-full shadow-2xl flex flex-col items-center justify-center border-4 border-[#eceef1]">
                    <span className="text-xs uppercase font-bold text-[#414750] opacity-60">Match Score</span>
                    <span className="text-5xl font-[Inter_Tight] font-bold text-[#005394]">94</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Analytics Preview */}
        <section className="py-32 px-8 max-w-7xl mx-auto">
          <h2 className="text-4xl font-[Inter_Tight] font-bold mb-16 text-center">
            Engagement &amp; Scraping Analytics
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 bg-white rounded-3xl p-8 shadow-sm">
              <div className="flex justify-between items-center mb-12">
                <h3 className="text-xl font-bold font-[Inter_Tight]">Opportunity Density Heat Map</h3>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-[#eceef1] rounded-lg text-xs font-bold">Scraped Leads</span>
                  <span className="px-3 py-1 bg-[#eceef1] rounded-lg text-xs font-bold">CRM Matches</span>
                </div>
              </div>
              <div className="h-80 bg-[#eceef1] rounded-2xl relative overflow-hidden flex items-center justify-center">
                <div className="relative flex flex-col items-center gap-2">
                  <div className="w-16 h-16 bg-[#005394] rounded-full animate-pulse opacity-70" />
                  <p className="font-bold text-[#005394]">High Opportunity: Los Angeles Hub</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-3xl p-8 shadow-sm">
              <h3 className="text-xl font-bold font-[Inter_Tight] mb-12">Matching Funnel</h3>
              <div className="space-y-8">
                {[
                  { label: "Discovered (Scraped)", count: "2,481", width: "100%" },
                  { label: "CRM Potential Matches", count: "842", width: "34%" },
                  { label: "Specialist Confirmed", count: "114", width: "5%" },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-bold">{item.label}</span>
                      <span className="text-sm">{item.count}</span>
                    </div>
                    <div className="h-3 bg-[#eceef1] rounded-full overflow-hidden">
                      <div className="h-full bg-[#005394]" style={{ width: item.width }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Partners */}
        <section className="py-24 border-y border-[#eceef1]">
          <div className="px-8 max-w-7xl mx-auto">
            <p className="text-center text-[#414750] font-bold uppercase tracking-widest text-xs mb-12">
              Bridging CRM Data to
            </p>
            <div className="flex flex-wrap justify-center gap-12 md:gap-24 grayscale opacity-60">
              {["CPP", "UCLA", "SDSU", "UC DAVIS", "USC", "PORTLAND STATE"].map((school) => (
                <span key={school} className="text-2xl font-[Inter_Tight] font-extrabold">{school}</span>
              ))}
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="px-8 py-32 max-w-5xl mx-auto text-center">
          <h2 className="text-5xl font-[Inter_Tight] font-bold mb-8">
            Ready to sync your database with the web?
          </h2>
          <p className="text-xl text-[#414750] mb-12 max-w-2xl mx-auto">
            Join the IA West network and transform how your internal specialist database interacts
            with real-world university opportunities.
          </p>
          <Link
            to="/login"
            className="bg-gradient-to-r from-[#005394] to-[#2b6cb0] text-white px-10 py-5 rounded-2xl text-xl font-bold shadow-xl active:scale-95 transition-all inline-block"
          >
            Get Started
          </Link>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-[#eceef1] bg-white">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 px-12 py-16 max-w-7xl mx-auto">
          <div className="col-span-2">
            <span className="text-md font-bold font-[Inter_Tight] mb-4 block">IA SmartMatch</span>
            <p className="text-[#414750] max-w-xs">
              Connecting internal specialist CRM data with real-time scraped academic opportunities.
            </p>
          </div>
          <div className="space-y-4">
            <p className="font-[Inter_Tight] font-semibold">Product</p>
            <ul className="space-y-2 text-[#414750]">
              <li>Specialist CRM</li>
              <li>Scraping Engine</li>
            </ul>
          </div>
          <div className="space-y-4">
            <p className="font-[Inter_Tight] font-semibold">About</p>
            <ul className="space-y-2 text-[#414750]">
              <li>About IA West</li>
              <li>Contact</li>
            </ul>
          </div>
        </div>
        <div className="px-12 py-8 border-t border-[#eceef1] max-w-7xl mx-auto">
          <p className="text-[#414750] text-sm">&copy; 2026 IA West. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
