# CPP AI Hackathon 2026 — AI for a Better Future

**Event:** Cal Poly Pomona AI Hackathon &nbsp;|&nbsp; **Date:** April 16, 2026 &nbsp;|&nbsp; **Team Size:** 3–5

This repo contains all planning, source code, and agent tooling for the team's hackathon submission. Five challenge tracks have been fully researched and CTO-reviewed. The team has not yet voted on which category to pursue — this repo is pre-staged and ready for whichever is chosen.

---

## Challenge Categories

| # | Track | Sponsor | Tier | CTO Verdict |
|---|-------|---------|------|-------------|
| [1](./Category%201%20-%20Avanade%20AI%20Wellbeing/) | AI Wellbeing — *BalanceIQ* | Avanade | 3 | Approved w/ revisions |
| [2](./Category%202%20-%20ISACA%20Cyber%20Safety%20Coach/) | Cyber Safety Coach — *PhishGuard AI* | ISACA | **1** | Approved ✓ |
| [3](./Category%203%20-%20IA%20West%20Smart%20Match%20CRM/) | Smart Match CRM — *IA SmartMatch* | IA West | **1** | Approved w/ revisions |
| [4](./Category%204%20-%20Aytm%20x%20Neo%20Smart%20Living/) | Smart Living Research — *Simulated MR* | Aytm × Neo | 2 | Approved w/ revisions |
| [5](./Category%205%20-%20Avanade%20Creative%20SDG/) | Creative SDG — *CropSense AI* | Avanade | 2 | Approved w/ revisions |

> **Tier 1** = highest win probability. See [`CTO_REVIEW_OUTPUT.md`](./CTO_REVIEW_OUTPUT.md) for full rankings and per-category notes.

**Active category:** Update `CLAUDE.md` → `ACTIVE_CATEGORY` once the team votes.

---

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url>
cd HackathonForBetterFuture2026

# 2. Set up API keys
cp .env.example .env
# Edit .env — minimum: fill in OPENAI_API_KEY

# 3. Set up chosen category (replace N with 1–5)
make setup CAT=N

# 4. Activate the venv and run
cd "Category N - <Name>"
source .venv/bin/activate      # Windows: .venv\Scripts\activate
streamlit run src/app.py

# Or, from the repo root:
make run CAT=N
```

---

## Repo Structure

```
HackathonForBetterFuture2026/
│
├── Category 1–5/              # One folder per challenge track
│   ├── src/                   # Application source code
│   ├── tests/                 # pytest test suite
│   ├── docs/                  # Category-specific docs
│   ├── data/                  # CSVs, assets (never commit raw secrets)
│   ├── PLAN.md                # Challenge analysis + recommended approach
│   ├── .status.md             # Pipeline stage tracker (update before starting)
│   ├── requirements.txt       # Python deps (extends requirements-common.txt)
│   └── .env.example           # Required env vars for this category
│
├── Categories list/           # Raw source materials (PDFs, CSVs, prototype)
├── shared/                    # Reusable utilities across categories
│   └── llm.py                 # LLM client wrapper (OpenAI / OpenRouter)
├── docs/                      # Shared team documentation
│   ├── setup.md               # Dev environment setup guide
│   ├── team.md                # Team roles and ownership
│   └── architecture.md        # Architecture principles + data flow
│
├── .claude/agents/            # Claude sub-agent definitions
├── .memory/                   # Persistent team memory (decisions, blockers, context)
│
├── requirements-common.txt    # Shared Python dependencies
├── .env.example               # Root env var template
├── Makefile                   # make setup/run/test/clean CAT=N
│
├── CLAUDE.md                  # Agent harness — pipeline, conventions, rules
├── AGENTS_QUICK_START.md      # How to invoke each Claude sub-agent
├── HACKATHON_PRD.md           # Master strategy + feasibility for all 5 categories
├── CTO_REVIEW_OUTPUT.md       # Tier rankings + CTO notes per category
└── PRD_SECTION_CAT[1-5].md   # Detailed feature specs per category
```

---

## Development Pipeline

Every feature follows this 8-stage pipeline. All 5 categories are pre-credited through **Stage 2**. Development picks up at **Stage 3** for whichever category is chosen.

```
IDEA → FEATURES → DOC → MEMORY → VERIFY → TEST → DRIFT → COMMIT
  ✓         ✓       ←── start here ───────────────────────────→
```

| Stage | Agent | Gate to advance |
|-------|-------|-----------------|
| 1 IDEA | `idea-capture` | Has problem statement + proposed approach |
| 2 FEATURES | `feature-spec` | Every feature has testable acceptance criteria |
| 3 DOC | `agent-doc-gen` | Doc references the category it belongs to |
| 4 MEMORY | _(auto)_ | At least one `.memory/` entry exists for this work |
| 5 VERIFY | `plan-verifier` | Verdict is PASS or PASS-WITH-NOTES |
| 6 TEST | `tdd-guide` | All tests pass, coverage ≥ 80% |
| 7 DRIFT | `drift-detector` | Verdict is CLEAN or MINOR-DRIFT |
| 8 COMMIT | `git commit` | Conventional format: `feat(cat3): ...` |

**Fast-Track (final 48 hrs):** `IDEA → FEATURES → TEST → COMMIT` — skip middle stages when the change is < 2 hrs and modifies existing code.

---

## Claude Sub-Agents

Six custom agents live in `.claude/agents/` and slot into the pipeline above. See [`AGENTS_QUICK_START.md`](./AGENTS_QUICK_START.md) for full usage.

| Agent | When to use |
|-------|-------------|
| `hackathon-orchestrator` | Session start — routes work to the right agent |
| `idea-capture` | Stage 1: logging a new idea or problem statement |
| `feature-spec` | Stage 2: turning ideas into scoped, testable features |
| `agent-doc-gen` | Stage 3: generating docs from existing feature specs |
| `plan-verifier` | Stage 5: independent audit of a plan (different session) |
| `drift-detector` | Stage 7: checking code vs. docs for misalignment |

---

## Tech Stack

| Component | Tool | Used in |
|-----------|------|---------|
| Frontend | Streamlit | Cat 1, 2, 3, 4 |
| LLM API | OpenAI / OpenRouter | All |
| Data Processing | Pandas + NumPy | Cat 3, 4 |
| Visualization | Plotly + Seaborn + Matplotlib | Cat 1, 3, 4, 5 |
| NLP | spaCy, VADER, scikit-learn | Cat 2, 4 |
| Deployment | Streamlit Community Cloud | All |
| Language | Python 3.10+ | All |

---

## Key Documents

| Document | What it answers |
|----------|----------------|
| [`CLAUDE.md`](./CLAUDE.md) | Full pipeline rules, agent conventions, memory format |
| [`AGENTS_QUICK_START.md`](./AGENTS_QUICK_START.md) | How to invoke each sub-agent |
| [`HACKATHON_PRD.md`](./HACKATHON_PRD.md) | Full strategy, feasibility, and scoring for all 5 tracks |
| [`CTO_REVIEW_OUTPUT.md`](./CTO_REVIEW_OUTPUT.md) | Tier rankings + specific CTO recommendations |
| [`PRD_SECTION_CAT[N].md`](./PRD_SECTION_CAT1.md) | Detailed feature specs per category |
| [`docs/setup.md`](./docs/setup.md) | Dev environment setup (venv, API keys, Streamlit) |
| [`docs/team.md`](./docs/team.md) | Team roles and ownership assignments |
| [`docs/architecture.md`](./docs/architecture.md) | Architecture principles and data flow |
| [`.memory/INDEX.md`](./.memory/INDEX.md) | All past decisions, blockers, and session context |

---

## Hackathon Priorities

1. **Demo-first** — every decision should be evaluated by "does this make the 5-minute demo better?"
2. **One category deep > five shallow** — pick 1–2 and polish them
3. **Ground truth wins** — any comparison against real data is worth 10× a new feature
4. **Responsible AI is a feature** — build it into the UI, not just a doc appendix
5. **Speed over perfection** — ship a working prototype, iterate fast
