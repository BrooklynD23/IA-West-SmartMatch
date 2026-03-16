# Development Pipeline — Detail

## Stage Gates

| From → To | Gate Condition |
|-----------|---------------|
| IDEA → FEATURES | Idea has a problem statement + at least one proposed approach |
| FEATURES → DOC | Every feature has testable acceptance criteria |
| DOC → MEMORY | Doc references which category it belongs to |
| MEMORY → VERIFY | At least one memory entry exists for this work |
| VERIFY → TEST | plan-verifier verdict is PASS or PASS-WITH-NOTES. If FAIL, return to FEATURES |
| TEST → DRIFT | All tests pass. New code coverage ≥ 80% |
| DRIFT → COMMIT | drift-detector verdict is CLEAN or MINOR-DRIFT. If MAJOR-DRIFT, fix docs first |

## Pre-Credited Stages

All 5 categories already have substantial planning complete. Do not re-do this work.

| Document | Stage | Status | Applies To |
|----------|-------|--------|------------|
| `Category N/PLAN.md` | IDEA + FEATURES (partial) | Done | All 5 |
| `CTO_REVIEW_OUTPUT.md` | VERIFY (of plans) | Done | All 5 |
| `PRD_SECTION_CAT[N].md` | FEATURES (detailed) | Done | All 5 |
| Cat 4 prototype code | TEST + implementation | In-progress | Cat 4 |
| Cat 3 CSV data | Data inputs ready | Available | Cat 3 |

**The pipeline picks up at Stage 3 (DOC) for whichever category the team selects.**
