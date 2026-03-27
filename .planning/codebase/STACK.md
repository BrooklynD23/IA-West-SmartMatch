# Technology Stack

**Analysis Date:** 2026-03-26

## Languages

**Primary**
- Python - Core backend, legacy Streamlit UI, scripts, and tests live under `Category 3 - IA West Smart Match CRM/src/`, `Category 3 - IA West Smart Match CRM/scripts/`, and `Category 3 - IA West Smart Match CRM/tests/`.
- TypeScript - The promoted React coordinator app lives under `Category 3 - IA West Smart Match CRM/frontend/src/`.

**Secondary**
- Markdown - Planning, milestone, and product context live in `.planning/`, `Category 3 - IA West Smart Match CRM/docs/`, `Agents.md`, and `tasks/todo.md`.
- JSON / JSONL - QR and feedback persistence now use local files such as `Category 3 - IA West Smart Match CRM/data/qr/manifest.json`, `Category 3 - IA West Smart Match CRM/data/qr/scan-log.jsonl`, `Category 3 - IA West Smart Match CRM/data/feedback/feedback-log.jsonl`, and `Category 3 - IA West Smart Match CRM/data/feedback/weight-history.json`.
- CSV / NPY - Canonical event, speaker, calendar, and pipeline inputs plus cached embeddings remain file-backed under `Category 3 - IA West Smart Match CRM/data/` and `Category 3 - IA West Smart Match CRM/cache/`.
- TOML - Streamlit runtime config lives in `Category 3 - IA West Smart Match CRM/.streamlit/config.toml`.

## Runtime

**Python runtime**
- Local development uses the checked-in venv at `Category 3 - IA West Smart Match CRM/.venv/`.
- Deployment target remains CPython 3.11 via `Category 3 - IA West Smart Match CRM/runtime.txt`.
- The legacy Streamlit app still starts from `Category 3 - IA West Smart Match CRM/src/app.py`.
- The promoted API server starts from `Category 3 - IA West Smart Match CRM/src/api/main.py`.

**Frontend runtime**
- Vite dev/build tooling is defined in `Category 3 - IA West Smart Match CRM/frontend/package.json`.
- The React app targets local development on port `5173` and production static output under `Category 3 - IA West Smart Match CRM/frontend/dist/`.

**Package managers / lockfiles**
- Python dependencies are declared in `Category 3 - IA West Smart Match CRM/requirements.txt`.
- npm dependencies are declared in `Category 3 - IA West Smart Match CRM/frontend/package.json`.
- Lockfiles now exist for both stacks: `Category 3 - IA West Smart Match CRM/package-lock.json` and `Category 3 - IA West Smart Match CRM/frontend/package-lock.json`.

## Frameworks

**Backend / legacy app**
- Streamlit 1.42.2 powers the original coordinator UI in `Category 3 - IA West Smart Match CRM/src/app.py` and `Category 3 - IA West Smart Match CRM/src/ui/`.
- FastAPI powers the promoted backend in `Category 3 - IA West Smart Match CRM/src/api/main.py` and `Category 3 - IA West Smart Match CRM/src/api/routers/`.
- Pydantic request models are used in router modules such as `Category 3 - IA West Smart Match CRM/src/api/routers/matching.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/qr.py`, and `Category 3 - IA West Smart Match CRM/src/api/routers/feedback.py`.

**Frontend**
- React 18.3.1 is the coordinator app runtime in `Category 3 - IA West Smart Match CRM/frontend/src/`.
- React Router is used in `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx`.
- Vite 6 drives frontend bundling via `Category 3 - IA West Smart Match CRM/frontend/vite.config.ts`.
- Tailwind CSS 4 is wired through `Category 3 - IA West Smart Match CRM/frontend/postcss.config.mjs`.
- Recharts is used for dashboard/pipeline analytics in `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx` and `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Pipeline.tsx`.
- Lucide icons, Radix UI primitives, MUI packages, and project CSS tokens are used across `Category 3 - IA West Smart Match CRM/frontend/src/components/` and `Category 3 - IA West Smart Match CRM/frontend/src/styles/`.

**Data / matching / utilities**
- pandas and NumPy support CSV ingestion, cached embeddings, and match scoring in `Category 3 - IA West Smart Match CRM/src/data_loader.py`, `Category 3 - IA West Smart Match CRM/src/embeddings.py`, and `Category 3 - IA West Smart Match CRM/src/matching/`.
- Plotly remains in use on the Streamlit side under `Category 3 - IA West Smart Match CRM/src/ui/`.
- qrcode and Pillow are now part of the QR generation path in `Category 3 - IA West Smart Match CRM/src/qr/service.py`.

**Testing**
- pytest is the backend test runner for `Category 3 - IA West Smart Match CRM/tests/`.
- Frontend currently has no checked-in test runner or spec files under `Category 3 - IA West Smart Match CRM/frontend/`.

## Key Dependencies

**Backend critical**
- `fastapi` / `uvicorn` - REST promotion path in `Category 3 - IA West Smart Match CRM/src/api/`.
- `streamlit` - Legacy coordinator shell and demo path in `Category 3 - IA West Smart Match CRM/src/app.py`.
- `pandas`, `numpy` - Canonical data loading and scoring logic in `Category 3 - IA West Smart Match CRM/src/data_loader.py` and `Category 3 - IA West Smart Match CRM/src/matching/`.
- `qrcode`, `Pillow` - Deterministic QR generation in `Category 3 - IA West Smart Match CRM/src/qr/service.py`.

**Frontend critical**
- `react`, `react-dom`, `react-router` - SPA routing and rendering in `Category 3 - IA West Smart Match CRM/frontend/src/app/`.
- `recharts` - analytics surfaces on dashboard and pipeline pages.
- `lucide-react` - iconography across the promoted UI.
- `vite`, `typescript`, `@vitejs/plugin-react` - local build pipeline.

**AI / discovery / scraping**
- No Gemini SDK package is used; direct REST calls live in `Category 3 - IA West Smart Match CRM/src/gemini_client.py`.
- `requests`, `beautifulsoup4`, and `playwright` support discovery scraping in `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py`.

## Configuration

**Backend env/config**
- `Category 3 - IA West Smart Match CRM/src/config.py` is the shared source of truth for environment variables, factor weights, optimizer bounds, and runtime paths.
- `.env`-style configuration is bootstrapped through `load_dotenv()` in `Category 3 - IA West Smart Match CRM/src/config.py`.
- Streamlit-specific settings live in `Category 3 - IA West Smart Match CRM/.streamlit/config.toml`.

**Frontend config**
- `Category 3 - IA West Smart Match CRM/frontend/vite.config.ts` controls the Vite build and local dev setup.
- Theme and font tokens live in `Category 3 - IA West Smart Match CRM/frontend/src/styles/theme.css` and `Category 3 - IA West Smart Match CRM/frontend/src/styles/fonts.css`.
- The frontend API contract and normalization layer are centralized in `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`.

## Platform Requirements

**Development**
- Python venv support is required for the backend and tests.
- Node/npm are required for the React app under `Category 3 - IA West Smart Match CRM/frontend/`.
- Playwright browser binaries are still needed for browser-backed scraping or UAT, but are not always available in-session.

**Deployment**
- The repo currently supports a parallel runtime model recorded in `.planning/STATE.md`: Streamlit on `:8501`, FastAPI on `:8000`, and React/Vite on `:5173`.
- Production hosting remains partly hackathon-scoped and file-backed; QR, feedback, and optimizer state are persisted locally rather than in a database.

---

*Stack analysis: 2026-03-26*
