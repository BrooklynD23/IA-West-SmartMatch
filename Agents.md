##

## Workflow Orchestration

### 1. Plan Mode Default

- Enter plan mode for any non-trivial task (3+ steps or architectural decisions).
- If something goes sideways, stop and re-plan immediately.
- Use plan mode for verification steps, not just building.
- Write detailed specs upfront to reduce ambiguity.

### 2. Subagent Strategy

- Use subagents liberally to keep the main context window clean.
- Offload research, exploration, and parallel analysis to subagents.
- For complex problems, throw more compute at it via subagents.
- One task per subagent for focused execution.

### 3. Self-Improvement Loop

- After any correction from the user, update `tasks/lessons.md` with the pattern.
- Write rules for yourself that prevent the same mistake.
- Ruthlessly iterate on these lessons until the mistake rate drops.
- Review lessons at session start for the relevant project.

### 4. Verification Before Done

- Never mark a task complete without proving it works.
- Diff behavior between main and your changes when relevant.
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, and demonstrate correctness.

### 5. Demand Elegance

- For non-trivial changes, pause and ask: "Is there a more elegant way?"
- If a fix feels hacky, implement the elegant solution instead.
- Skip this for simple, obvious fixes. Do not over-engineer.
- Challenge your own work before presenting it.

### 6. Autonomous Bug Fixing

- When given a bug report, just fix it. Do not ask for hand-holding.
- Point at logs, errors, and failing tests, then resolve them.
- Keep the user out of unnecessary context switching.
- Fix failing CI tests without needing to be told how.

## Task Management

1. Plan first: write the plan to `tasks/todo.md` with checkable items.
2. Verify the plan: check in before starting implementation.
3. Track progress: mark items complete as you go.
4. Explain changes: provide a high-level summary at each step.
5. Document results: add a review section to `tasks/todo.md`.
6. Capture lessons: update `tasks/lessons.md` after corrections.

## Core Principles

- Simplicity first: make every change as simple as possible. Impact minimal code.
- No laziness: find root causes. No temporary fixes. Senior developer standards.
- Minimal impact: only touch what's necessary. No side effects with new bugs.
