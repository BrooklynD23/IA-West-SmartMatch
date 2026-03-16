# Hackathon Agent Harness — CPP AI Hackathon 2026

**Event:** Cal Poly Pomona AI Hackathon "AI for a Better Future" · **Date:** April 16, 2026 · **Team:** 3-5

<!-- Update when team votes -->
ACTIVE_CATEGORY: TBD
SECONDARY_CATEGORY: TBD

---

## Pipeline (8 stages)

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

**Fast-track** (final 48h, <2h change, existing code, team agrees): `IDEA → FEATURES → TEST → COMMIT`

For stage gates and pre-credited work → [`.claude/docs/pipeline.md`](.claude/docs/pipeline.md)

---

## Agent Rules

1. Agents do not call each other — orchestrator recommends, human invokes.
2. Agents read `.memory/` before starting.
3. Agents write to `.memory/` when they make decisions.
4. Agents update `.status.md` after completing a stage.
5. `plan-verifier` must run in a **different session** than the one that created the plan.

---

## Commits

```
<type>(cat<N>): <description>
```
Types: `feat` `fix` `refactor` `docs` `test` `chore` `perf`
Scopes: `cat1` `cat2` `cat3` `cat4` `cat5` `infra` `memory`

---

## Priorities

1. **Demo-first** — does this make the 5-min demo better?
2. **Speed over perfection** — ship prototypes, iterate.
3. **One category deep > five shallow** — pick 1-2 and polish.
4. **Ground truth wins** — real data beats a new feature.
5. **Responsible AI is a feature** — build it into the UI.

---

## Reference Index

| When you need to… | Read |
|---|---|
| Understand stage gates / pre-credited work | [`.claude/docs/pipeline.md`](.claude/docs/pipeline.md) |
| Write or find a memory entry | [`.claude/docs/memory.md`](.claude/docs/memory.md) |
| Check the tech stack | [`.claude/docs/tech-stack.md`](.claude/docs/tech-stack.md) |
| Use the custom agents | [`AGENTS_QUICK_START.md`](AGENTS_QUICK_START.md) |
| Read full strategy & feasibility | [`HACKATHON_PRD.md`](HACKATHON_PRD.md) |
| See tier rankings per category | [`CTO_REVIEW_OUTPUT.md`](CTO_REVIEW_OUTPUT.md) |
| Get detailed feature specs | `PRD_SECTION_CAT[N].md` |
| See category challenge analysis | `Category N/PLAN.md` |
| Review past decisions & blockers | [`.memory/INDEX.md`](.memory/INDEX.md) |
| Read agent definitions | `.claude/agents/*.md` |
