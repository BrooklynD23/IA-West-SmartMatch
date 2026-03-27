# Testing Patterns

**Analysis Date:** 2026-03-26

## Test Framework

**Runner:**
- `pytest` `8.3.4`, declared in `Category 3 - IA West Smart Match CRM/requirements.txt`.
- Config: Not detected. `Category 3 - IA West Smart Match CRM/` does not contain `pytest.ini`, `pyproject.toml`, or `tox.ini`, so discovery and behavior come from direct command invocation and in-test fixtures.
- Browser E2E also runs through Python `pytest`, using Playwright-backed suites in `Category 3 - IA West Smart Match CRM/tests/test_e2e_flows.py` and `Category 3 - IA West Smart Match CRM/tests/test_e2e_playwright.py`.
- Frontend-specific JS test tooling is not used. `Category 3 - IA West Smart Match CRM/frontend/package.json` exposes `dev`, `build`, and `preview` only; there is no `test` script and no `vitest`/`jest` config.

**Assertion Library:**
- Native `assert` statements are the default throughout `Category 3 - IA West Smart Match CRM/tests/`.
- Use `pytest.raises(...)` for contract violations and `pytest.approx(...)` for numeric tolerance; see `tests/test_api_matching.py`, `tests/test_embeddings.py`, and `tests/test_engine.py`.
- Use Playwright `expect(...)` assertions in the browser suite inside `tests/test_e2e_playwright.py`.

**Run Commands:**
```bash
./.venv/bin/python -m pytest -q
./.venv/bin/python -m pytest tests/test_<module>.py -q
./.venv/bin/python -m pytest --cov=src --cov-report=term-missing
```

## Test File Organization

**Location:**
- Keep automated Python tests in `Category 3 - IA West Smart Match CRM/tests/`.
- Keep shared manual QA artifacts and rehearsal logs in `Category 3 - IA West Smart Match CRM/docs/testing/`.
- Keep browser automation and preflight helpers in `Category 3 - IA West Smart Match CRM/scripts/`.
- Do not add frontend test files under `Category 3 - IA West Smart Match CRM/frontend/src/` unless the repository first adopts a JS test runner. No `*.test.tsx` or `*.spec.tsx` files are present there now.

**Naming:**
- Name test modules `test_<feature>.py`; examples: `tests/test_api_feedback.py`, `tests/test_page_router.py`, `tests/test_sprint4_preflight.py`, and `tests/test_e2e_flows.py`.
- Reserve `tests/conftest.py` for shared environment bootstrapping that multiple suites need.
- Use script names that describe the verification action directly; examples: `scripts/sprint4_preflight.py` and `scripts/run_playwright_demo_qa.py`.

**Structure:**
```text
Category 3 - IA West Smart Match CRM/
├── tests/
│   ├── conftest.py
│   ├── test_api_feedback.py
│   ├── test_page_router.py
│   ├── test_sprint4_preflight.py
│   ├── test_e2e_flows.py
│   └── test_e2e_playwright.py
├── docs/testing/
│   ├── README.md
│   ├── test_log.md
│   ├── bug_log.md
│   ├── rehearsal_log.md
│   └── 2026-03-25-playwright-demo-report.md
└── scripts/
    ├── sprint4_preflight.py
    └── run_playwright_demo_qa.py
```

## Test Structure

**Suite Organization:**
```python
@patch("streamlit.session_state", new_callable=dict)
def test_init_page_state_normalizes_alias_and_flags(mock_state: dict) -> None:
    import src.ui.page_router as router

    with (
        patch.object(router, "_get_query_params", return_value={"route": "coordinator", "demo": "1"}),
        patch.object(router, "_set_query_params") as mock_set,
    ):
        router.init_page_state()

    assert mock_state["current_page"] == "dashboard"
    mock_set.assert_called_once()


class TestResolveEmbeddingLookupDicts:
    def test_bootstraps_missing_cache_when_gemini_key_is_available(self) -> None:
        ...
```

**Patterns:**
- Mix free-function tests for narrow contracts with `class Test...:` groupings for larger module surfaces; compare `tests/test_page_router.py` with `tests/test_app.py` and `tests/test_styles.py`.
- Keep fixtures close to the suite that uses them. Module-local factories dominate, while `tests/conftest.py` is reserved for truly global environment setup.
- Prefer direct function calls over full HTTP clients when testing the FastAPI layer. `tests/test_api_matching.py`, `tests/test_api_feedback.py`, and `tests/test_api_qr.py` invoke router functions and Pydantic request models directly instead of using `TestClient`.
- Use `ExitStack` when a test must patch several collaborators around a single entry point, as in `tests/test_app.py`.
- Load script modules dynamically when the test targets a standalone script entry point. `tests/test_sprint4_preflight.py` uses `importlib.util.spec_from_file_location(...)` to test `scripts/sprint4_preflight.py`.

## Mocking

**Framework:** `unittest.mock` (`patch`, `MagicMock`, `AsyncMock`) plus `pytest` `monkeypatch`

**Patterns:**
```python
@patch("streamlit.session_state", new_callable=dict)
def test_navigate_to_updates_session_and_triggers_rerun(mock_state: dict) -> None:
    import src.ui.page_router as router

    with (
        patch.object(router, "_get_query_params", return_value={}),
        patch.object(router, "_set_query_params") as mock_set,
        patch.object(router.st, "rerun") as mock_rerun,
    ):
        router.navigate_to("coordinator", role="coordinator", demo=True)

    mock_set.assert_called_once()
    mock_rerun.assert_called_once()
```

```python
@pytest.fixture()
def feedback_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(data_helpers, "_data_dir", lambda: data_dir)
    monkeypatch.setattr(feedback_service, "_data_dir", lambda: data_dir)
    yield data_dir
```

```python
mock_page = AsyncMock()
mock_browser = AsyncMock()
mock_pw_ctx = AsyncMock()
mock_pw_ctx.__aenter__ = AsyncMock(return_value=mock_pw)
```

**What to Mock:**
- Mock Streamlit before importing `src` modules. `tests/conftest.py` installs a fake `streamlit` module and fake `streamlit.errors.StreamlitAPIException`.
- Mock voice/audio dependencies globally in `tests/conftest.py` because those packages are not guaranteed in CI or local review environments.
- Mock network, DNS, robots, and Playwright internals in scraper tests; see `tests/test_scraper.py`.
- Mock persistence roots with `tmp_path` plus `monkeypatch.setattr(...)` of `_data_dir`, path constants, or cached loader functions in `tests/test_api_feedback.py`, `tests/test_api_qr.py`, and `tests/test_pipeline_updater.py`.
- Mock Gemini and other model calls at the module import site, not at a downstream wrapper. Examples: `src.extraction.llm_extractor.generate_text`, `src.matching.explanations.generate_text`, and `src.embeddings.generate_embeddings`.
- When config state matters, patch the source module that owns the value first, following the pattern in `tests/test_config.py` and `tests/test_embeddings.py`.

**What NOT to Mock:**
- Do not mock the scoring math when verifying `src/matching/engine.py` and `src/matching/factors.py`. Those suites rely on real pandas/NumPy calculations with deterministic fixtures.
- Do not bypass the repo’s demo fixture contract when testing Demo Mode behavior. `tests/test_demo_mode.py` treats `cache/demo_fixtures/*.json` as a checked-in interface.
- Do not replace `app.routes` inspection with fakes when testing router registration. `tests/test_api_feedback.py` and `tests/test_api_qr.py` assert directly against `src.api.main.app`.

## Fixtures and Factories

**Test Data:**
```python
@pytest.fixture()
def qr_storage(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    (data_dir / "qr").mkdir(parents=True)

    monkeypatch.setattr(data_helpers, "_data_dir", lambda: data_dir)
    monkeypatch.setattr(qr_service, "_data_dir", lambda: data_dir)
    yield data_dir
```

```python
def _request(path: str = "/api/qr/generate", scheme: str = "https", host: str = "example.org") -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "scheme": scheme,
        "path": path,
        "server": (host, 443 if scheme == "https" else 80),
        "headers": [(b"host", host.encode("utf-8"))],
    }
    return Request(scope, _receive)
```

**Location:**
- Keep small inline fixtures and CSV/DataFrame factories in the owning test module; see `tests/test_app.py`, `tests/test_engine.py`, and `tests/test_data_loader.py`.
- Keep global environment setup in `tests/conftest.py` only.
- Keep checked-in golden fixtures under `Category 3 - IA West Smart Match CRM/cache/demo_fixtures/`.
- Keep browser QA artifacts under `Category 3 - IA West Smart Match CRM/output/playwright/` and human-readable logs under `Category 3 - IA West Smart Match CRM/docs/testing/`.

## Coverage

**Requirements:** No coverage gate is enforced by checked-in tooling.
- `pytest-cov` is installed via `Category 3 - IA West Smart Match CRM/requirements.txt`.
- Project docs such as `Category 3 - IA West Smart Match CRM/docs/README.md` and `Category 3 - IA West Smart Match CRM/docs/sprints/README.md` treat `--cov=src --cov-report=term-missing` and 80%+ coverage as the working target, but that target is cultural rather than enforced by config.

**View Coverage:**
```bash
./.venv/bin/python -m pytest --cov=src --cov-report=term-missing
```

## Test Types

**Unit Tests:**
- This is the dominant test type. Most Python modules in `Category 3 - IA West Smart Match CRM/src/` have a direct peer test under `Category 3 - IA West Smart Match CRM/tests/`.
- Unit coverage includes helpers, matching factors, QR and feedback services, Streamlit view logic, and typed adapters in files such as `tests/test_utils.py`, `tests/test_factors.py`, `tests/test_api_qr.py`, and `tests/test_styles.py`.

**Integration Tests:**
- Integration tests focus on file-backed persistence, API/router boundaries, and script/module wiring rather than live external services.
- `tests/test_api_feedback.py`, `tests/test_api_qr.py`, `tests/test_api_outreach_workflow.py`, and `tests/test_api_calendar.py` validate router behavior by combining real router functions, Pydantic models, and temp storage.
- `tests/test_sprint4_preflight.py` validates the standalone deployment/prewarm script contract in `scripts/sprint4_preflight.py`.
- The Streamlit integration seam is covered through orchestrated patches in `tests/test_app.py`, `tests/test_pipeline_tab.py`, and `tests/test_match_engine_page.py`.

**E2E Tests:**
- Browser-backed E2E lives in Python, not JavaScript. Use `tests/test_e2e_flows.py` for the routed workspace flow and `tests/test_e2e_playwright.py` for the broader page audit.
- `tests/test_e2e_flows.py` uses `pytest.mark.skipif(os.getenv("SKIP_E2E") == "1", ...)` and expects a running Streamlit app on `http://localhost:8501`.
- `scripts/run_playwright_demo_qa.py` is the scripted artifact-producing browser pass that writes screenshots and JSON summaries into `output/playwright/`.
- Manual E2E and rehearsal evidence remains part of the shipping workflow through `docs/testing/README.md`, `docs/testing/test_log.md`, `docs/testing/bug_log.md`, and `docs/testing/rehearsal_log.md`.
- React component tests are not used. Treat `cd frontend && npm run build` as the frontend verification floor until the repository adopts a JS test runner.

## Common Patterns

**Async Testing:**
```python
mock_page = AsyncMock()
mock_browser = AsyncMock()
mock_pw_ctx = AsyncMock()
mock_pw_ctx.__aenter__ = AsyncMock(return_value=mock_pw)
mock_pw_ctx.__aexit__ = AsyncMock(return_value=False)
```
- Follow the `tests/test_scraper.py` pattern when isolating Playwright-backed or other async integrations.

**Error Testing:**
```python
with pytest.raises(ValidationError):
    RankRequest(limit=3)
```

```python
result = module.check_runtime_file()
assert result.status == "fail"
assert "python-3.11" in result.details
```

```python
payload = feedback_stats()
assert 0.0 <= payload["pain_score"] <= 100.0
```
- Use `pytest.raises(...)` for hard contract failures and explicit status/shape assertions for recoverable behavior or warning-level flows.

## Verification Habits

- Start with targeted tests for the changed files, then expand to the full suite from `Category 3 - IA West Smart Match CRM/` using `./.venv/bin/python -m pytest -q`.
- For Streamlit routing, feedback, or other recent workspace changes, `tests/test_page_router.py`, `tests/test_app.py`, `tests/test_api_feedback.py`, and `tests/test_api_qr.py` are the representative thin slices to run first.
- For deployment, cache, or environment-sensitive work, run `Category 3 - IA West Smart Match CRM/scripts/sprint4_preflight.py` and optionally `--json-out` or `--prewarm-discovery`, following `docs/testing/README.md`.
- For routed browser flows, run either `./.venv/bin/python -m pytest tests/test_e2e_flows.py -q` or `./.venv/bin/python scripts/run_playwright_demo_qa.py` with Streamlit already serving `src/app.py` on port `8501`.
- For React changes under `Category 3 - IA West Smart Match CRM/frontend/src/`, run `cd 'Category 3 - IA West Smart Match CRM/frontend' && npm run build`. There is no npm-side unit-test safety net.
- Preserve evidence in the repo when a change affects ship readiness: update `docs/testing/*.md`, Playwright artifacts under `output/playwright/`, or the relevant phase/milestone verification docs under `.planning/`.

---

*Testing analysis: 2026-03-26*
