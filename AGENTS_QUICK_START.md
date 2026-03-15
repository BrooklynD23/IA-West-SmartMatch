# Agent Quick Start Guide

**For: Team members using Claude Code to build hackathon submissions**

This guide explains the 6 custom agents and how to use them. You don't need to understand how they work internally — just know when to call them and what to expect.

---

## The Pipeline (TL;DR)

Every feature goes through these stages:

```
1. IDEA        💡 Capture the idea
2. FEATURES    📋 List features & acceptance criteria
3. DOC         📚 Generate implementation docs
4. MEMORY      🧠 Store decisions (automatic)
5. VERIFY      ✅ Someone else checks the plan
6. TEST        🧪 Write tests & implement (TDD)
7. DRIFT       🔍 Check docs still match code
8. COMMIT      ✨ Git commit
```

**Stages 1-3** = Planning. **Stages 5-8** = Implementation & verification.

---

## How to Use the Agents

### Stage 1: Capture an Idea ✨

**Agent:** `idea-capture`

**When to use:**
- You have a new feature idea
- The team brainstormed something
- You want to pivot or add a new direction

**How to invoke:**
```
/agent idea-capture
```

Then tell it:
- What's the problem you're solving?
- What's your proposed approach?
- How does it improve the demo?

**What you get:**
A structured idea document in `Category N/ideas/YYYY-MM-DD-slug.md` with:
- Problem statement
- Proposed approach
- Demo impact
- Effort estimate (low/medium/high)
- Open questions

**Example:**
> "I want to add a phishing email analyzer to Cat 2 that shows confidence scores for each classification."

The agent turns this into a structured idea with problem, approach, and demo impact.

---

### Stage 2: Turn Idea into Features 📋

**Agent:** `feature-spec`

**When to use:**
- After the idea-capture agent produced an idea document
- You're ready to list what features to build

**How to invoke:**
```
/agent feature-spec
```

Then tell it the path to the idea document (e.g., `Category 2/ideas/2026-04-03-confidence-scores.md`).

**What you get:**
A feature spec in `Category N/features/YYYY-MM-DD-slug.md` with:
- **Features** (broken into small, independent pieces)
- **Acceptance criteria** for each (GIVEN/WHEN/THEN format — these are testable!)
- **Priority** (P0/P1/P2)
- **Demo-visible flag** (does it show up in the 5-min demo?)
- **Estimated hours** per feature
- **Implementation order** (what depends on what)
- **Risks** and mitigations

**Example output:**
```
Feature 1: Confidence Score Display
- Priority: P0
- Demo-visible: Yes
- Estimated: 3 hours
- Acceptance Criteria:
  * GIVEN a phishing email, WHEN classified, THEN show a % confidence (0-100)
  * GIVEN a legitimate email, WHEN shown confidence, THEN display in green
```

---

### Stage 3: Generate Agent Docs 📚

**Agent:** `agent-doc-gen`

**When to use:**
- After feature-spec produced a feature spec
- You're ready to hand off to a developer/implementer

**How to invoke:**
```
/agent agent-doc-gen
```

Then tell it which category and feature spec you're documenting (e.g., `Category 2`, or point to the feature spec file).

**What you get:**
Three documents in `Category N/docs/`:
1. **Implementation Brief** — "Here's what to build, here's the file map, here's the data flow"
2. **Test Spec** — "Here's what tests to write, here's test data to use"
3. **Review Checklist** — "Here's what the code reviewer will look for"

These docs are **agent-readable** — the downstream agents (implementers, testers, reviewers) can read them without needing to ask questions.

**Example:**
> Implementation Brief explains: "Create `src/classifier.py` with a `classify(email) → (label, confidence)` function. Use the PhishTank API. Handle rate limits by caching."

---

### Stage 5: Get a Second Opinion ✅

**Agent:** `plan-verifier`

**When to use:**
- After agent-doc-gen produced implementation docs
- Before you start writing code
- **IMPORTANT:** Invoke in a **different Claude Code session** than the one that created the plan

**How to invoke:**
Open a fresh Claude Code window (new session), then:
```
/agent plan-verifier
```

Then tell it which feature spec or implementation brief to verify.

**What the agent checks:**
- ✅ Can this be built in the estimated time?
- ✅ Are all dependencies available (APIs, libraries, free tier)?
- ✅ Does it conflict with any prior decisions in `.memory/`?
- ✅ Is the demo impact clear?
- ✅ Are all acceptance criteria actually testable?
- ✅ Does it align with CTO_REVIEW_OUTPUT.md recommendations?

**What you get:**
A verification report with one of three verdicts:
- **PASS** — Go build it!
- **PASS-WITH-NOTES** — Build it, but watch out for X, Y, Z
- **FAIL** — Stop. These blocking issues must be fixed first.

**Why a different session?**
Because the fresh session has no bias toward the plan it didn't create. It's a genuine second pair of eyes.

---

### Stage 6: Write Tests & Implement 🧪

**Agent:** Global `tdd-guide` agent

**When to use:**
- After plan-verifier gave a PASS verdict
- You're ready to write code

**How to invoke:**
```
/agent tdd-guide
```

Tell it to read the test spec (from stage 3) and implement the features.

**What it does:**
1. Reads the test spec
2. Writes tests first (RED)
3. Implements minimal code to pass tests (GREEN)
4. Refactors (IMPROVE)
5. Verifies 80%+ test coverage

**You provide:**
- Test spec path (generated in stage 3)
- Link to implementation brief
- Existing code (if any — Cat 4 has a prototype)

---

### Stage 7: Check for Doc Drift 🔍

**Agent:** `drift-detector`

**When to use:**
- After tests pass and code is implemented
- Before you commit
- To verify docs still match what you built

**How to invoke:**
```
/agent drift-detector
```

Tell it which category to check.

**What it checks:**
- File existence: "Does `src/classifier.py` actually exist?"
- Function signatures: "Does `classify(email)` have the right parameters?"
- Dependencies: "Is `plotly` in requirements.txt?"
- Status tracking: "If docs say FEATURES=done, is there actually a feature spec file?"

**What you get:**
A drift report with one of three verdicts:
- **CLEAN** — All good! Ready to commit.
- **MINOR-DRIFT** — Small stuff (typo in version number). Can fix later.
- **MAJOR-DRIFT** — Real problem (docs say a file exists but it doesn't). Fix before committing.

---

### Stage Meta: Check Overall Status 📊

**Agent:** `hackathon-orchestrator`

**When to use:**
- You sit down to work and want to know "What's next?"
- You want a summary of where the category is
- You want the agent to recommend which agent to invoke

**How to invoke:**
```
/agent hackathon-orchestrator
```

**What you get:**
A status report like this:

```
Category 2 — ISACA Cyber Safety Coach

| Stage    | Status      |
|----------|-------------|
| IDEA     | done        |
| FEATURES | done        |
| DOC      | in-progress |
| MEMORY   | done        |
| VERIFY   | pending     |
| TEST     | pending     |
| DRIFT    | pending     |
| COMMIT   | pending     |

Next step: Invoke /agent agent-doc-gen to complete the DOC stage.
Reason: Feature spec is ready. Implementation docs will unlock the VERIFY stage.
```

Use this report to figure out what to do next. The agent recommends which agent to invoke.

---

## Workflow Example (End-to-End)

**Scenario:** You have a new idea for Cat 2 (PhishGuard AI).

### Day 1: Planning

```
You: I want to add a feature that explains WHY we classified an email as phishing.

You: /agent idea-capture
idea-capture: "Captured your idea in Category 2/ideas/2026-04-05-phishing-explanations.md"

You: /agent feature-spec
feature-spec: "Created feature spec in Category 2/features/2026-04-05-phishing-explanations.md
  - Feature 1: Explanation Engine (P0, 4 hours)
  - Feature 2: Confidence Score Explanation (P1, 2 hours)
  - Total: 6 hours"

You: /agent agent-doc-gen
agent-doc-gen: "Generated docs in Category 2/docs/
  - Implementation Brief
  - Test Spec
  - Review Checklist"

You: /agent hackathon-orchestrator
orchestrator: "Next: Have someone else verify this plan.
  Invoke /agent plan-verifier in a fresh session."
```

### Day 2: Verification (Different person)

```
Alex (new session): /agent plan-verifier
plan-verifier: "Read the feature spec and implementation brief.
  Verdict: PASS-WITH-NOTES
  Note: PhishTank API rate limit is 100 req/15min. Consider caching."
```

### Day 2: Implementation

```
You: /agent tdd-guide
tdd-guide: "Read test spec. Writing tests for explanation_engine.py...
  [writes 12 tests, all RED]
  Implementing classify_with_explanation()...
  [all tests now GREEN]
  Refactoring for readability...
  Coverage: 82%"

You: /agent drift-detector
drift-detector: "Checking docs vs. code...
  CLEAN. All docs match implementation."

You: git add . && git commit -m "feat(cat2): add phishing explanation engine"
```

Done! ✨

---

## Quick Reference: When to Use Each Agent

| Situation | Agent |
|-----------|-------|
| "I have an idea I want to capture" | **idea-capture** |
| "I have an idea document, turn it into a feature list" | **feature-spec** |
| "I have a feature spec, generate implementation docs" | **agent-doc-gen** |
| "I have a plan, ask someone else to review it" | **plan-verifier** (diff session) |
| "I have code, make sure docs still match" | **drift-detector** |
| "I don't know what to do next" | **hackathon-orchestrator** |
| "I'm ready to code" | **tdd-guide** (global) |
| "I'm ready to commit" | git commit |

---

## Common Questions

### Q: Can I skip stages?

**Short answer:** Only skip for tiny changes (typos, config tweaks). Everything else goes through the full pipeline.

**Fast-track mode** (final week before hackathon): You can go IDEA → FEATURES → TEST → COMMIT, skipping DOC/VERIFY/DRIFT if the change is under 2 hours and modifies existing code only.

### Q: Why do I need a different session for plan-verifier?

Because the person who created the plan will naturally defend it. A fresh session (different person, new window) has no bias and will catch real issues.

### Q: What if the verifier says FAIL?

Go back to the feature-spec or idea-capture agent. Fix the blocking issues. Re-run the verifier. It should then PASS.

### Q: Do I really need to run drift-detector?

Yes, if you've modified any docs during implementation. It's fast (2 min) and catches drift that could cause confusion for teammates.

### Q: What if two people work on the same category at the same time?

Use `.status.md` to coordinate. Before you start a stage, update `.status.md` to `in-progress` with your name. Then run `git pull` to stay in sync. Merge conflicts are rare because files are small.

### Q: Do agents write to memory automatically?

Yes. After each stage, the agent writes a memory entry in `.memory/context/` or `.memory/decisions/`. You can ignore this — it's for other agents and teammates to read.

---

## Pro Tips

1. **Read CTO_REVIEW_OUTPUT.md before planning** — It ranks categories by win probability and gives specific recommendations for each.

2. **Check `.memory/blockers/` before starting** — Maybe someone already discovered an API rate limit or blocker that affects your plan.

3. **Use the implementation brief to hand off to a teammate** — If person A plans and person B codes, person B reads the implementation brief. No meetings needed.

4. **The feature spec is your test spec** — Acceptance criteria in the feature spec become your tests. If it says "GIVEN X, WHEN Y, THEN Z", write a test for that.

5. **Commit often** — The hackathon is a race. Commit every 1-2 features, not at the end.

6. **Use the orchestrator as your daily standup** — Every morning, run `/agent hackathon-orchestrator` to see what's done and what's next.

---

## Getting Help

- **"How do I use an agent?"** → This guide (you're reading it!)
- **"What's the full pipeline?"** → See `CLAUDE.md`
- **"What are the agent specs?"** → See `.claude/agents/*.md`
- **"What are the decisions the team has made?"** → See `.memory/`
- **"What's the CTO's verdict on this idea?"** → See `CTO_REVIEW_OUTPUT.md`
- **"What features does this category already have?"** → See `PRD_SECTION_CAT[N].md`

---

**Happy building! 🚀**
