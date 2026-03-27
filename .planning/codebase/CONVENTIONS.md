# Coding Conventions

**Analysis Date:** 2026-03-26

## Naming Patterns

**Files:**
- Use `snake_case.py` for Python modules under `Category 3 - IA West Smart Match CRM/src/` and `Category 3 - IA West Smart Match CRM/tests/`; examples: `src/runtime_state.py`, `src/api/routers/matching.py`, `tests/test_api_feedback.py`.
- Use `PascalCase.tsx` for React pages and reusable components under `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/`, `Category 3 - IA West Smart Match CRM/frontend/src/app/components/`, and `Category 3 - IA West Smart Match CRM/frontend/src/components/`; examples: `frontend/src/app/pages/Dashboard.tsx`, `frontend/src/components/FeedbackForm.tsx`, `frontend/src/components/QRCodeCard.tsx`.
- Keep non-component frontend support files lowercase or route-style names; examples: `frontend/src/lib/api.ts`, `frontend/src/app/routes.tsx`, `frontend/src/styles/theme.css`.
- Name test files `test_<feature>.py` and align them to the production surface or workflow they cover; examples: `tests/test_page_router.py`, `tests/test_api_qr.py`, `tests/test_sprint4_preflight.py`.

**Functions:**
- Use `snake_case` for Python functions and reserve a leading `_` for module-private helpers; examples: `_resolve_embedding_lookup_dicts()` in `src/app.py`, `_normalize_ranked_match()` in `src/api/routers/matching.py`, `_feedback_entry_id()` in `src/feedback/service.py`.
- Use `camelCase` for TypeScript helpers and event handlers; examples: `monthLabel()` in `frontend/src/app/pages/Dashboard.tsx`, `handleSubmit()` in `frontend/src/components/FeedbackForm.tsx`, `resolvePreviewSource()` in `frontend/src/components/QRCodeCard.tsx`.
- Use `PascalCase` for React components and inline view helpers that render JSX; examples: `Dashboard`, `AIMatching`, `MetricCard`, `ScoreRing`, and `FactorRadar` in `frontend/src/app/pages/AIMatching.tsx`.

**Variables:**
- Use `snake_case` for Python locals, parameters, and session-state keys; examples: `embedding_issues` in `src/app.py`, `current_page` in `src/ui/page_router.py`, and `"demo_mode"` or `"matching_discovered_events"` in `streamlit.session_state`.
- Use `UPPER_SNAKE_CASE` for Python constants and registries; examples: `DATASET_FILE_NAMES` in `src/app.py`, `FACTOR_REGISTRY` and `DEFAULT_WEIGHTS` in `src/config.py`, `SCAN_LOG_FILENAME` in `src/qr/service.py`.
- Use `camelCase` for frontend locals and React state; examples: `calendarEvents`, `feedbackStats`, `primaryMatch`, and `leadAdjustment` in `frontend/src/app/pages/Dashboard.tsx`.
- Use CSS custom properties in `--kebab-case`; examples in `frontend/src/styles/theme.css` include `--primary`, `--sidebar-border`, and `--color-surface-container`.

**Types:**
- Use `PascalCase` for Python dataclasses and Pydantic models; examples: `FactorSpec` in `src/config.py`, `RankRequest` and `ScoreRequest` in `src/api/routers/matching.py`, `FeedbackSubmitRequest` in `src/api/routers/feedback.py`.
- Use `PascalCase` for TypeScript interfaces, prop types, and named unions; examples: `RankedMatch`, `FeedbackStatsSummary`, `MetricCardProps`, and `QRCodeCardProps` in `frontend/src/lib/api.ts`, `frontend/src/app/components/MetricCard.tsx`, and `frontend/src/components/QRCodeCard.tsx`.

## Code Style

**Formatting:**
- No formatter config is checked in for either stack. `Category 3 - IA West Smart Match CRM/` does not contain `pyproject.toml`, `ruff.toml`, `pytest.ini`, `eslint.config.*`, `.eslintrc*`, or `.prettierrc*`, so match the surrounding file style instead of introducing a new formatter contract.
- Preserve 4-space indentation, top-level module docstrings, and section-divider comments in Python modules; see `src/app.py`, `src/config.py`, `src/feedback/service.py`, and `tests/test_styles.py`.
- Preserve 2-space indentation, double-quoted imports, and trailing commas in multiline frontend literals; see `frontend/src/app/pages/Dashboard.tsx`, `frontend/src/app/pages/AIMatching.tsx`, and `frontend/src/components/FeedbackForm.tsx`.
- Keep `st.set_page_config(...)` as the first Streamlit call in `src/app.py`, and keep the follow-on `from src...` imports marked with `# noqa: E402`. That ordering is part of the app contract.
- Keep JSX styling inline with Tailwind utility strings or short local constants instead of extracting ad hoc CSS modules; see `frontend/src/app/components/Layout.tsx`, `frontend/src/app/components/MetricCard.tsx`, and `frontend/src/components/OutreachWorkflowModal.tsx`.
- Keep frontend theme tokens in `frontend/src/styles/theme.css` and import styles through `frontend/src/styles/index.css`.

**Linting:**
- No active lint runner is committed. Use the source tree itself as the lint baseline.
- Treat `frontend/tsconfig.json` as the primary static-style contract for the React app: `strict` is enabled, `noFallthroughCasesInSwitch` is enabled, and `noUnusedLocals` / `noUnusedParameters` are intentionally disabled.
- Preserve narrow suppressions instead of widening them. Examples: `# noqa: E402` in `src/app.py` and defensive `except Exception as exc:  # pragma: no cover` boundaries in `src/api/routers/*.py`.
- Avoid style-only rewrites. Existing repo guidance in `AGENTS.md` and `tasks/lessons.md` favors targeted fixes over broad cleanup.

## Import Organization

**Order:**
1. Standard-library imports or React runtime hooks first.
2. Third-party packages second.
3. Project-local imports last, using `from src...`, `@/...`, or short relative sibling imports.

```python
import logging
from pathlib import Path

import pandas as pd

from src.config import DATA_DIR
```

```tsx
import { useEffect, useState } from "react";
import { Activity, Sparkles } from "lucide-react";

import { fetchFeedbackStats, type FeedbackStatsSummary } from "@/lib/api";

import { MetricCard } from "../components/MetricCard";
```

**Path Aliases:**
- Use package-root imports from `src`, not bare module imports and not relative Python package hops; see `src/api/main.py`, `src/ui/page_router.py`, and `scripts/sprint4_preflight.py`.
- For Python scripts under `Category 3 - IA West Smart Match CRM/scripts/`, add `PROJECT_ROOT` to `sys.path` once and then import from `src`, following `scripts/sprint4_preflight.py`.
- Use the frontend alias `@/*` for cross-feature imports inside `frontend/src/`, as defined in `frontend/tsconfig.json` and `frontend/vite.config.ts`.
- Use short relative imports only for neighboring frontend modules inside the same feature area; see `frontend/src/app/App.tsx`, `frontend/src/app/routes.tsx`, and `frontend/src/app/pages/Dashboard.tsx`.

## Error Handling

**Patterns:**
- Validate early and return narrow domain errors for invalid input or configuration; examples include `validate_config()` in `src/config.py`, `deterministic_referral_code()` callers in `src/qr/service.py`, and Pydantic field constraints in `src/api/routers/feedback.py` and `src/api/routers/matching.py`.
- Use graceful fallbacks for UI-facing or cache-backed flows instead of crashing the app. Examples: empty collections and warnings in `src/app.py`, cache-aware fallbacks in `src/scraping/scraper.py`, and default summaries in `frontend/src/app/pages/Dashboard.tsx` and `frontend/src/components/FeedbackForm.tsx`.
- Wrap FastAPI route bodies in a small API boundary that converts unexpected exceptions into `HTTPException(status_code=500, detail=...)`; see `_server_error()` and the `rank()`, `score()`, `submit()`, and `stats()` handlers in `src/api/routers/`.
- Surface operational errors to users through the UI, not stdout. Streamlit uses `st.warning(...)` / `st.error(...)` in `src/app.py` and `src/ui/styles.py`; React stores `error` state and renders inline banners in `frontend/src/app/pages/Dashboard.tsx`, `frontend/src/components/FeedbackForm.tsx`, and `frontend/src/components/OutreachWorkflowModal.tsx`.
- Normalize API payloads at the boundary so downstream UI code does not guess field names. `_normalize_ranked_match()` in `src/api/routers/matching.py` and the frontend adapters in `frontend/src/lib/api.ts` are the pattern to follow.

## Logging

**Framework:** `logging` on the Python side; no structured browser logging layer is checked in for `frontend/src/`.

**Patterns:**
- Create one module logger with `logging.getLogger(__name__)` when a module emits operational events; see `src/app.py` and `src/matching/engine.py`.
- Use `configure_logging()` from `src/utils.py` for script entry points instead of hand-rolled logging setup.
- Prefer `logger.warning(...)`, `logger.error(...)`, and `logger.exception(...)` over `print()`.
- Keep frontend diagnostics out of the shipped code. No persistent `console.log(...)` usage is present under `frontend/src/`; preserve that baseline.

## Comments

**When to Comment:**
- Start Python modules with a short docstring that states the file responsibility; this is consistent across `src/`, `tests/`, and `scripts/`.
- Use section-divider comments in long Python modules to break up helpers, schemas, and public APIs; see `src/app.py`, `src/config.py`, and `tests/test_styles.py`.
- Use inline comments only for non-obvious contracts, compatibility layers, or browser/runtime quirks. Examples include the Streamlit ordering note in `src/app.py`, compatibility alias comment in `src/api/routers/matching.py`, and QR preview note in `frontend/src/components/QRCodeCard.tsx`.
- Use frontend comments sparsely and mostly to label UI sections or explain one-off DOM behavior; see `frontend/src/app/components/Layout.tsx` and `frontend/src/components/OutreachWorkflowModal.tsx`.

**JSDoc/TSDoc:**
- Not used broadly. The React code relies on prop types and interface names instead of JSDoc blocks.
- Python docstrings are the primary documentation contract for functions, scripts, and modules.

## Function Design

**Size:** Prefer medium-sized functions with extracted helpers over monolithic view or service code. Python modules such as `src/feedback/service.py` and frontend pages such as `frontend/src/app/pages/AIMatching.tsx` both split calculations into small pure helpers above the main entry point.

**Parameters:** Favor explicit typed parameters and typed prop objects over ambient globals. Use Pydantic request models for API bodies in `src/api/routers/`, typed props in `frontend/src/components/`, and keyword-heavy calls when a Python function has many arguments, as in `src/app.py` and `src/matching/engine.py`.

**Return Values:** Return stable normalized shapes:
- Python utilities return primitive containers or dataclasses with predictable keys; see `src/utils.py`, `src/config.py`, and `src/feedback/service.py`.
- API routers return frontend-oriented dictionaries rather than raw pandas rows; see `src/api/routers/matching.py`, `src/api/routers/feedback.py`, and `src/api/routers/qr.py`.
- Frontend fetch helpers expose typed interfaces from `frontend/src/lib/api.ts` and use empty arrays or empty summary objects for recoverable no-data states.

## Module Design

**Exports:**
- Prefer direct imports from leaf Python modules such as `from src.api.routers.feedback import submit` or `from src.matching.engine import rank_speakers_for_event`.
- Keep `__init__.py` files minimal and do not build broad Python re-export layers; `src/extraction/__init__.py` and package markers under `src/api/` are the model.
- Favor named exports for React pages and reusable components; examples include `Dashboard`, `AIMatching`, `Layout`, `FeedbackForm`, and `QRCodeCard`.
- Reserve default exports for top-level entry files only. `frontend/src/app/App.tsx` is the main example.

**Barrel Files:** Not used beyond minimal Python package markers. The frontend does not use `index.ts` barrel files, and future code should continue importing components from their concrete file paths.

---

*Convention analysis: 2026-03-26*
