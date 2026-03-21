# Roadmap: Category 3 SmartMatch Sprint 5 Closeout

## Overview

This roadmap closes Sprint 5 for the existing Category 3 SmartMatch app on `sprint5-cat3`. It follows the requested closeout flow: first repair and harden the live demo path, then reconcile docs and governance from one live verification baseline, then run `$ecc-code-review`, remediate accepted findings, and record explicit closure evidence without introducing net-new product scope.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Runtime Fixes and Clean Outputs** - Restore the closeout-critical demo path and isolate generated runtime artifacts.
- [x] **Phase 2: Documentation and Governance Reconciliation** - Refresh Category 3 closeout docs and mirrors from one live verification baseline.
- [x] **Phase 3: Adversarial Audit and Sprint Closure** - Run `$ecc-code-review`, remediate accepted findings, verify the final state, and close Sprint 5.

## Phase Details

### Phase 1: Runtime Fixes and Clean Outputs
**Goal**: The operator can run the intended discovery-to-match demo flow from stable project-root configuration without generated rehearsal outputs polluting source-controlled diffs.
**Depends on**: Nothing (first phase)
**Requirements**: FLOW-01, FLOW-02, DEMO-01, PATH-01, OPS-01
**Parallelization**: After the runtime handoff contract is fixed, regression coverage work and artifact-isolation work can run in parallel subagents.
**Success Criteria** (what must be TRUE):
  1. Operator can add a discovered event to the active match pool and see it in the Matches tab during the same Streamlit session.
  2. Automated regression coverage fails when the discovery-to-matching session-state handoff breaks.
  3. Operator can exercise the core matching flow in Demo Mode or cache-only mode on a clean checkout without requiring live Gemini calls.
  4. Running the app from the repo root or the Category 3 directory writes feedback and generated artifacts to configured project-root locations.
  5. Rehearsal and runtime-generated files are ignored or isolated so they do not appear as product-source changes during Sprint 5 work.
**Plans**: 3 plans

Plans:
- [x] 01-01: Repair the discovery-to-matching handoff and project-root path resolution in the existing runtime.
- [x] 01-02: Add targeted regression coverage for the handoff and clean-checkout demo-mode or cache-only flow.
- [x] 01-03: Isolate or ignore generated runtime outputs and verify that closeout rehearsal does not dirty source-controlled paths.

### Phase 2: Documentation and Governance Reconciliation
**Goal**: Category 3 closeout docs, status surfaces, and governance mirrors report one current verification baseline and one truthful set of remaining manual steps.
**Depends on**: Phase 1
**Requirements**: GOV-01, DOC-01
**Parallelization**: Once the live verification baseline is established, Category 3 doc refreshes and governance-mirror reconciliation can run in parallel subagents.
**Success Criteria** (what must be TRUE):
  1. Category 3 status docs, sprint docs, and the task board all report the same current verification baseline for Sprint 5 closeout.
  2. Operators can read the closeout docs and see the real remaining manual steps, demo readiness, and preflight expectations without stale or contradictory claims.
  3. Governance-facing mirrors point back to one live source of truth for closeout evidence instead of maintaining conflicting copies.
**Plans**: 2 plans

Plans:
- [x] 02-01: Reconcile the canonical verification baseline across Category 3 status, sprint, and task-board documents.
- [x] 02-02: Refresh closeout guidance and governance mirrors so manual steps, readiness notes, and ownership are current.

### Phase 3: Adversarial Audit and Sprint Closure
**Goal**: Sprint 5 changes survive adversarial review, accepted findings are resolved or explicitly documented, and closure evidence is preserved on `sprint5-cat3`.
**Depends on**: Phase 2
**Requirements**: REV-01, REV-02
**Parallelization**: After review triage, independent accepted findings can be remediated in parallel subagents before one final verification and closure pass.
**Success Criteria** (what must be TRUE):
  1. Sprint 5 changes have an `$ecc-code-review` report that records severity, locations, and suggested fixes for the branch delta.
  2. Every accepted review finding is fixed or explicitly documented before the sprint is closed.
  3. Direct verification evidence for touched behavior is recorded in planning or task docs and matches the final closeout state.
  4. Sprint 5 closure on `sprint5-cat3` is supported by scoped remediation work and explicit final verification evidence.
**Plans**: 3 plans

Plans:
- [x] 03-01: Run `$ecc-code-review` on the Sprint 5 change set and triage findings by acceptance and severity.
- [x] 03-02: Remediate accepted findings, rerun targeted or full verification, and keep fixes inside the closeout scope.
- [x] 03-03: Record final closure evidence in planning or task docs and prepare the sprint-closeout handoff.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Runtime Fixes and Clean Outputs | 3/3 | Complete | 2026-03-20 |
| 2. Documentation and Governance Reconciliation | 2/2 | Complete | 2026-03-20 |
| 3. Adversarial Audit and Sprint Closure | 3/3 | Complete | 2026-03-21 |
