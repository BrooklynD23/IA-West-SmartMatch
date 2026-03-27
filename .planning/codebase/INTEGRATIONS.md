# External Integrations

**Analysis Date:** 2026-03-26

## APIs & External Services

**Gemini Developer API**
- Used for embeddings, extraction, explanations, and outreach generation through `Category 3 - IA West Smart Match CRM/src/gemini_client.py`.
- Call sites include `Category 3 - IA West Smart Match CRM/src/embeddings.py`, `Category 3 - IA West Smart Match CRM/src/extraction/llm_extractor.py`, `Category 3 - IA West Smart Match CRM/src/matching/explanations.py`, and `Category 3 - IA West Smart Match CRM/src/outreach/email_gen.py`.
- Authentication depends on `GEMINI_API_KEY` from environment variables or Streamlit secrets.

**Public university websites**
- Discovery scraping targets public university pages via `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py`.
- The stack uses `requests`, `BeautifulSoup`, optional Playwright automation, and local cache files under `Category 3 - IA West Smart Match CRM/cache/`.
- User-entered URLs in the legacy discovery UI are still constrained to public university hosts.

**Local promoted frontend/backend contract**
- The React app in `Category 3 - IA West Smart Match CRM/frontend/` talks to the FastAPI backend in `Category 3 - IA West Smart Match CRM/src/api/` over relative `/api/*` routes normalized by `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`.
- Key promoted endpoints now include:
- `Category 3 - IA West Smart Match CRM/src/api/routers/data.py`
- `Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py`
- `Category 3 - IA West Smart Match CRM/src/api/routers/matching.py`
- `Category 3 - IA West Smart Match CRM/src/api/routers/outreach.py`
- `Category 3 - IA West Smart Match CRM/src/api/routers/qr.py`
- `Category 3 - IA West Smart Match CRM/src/api/routers/feedback.py`

**Browser automation**
- Playwright remains a tooling/runtime dependency for scraping fallback and manual QA, not a hosted SaaS integration.
- Current code paths live in `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py` and verification scripts under `Category 3 - IA West Smart Match CRM/scripts/`.

## Data Storage

**Primary persistence model**
- There is still no relational database.
- Canonical source data remains CSV-backed under `Category 3 - IA West Smart Match CRM/data/`.
- The promoted FastAPI layer reads and writes local files via helpers in `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py`.

**QR storage**
- QR metadata lives in `Category 3 - IA West Smart Match CRM/data/qr/manifest.json`.
- QR scan events are appended to `Category 3 - IA West Smart Match CRM/data/qr/scan-log.jsonl`.
- Ownership: `Category 3 - IA West Smart Match CRM/src/qr/service.py`.

**Feedback / optimizer storage**
- Feedback events are appended to `Category 3 - IA West Smart Match CRM/data/feedback/feedback-log.jsonl`.
- Weight snapshots are stored in `Category 3 - IA West Smart Match CRM/data/feedback/weight-history.json`.
- Ownership: `Category 3 - IA West Smart Match CRM/src/feedback/service.py`.

**Legacy / shared file storage**
- CSV inputs such as speaker profiles, CPP events, calendar data, and sample pipeline rows remain under `Category 3 - IA West Smart Match CRM/data/`.
- Cached embeddings, scrape artifacts, explanations, and generated emails remain under `Category 3 - IA West Smart Match CRM/cache/`.

## Authentication & Identity

**User auth**
- No user-facing authentication provider is implemented for either Streamlit or the promoted React/FastAPI path.
- Access control is effectively environmental and deployment-scoped rather than identity-scoped.

**Secrets**
- `GEMINI_API_KEY` is the primary sensitive secret.
- Local configuration uses `.env`; Streamlit deployments can also use `st.secrets` via `Category 3 - IA West Smart Match CRM/src/config.py`.

## Monitoring & Observability

**Application logs**
- Python logging is used across backend modules, especially in `Category 3 - IA West Smart Match CRM/src/`.
- Frontend error handling is mostly local state and request normalization inside `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`.

**Operational scripts**
- `Category 3 - IA West Smart Match CRM/scripts/sprint4_preflight.py` remains the main repo-local verification script.
- Browser-backed evidence is still a manual/tooling step rather than a CI-integrated pipeline.

## CI/CD & Deployment

**Deployment shape**
- The active milestone records a parallel runtime model: Streamlit legacy UI, FastAPI backend, and React frontend.
- Backend entrypoint: `Category 3 - IA West Smart Match CRM/src/api/main.py`
- Frontend build entrypoint: `Category 3 - IA West Smart Match CRM/frontend/package.json`
- Legacy app entrypoint: `Category 3 - IA West Smart Match CRM/src/app.py`

**CI**
- No checked-in GitHub Actions or other automated CI definition is present.
- Verification is currently command-driven and documented in `.planning/` artifacts plus `tasks/todo.md`.

## Environment Configuration

**Backend**
- Shared runtime config lives in `Category 3 - IA West Smart Match CRM/src/config.py`.
- Notable variables now include factor and optimizer settings such as the default weights and optimizer bounds consumed by `Category 3 - IA West Smart Match CRM/src/feedback/service.py` and `Category 3 - IA West Smart Match CRM/src/matching/`.

**Frontend**
- Local frontend config is provided by `Category 3 - IA West Smart Match CRM/frontend/vite.config.ts`, `Category 3 - IA West Smart Match CRM/frontend/tsconfig.json`, and project CSS tokens under `Category 3 - IA West Smart Match CRM/frontend/src/styles/`.

## Webhooks & Callbacks

**Outgoing**
- HTTPS requests to Gemini REST endpoints from `Category 3 - IA West Smart Match CRM/src/gemini_client.py`.
- HTTPS requests to public university sites from `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py`.
- Local browser automation sessions from Playwright-backed scripts and scraping helpers.

**Incoming**
- No third-party webhooks are configured.
- The only inbound HTTP surface is the local FastAPI app under `Category 3 - IA West Smart Match CRM/src/api/`.

## Notable Gaps

- No database, queue, or durable multi-user state store.
- No auth provider.
- No transactional email or calendar SaaS integration.
- No checked-in error-tracking or analytics SaaS.

---

*Integration audit: 2026-03-26*
