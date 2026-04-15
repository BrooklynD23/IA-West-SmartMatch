import { Link } from "react-router";
import { motion, useReducedMotion } from "motion/react";

const introReveal = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] as const },
  viewport: { once: true, amount: 0.35 },
} as const;

const cards = [
  {
    title: "Discover",
    description:
      "Capture opportunity signals from across the West Coast and surface the ones that matter in one clear blue/white workspace.",
  },
  {
    title: "Rank",
    description:
      "Use matching logic, availability, and specialist context to rank the best-fit coordinator actions without visual clutter.",
  },
  {
    title: "Activate",
    description:
      "Route the public surface into a single coordinator login path so the public brand stays simple and focused.",
  },
];

const proofRows = [
  { label: "Discovered opportunities", value: "2,481", width: "100%" },
  { label: "High-confidence matches", value: "842", width: "34%" },
  { label: "Coordinator-ready", value: "114", width: "5%" },
];

const marketSignals = [
  {
    label: "Los Angeles",
    tone: "bg-primary/20 text-primary",
    schools: ["CPP", "UCLA", "USC", "Cal State LA"],
    opportunities: 1124,
    matches: 382,
    strength: "100%",
  },
  {
    label: "San Diego",
    tone: "bg-secondary text-foreground",
    schools: ["SDSU", "UCSD", "USD"],
    opportunities: 847,
    matches: 291,
    strength: "75%",
  },
  {
    label: "Bay Area",
    tone: "bg-muted text-foreground",
    schools: ["UC Davis", "Stanford", "USF", "Portland State"],
    opportunities: 510,
    matches: 169,
    strength: "45%",
  },
];

export function LandingPage() {
  const reduceMotion = useReducedMotion();

  return (
    <div className="public-shell">
      <header className="sticky top-0 z-50 border-b border-border/70 bg-background/85 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary text-sm font-bold text-primary-foreground shadow-lg shadow-primary/20">
              IW
            </span>
            <div className="leading-tight">
              <p className="font-semibold text-foreground">IA West Smart Match</p>
              <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">Coordinator Platform</p>
            </div>
          </Link>

          <Link to="/login" className="public-button-primary">
            Sign In
          </Link>
        </nav>
      </header>

      <main>
        <section
          id="hero"
          className="mx-auto grid max-w-7xl gap-12 px-6 py-16 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:px-8 lg:py-24"
        >
          <motion.div {...introReveal} className="space-y-8">
            <span className="public-pill">IA West Chapter</span>
            <div className="space-y-6">
              <h1 className="max-w-3xl font-[Inter_Tight] text-5xl font-semibold tracking-tight text-foreground md:text-7xl">
                <span className="whitespace-nowrap">Insights Association.</span> See it. Staff it. Secure it.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-muted-foreground md:text-xl">
                The public surface stays focused on one path: discover the brand, understand the
                product story, and sign in to the coordinator workflow.
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <Link to="/login" className="public-button-primary">
                Sign In
              </Link>
              <a href="#proof" className="public-button-secondary">
                See the proof
              </a>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div className="public-panel p-5">
                <p className="text-3xl font-semibold text-primary">2,481</p>
                <p className="mt-1 text-sm text-muted-foreground">opportunities surfaced</p>
              </div>
              <div className="public-panel p-5">
                <p className="text-3xl font-semibold text-primary">842</p>
                <p className="mt-1 text-sm text-muted-foreground">high-fit matches</p>
              </div>
              <div className="public-panel p-5">
                <p className="text-3xl font-semibold text-primary">94%</p>
                <p className="mt-1 text-sm text-muted-foreground">signal confidence</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            {...introReveal}
            transition={{ ...introReveal.transition, delay: 0.08 }}
            className="relative"
          >
            <div className="public-panel relative overflow-hidden p-6 md:p-8">
              <motion.div
                aria-hidden="true"
                className="absolute -right-16 -top-12 h-48 w-48 rounded-full bg-primary/10 blur-3xl"
                animate={
                  reduceMotion
                    ? undefined
                    : { scale: [1, 1.08, 1], opacity: [0.45, 0.7, 0.45] }
                }
                transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
              />
              <motion.div
                aria-hidden="true"
                className="absolute bottom-6 left-6 h-24 w-24 rounded-full bg-secondary/70 blur-2xl"
                animate={reduceMotion ? undefined : { y: [0, -8, 0] }}
                transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
              />

              <div className="relative space-y-6">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="public-pill">Opportunity snapshot</p>
                    <h2 className="mt-4 font-[Inter_Tight] text-2xl font-semibold text-foreground md:text-3xl">
                      UCLA Career Fair 2026
                    </h2>
                    <p className="mt-2 text-sm text-muted-foreground">Luskin Conference Center</p>
                  </div>
                  <span className="rounded-full bg-primary/10 px-3 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-primary">
                    High priority
                  </span>
                </div>

                <div className="grid gap-4 md:grid-cols-[1.2fr_0.8fr]">
                  <div className="rounded-[1.5rem] border border-border/70 bg-background p-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.28em] text-muted-foreground">
                      Specialist focus
                    </p>
                    <div className="mt-4 flex items-center gap-4">
                      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-lg font-semibold text-primary-foreground">
                        TM
                      </div>
                      <div>
                        <p className="font-semibold text-foreground">Travis Miller</p>
                        <p className="text-sm text-muted-foreground">SVP Sales, TechCorp</p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-[1.5rem] border border-border/70 bg-background p-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.28em] text-muted-foreground">
                      Match score
                    </p>
                    <div className="mt-3 flex items-end gap-2">
                      <span className="font-[Inter_Tight] text-5xl font-semibold text-primary">94</span>
                      <span className="pb-1 text-lg font-semibold text-muted-foreground">/100</span>
                    </div>
                    <div className="mt-4 h-2 overflow-hidden rounded-full bg-muted">
                      <div className="h-full w-[94%] rounded-full bg-primary" />
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </motion.div>
        </section>

        <motion.section
          id="story"
          {...introReveal}
          className="mx-auto max-w-7xl px-6 py-8 lg:px-8 lg:py-16"
        >
          <div className="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="space-y-3">
              <p className="public-pill">Product story</p>
              <h2 className="font-[Inter_Tight] text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
                One public journey, one coordinator handoff.
              </h2>
            </div>
            <p className="max-w-2xl text-muted-foreground">
              The public page explains the workflow without exposing dashboard chrome. The login
              path remains the single conversion point.
            </p>
          </div>

          <div className="grid gap-5 lg:grid-cols-3">
            {cards.map((card, index) => (
              <motion.div
                key={card.title}
                className="public-panel p-6"
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.08, ease: [0.16, 1, 0.3, 1] }}
                viewport={{ once: true, amount: 0.4 }}
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                  <span className="font-[Inter_Tight] text-lg font-semibold">{index + 1}</span>
                </div>
                <h3 className="mt-5 font-[Inter_Tight] text-2xl font-semibold text-foreground">{card.title}</h3>
                <p className="mt-3 leading-7 text-muted-foreground">{card.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        <motion.section
          id="proof"
          {...introReveal}
          className="mx-auto max-w-7xl px-6 py-8 lg:px-8 lg:py-16"
        >
          <div className="mb-10 space-y-3">
            <p className="public-pill">Analytics proof</p>
            <h2 className="font-[Inter_Tight] text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
              Brand clarity backed by operational signal.
            </h2>
          </div>

          <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="public-panel p-6 md:p-8">
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <h3 className="font-[Inter_Tight] text-2xl font-semibold text-foreground">
                    Opportunity density
                  </h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    A West Coast view of where the strongest engagements cluster.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {marketSignals.flatMap((s) => s.schools).filter((v, i, arr) => arr.indexOf(v) === i).map((school) => (
                    <span
                      key={school}
                      className="rounded-full border border-border/70 bg-background px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground"
                    >
                      {school}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-6 grid gap-4 rounded-[1.5rem] border border-border/70 bg-surface-container-low p-5 md:grid-cols-3">
                {marketSignals.map((signal, index) => (
                  <div
                    key={signal.label}
                    className="group rounded-2xl border border-border/70 bg-background p-4 transition-shadow hover:shadow-md"
                  >
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-foreground">{signal.label}</p>
                      <span className="text-xs font-semibold text-primary">#{index + 1}</span>
                    </div>
                    {/* Opportunity strength bar */}
                    <div className="mt-3">
                      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary transition-all duration-700"
                          style={{ width: signal.strength }}
                        />
                      </div>
                      <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                        <span>{signal.opportunities.toLocaleString()} opps</span>
                        <span>{signal.matches} matches</span>
                      </div>
                    </div>
                    {/* School names */}
                    <div className="mt-3 flex flex-wrap gap-1">
                      {signal.schools.map((school) => (
                        <span
                          key={school}
                          className="rounded-full bg-primary/8 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-primary"
                        >
                          {school}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="public-panel p-6 md:p-8">
              <h3 className="font-[Inter_Tight] text-2xl font-semibold text-foreground">Matching funnel</h3>
              <div className="mt-6 space-y-6">
                {proofRows.map((row) => (
                  <div key={row.label}>
                    <div className="flex items-center justify-between gap-4">
                      <p className="text-sm font-medium text-foreground">{row.label}</p>
                      <p className="text-sm font-semibold text-primary">{row.value}</p>
                    </div>
                    <div className="mt-3 h-3 overflow-hidden rounded-full bg-muted">
                      <div className="h-full rounded-full bg-primary" style={{ width: row.width }} />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 rounded-[1.5rem] border border-border/70 bg-background p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-muted-foreground">
                  Public CTA
                </p>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">
                  Every public interaction ends in the same place: the coordinator login flow.
                </p>
                <Link to="/login" className="public-button-primary mt-5">
                  Sign In
                </Link>
              </div>
            </div>
          </div>
        </motion.section>

        <motion.section
          id="login"
          {...introReveal}
          className="mx-auto max-w-5xl px-6 py-8 pb-20 lg:px-8 lg:py-16"
        >
          <div className="public-panel overflow-hidden p-8 md:p-10">
            <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
              <div className="space-y-4">
                <p className="public-pill">Ready for coordinators</p>
                <h2 className="font-[Inter_Tight] text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
                  Sign in to move from public brand to working dashboard.
                </h2>
                <p className="max-w-2xl text-muted-foreground">
                  The landing page stays clean and informative. The login page carries the same
                  blue/white system forward and hands coordinators directly into the app.
                </p>
              </div>

              <Link to="/login" className="public-button-primary justify-self-start lg:justify-self-end">
                Sign In
              </Link>
            </div>
          </div>
        </motion.section>
      </main>

      <footer className="border-t border-border/70 bg-background/80">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-6 py-8 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between lg:px-8">
          <p className="font-medium text-foreground">IA West Smart Match</p>
          <p>Blue/white public surface for the coordinator experience.</p>
        </div>
      </footer>
    </div>
  );
}
