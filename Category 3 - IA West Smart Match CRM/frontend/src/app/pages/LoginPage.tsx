import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";
import { motion } from "motion/react";

const panelReveal = {
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.65, ease: [0.16, 1, 0.3, 1] },
};

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleCoordinatorLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    navigate("/dashboard");
  }

  return (
    <div className="public-shell">
      <header className="border-b border-border/70 bg-background/85 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary text-sm font-bold text-primary-foreground shadow-lg shadow-primary/20">
              IW
            </span>
            <div className="leading-tight">
              <p className="font-semibold text-foreground">IA West Smart Match</p>
              <p className="text-xs uppercase tracking-[0.28em] text-muted-foreground">Coordinator login</p>
            </div>
          </Link>
          <Link to="/" className="text-sm font-medium text-muted-foreground transition hover:text-primary">
            Back to home
          </Link>
        </nav>
      </header>

      <main className="mx-auto flex max-w-7xl items-center px-6 py-12 lg:px-8 lg:py-20">
        <div className="grid w-full gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
          <motion.div {...panelReveal} className="space-y-6">
            <span className="public-pill">Public entry</span>
            <div className="space-y-4">
              <h1 className="font-[Inter_Tight] text-5xl font-semibold tracking-tight text-foreground md:text-6xl">
                Sign in to the coordinator workspace.
              </h1>
              <p className="max-w-xl text-lg leading-8 text-muted-foreground">
                The brand stays blue, bright, and minimal while coordinators move directly into the
                operational dashboard.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div className="public-panel p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted-foreground">
                  Access
                </p>
                <p className="mt-3 text-2xl font-semibold text-primary">Coordinator</p>
              </div>
              <div className="public-panel p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted-foreground">
                  Flow
                </p>
                <p className="mt-3 text-2xl font-semibold text-primary">Demo login</p>
              </div>
              <div className="public-panel p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted-foreground">
                  Brand
                </p>
                <p className="mt-3 text-2xl font-semibold text-primary">Blue / white</p>
              </div>
            </div>
          </motion.div>

          <motion.section {...panelReveal} transition={{ ...panelReveal.transition, delay: 0.08 }}>
            <div className="public-panel overflow-hidden">
              <div className="border-b border-border/70 px-6 py-5 md:px-8">
                <p className="public-pill">Coordinator Access</p>
                <h2 className="mt-4 font-[Inter_Tight] text-3xl font-semibold text-foreground">
                  Welcome back.
                </h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  Any credentials will open the demo coordinator experience.
                </p>
              </div>

              <div className="grid gap-0 border-b border-border/70 lg:grid-cols-1">
                <div className="px-6 py-6 md:px-8">
                  <form onSubmit={handleCoordinatorLogin} className="space-y-4">
                    <div>
                      <label className="mb-1.5 block text-sm font-medium text-muted-foreground" htmlFor="coordinator-email">
                        Email
                      </label>
                      <input
                        id="coordinator-email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        placeholder="coordinator@iawest.org"
                        className="w-full rounded-2xl border border-border/70 bg-surface-container-low px-4 py-3 text-foreground outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                      />
                    </div>

                    <div>
                      <label className="mb-1.5 block text-sm font-medium text-muted-foreground" htmlFor="coordinator-password">
                        Password
                      </label>
                      <input
                        id="coordinator-password"
                        type="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        placeholder="Enter password"
                        className="w-full rounded-2xl border border-border/70 bg-surface-container-low px-4 py-3 text-foreground outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                      />
                    </div>

                    <button type="submit" className="public-button-primary w-full">
                      Sign In as Coordinator
                    </button>
                  </form>
                </div>
              </div>

              <div className="bg-surface-container-low px-6 py-6 md:px-8">
                <div className="flex flex-wrap items-center gap-3">
                  <p className="font-[Inter_Tight] text-xl font-semibold text-foreground">Volunteer Access</p>
                  <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-primary">
                    Coming soon
                  </span>
                </div>
                <p className="mt-3 max-w-2xl text-sm leading-7 text-muted-foreground">
                  Volunteer login will eventually use LinkedIn integration for profile enrichment.
                  For now, coordinators own the public sign-in flow.
                </p>
                <button
                  type="button"
                  disabled
                  className="mt-5 flex w-full cursor-not-allowed items-center justify-center gap-3 rounded-2xl border border-border/70 bg-white px-4 py-3 font-semibold text-muted-foreground opacity-60"
                >
                  <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                  </svg>
                  Sign In with LinkedIn
                </button>
              </div>
            </div>
          </motion.section>
        </div>
      </main>
    </div>
  );
}
