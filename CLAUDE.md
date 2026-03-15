# Hackathon Agent Harness — CPP AI Hackathon 2026

## Project Context

- **Event:** Cal Poly Pomona AI Hackathon "AI for a Better Future"
- **Date:** April 16, 2026
- **Team Size:** 3-5
- **Categories:** 5 total; team focuses on 1-2
- **Existing Assets:** Working Python/Streamlit prototype (Cat 4), real CSV data (Cat 3)
- **Key Docs:** `HACKATHON_PRD.md` (master strategy), `CTO_REVIEW_OUTPUT.md` (tier rankings), `PRD_SECTION_CAT[1-5].md` (detailed specs)

## Active Category

<!-- Update when team votes on which category to pursue -->
ACTIVE_CATEGORY: TBD
SECONDARY_CATEGORY: TBD

---

## Canonical Development Pipeline

Every feature, idea, or change follows this 8-stage pipeline.
Trivial changes (typos, config tweaks) may skip stages, but substantive work must follow the full flow.

```
1. IDEA      → idea-capture agent
2. FEATURES  → feature-spec agent
3. DOC       → agent-doc-gen agent
4. MEMORY    → (any agent writes to .memory/ automatically)
5. VERIFY    → plan-verifier agent (DIFFERENT session)
6. TEST      → global tdd-guide agent
7. DRIFT     → drift-detector agent
8. COMMIT    → git commit (conventional format)
```

### Stage Gates

| From → To | Gate Condition |
|-----------|---------------|
| IDEA → FEATURES | Idea has a problem statement + at least one proposed approach |
| FEATURES → DOC | Every feature has testable acceptance criteria |
| DOC → MEMORY | Doc references which category it belongs to |
| MEMORY → VERIFY | At least one memory entry exists for this work |
| VERIFY → TEST | plan-verifier verdict is PASS or PASS-WITH-NOTES. If FAIL, return to FEATURES |
| TEST → DRIFT | All tests pass. New code coverage ≥ 80% |
| DRIFT → COMMIT | drift-detector verdict is CLEAN or MINOR-DRIFT. If MAJOR-DRIFT, fix docs first |

### Fast-Track Mode (Final Sprint)

For the final 48 hours, skip DOC/MEMORY/VERIFY/DRIFT when ALL of the following apply:
- Change estimated under 2 hours
- Modifying existing code (not new architecture)
- Team agrees verbally

Compressed path: `IDEA → FEATURES → TEST → COMMIT`

---

## Existing Work — Pre-Credited Stages

All 5 categories already have substantial planning complete. Do not re-do this work.

| Document | Stage | Status | Applies To |
|----------|-------|--------|------------|
| `Category N/PLAN.md` | IDEA + FEATURES (partial) | Done | All 5 |
| `CTO_REVIEW_OUTPUT.md` | VERIFY (of plans) | Done | All 5 |
| `PRD_SECTION_CAT[N].md` | FEATURES (detailed) | Done | All 5 |
| Cat 4 prototype code | TEST + implementation | In-progress | Cat 4 |
| Cat 3 CSV data | Data inputs ready | Available | Cat 3 |

**The pipeline picks up at Stage 3 (DOC) for whichever category the team selects.**

---

## Memory Conventions

All persistent state lives in `.memory/`. This directory is committed to git.

### File Naming
```
.memory/<subdirectory>/YYYY-MM-DD-<slug>.md
```

### Subdirectories

| Directory | What Goes Here |
|-----------|---------------|
| `decisions/` | Architecture choices, tech stack picks, strategy calls |
| `blockers/` | Known obstacles, rate limits, missing credentials |
| `context/` | Session handoff notes, "where I left off" summaries |
| `team/` | Role assignments, availability, who owns what |

### Memory Entry Format
```markdown
# <Title>

**Date:** YYYY-MM-DD
**Category:** Cat 1 | Cat 2 | Cat 3 | Cat 4 | Cat 5 | Cross-cutting
**Author:** <person or agent name>
**Status:** Active | Resolved | Superseded by <link>

## Context
<What prompted this entry>

## Decision / Blocker / Context
<The substance>

## Consequences
<What changes as a result>
```

### INDEX.md
`.memory/INDEX.md` is a flat list of all entries, newest first.
Agents append to INDEX.md when creating a new memory entry.

---

## Category Status Tracking

Each category folder has a `.status.md` tracking pipeline progress.
**Before starting a stage, update it to `in-progress` with your name.**
This prevents duplicate work when teammates are coding simultaneously.

Always run `git pull` before reading `.status.md` to get the latest state.

---

## Agent Interaction Rules

1. **Agents do not call each other.** The orchestrator recommends; a human invokes.
2. **Agents read `.memory/` before starting.** Check for relevant decisions and blockers.
3. **Agents write to `.memory/` when they make decisions.** This creates an audit trail.
4. **Agents update `.status.md` after completing a stage.**
5. **plan-verifier must run in a different session** than the one that created the plan.

---

## Tech Stack Reference

| Component | Tool | Categories |
|-----------|------|------------|
| Frontend | Streamlit | 1, 2, 3, 4 |
| LLM API | OpenAI / OpenRouter | All |
| Data Processing | Pandas + NumPy | 3, 4 |
| Visualization | Plotly + Seaborn + Matplotlib | 1, 3, 4, 5 |
| NLP | spaCy, VADER, scikit-learn LDA | 2, 4 |
| Deployment | Streamlit Community Cloud | All |
| Language | Python 3.10+ | All |

---

## Commit Message Format

```
<type>(cat<N>): <description>

<optional body>
```

**Types:** feat, fix, refactor, docs, test, chore, perf
**Scopes:** cat1, cat2, cat3, cat4, cat5, infra, memory

---

## Hackathon-Specific Priorities

1. **Demo-first:** Every decision should be evaluated by "does this make the 5-minute demo better?"
2. **Speed over perfection:** Ship working prototypes, iterate.
3. **One category deep > five shallow:** Pick 1-2 and polish them.
4. **Ground truth wins:** Any comparison to real data is worth 10x a new feature.
5. **Responsible AI is a feature:** Build it into the UI, not just a doc appendix.

---

## Quick Links

| Resource | What It Answers |
|----------|----------------|
| `AGENTS_QUICK_START.md` | How to use the custom agents |
| `HACKATHON_PRD.md` | Full strategy, pricing, feasibility for all 5 categories |
| `CTO_REVIEW_OUTPUT.md` | Tier rankings + specific recommendations per category |
| `PRD_SECTION_CAT[N].md` | Detailed feature specs per category |
| `Category N/PLAN.md` | Challenge analysis + recommended approach |
| `.memory/INDEX.md` | All past decisions, blockers, context |
| `.claude/agents/*.md` | Agent definitions and instructions |
