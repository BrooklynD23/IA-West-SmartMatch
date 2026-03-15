# Dev Environment Setup

## Prerequisites

- Python 3.10+
- Git
- A text editor (VS Code recommended)
- OpenAI or OpenRouter API key

## First-Time Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd HackathonForBetterFuture2026

# 2. Copy root env template
cp .env.example .env
# Edit .env and fill in OPENAI_API_KEY (minimum required)

# 3. Once active category is decided (replace N):
cd "Category N - <Name>"
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 4. Copy category .env (inherits root .env vars)
cp .env.example .env
```

## Running the App

```bash
# From the category folder with venv active:
streamlit run src/app.py

# Or from repo root using Make:
make run CAT=4
```

## Running Tests

```bash
# From category folder:
pytest tests/ -v --cov=src --cov-report=term-missing

# Or from repo root:
make test CAT=4
```

## Environment Variables

See `.env.example` at repo root for all available variables.
Category folders also have their own `.env.example` with category-specific vars.

**Never commit `.env` files.** They are in `.gitignore`.

## Streamlit Secrets (for deployment)

When deploying to Streamlit Community Cloud, add secrets via the dashboard UI
(Settings → Secrets) — do **not** commit `.streamlit/secrets.toml`.

## Common Issues

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Make sure venv is activated and `pip install -r requirements.txt` ran |
| API key errors | Check `.env` exists and `OPENAI_API_KEY` is set |
| Streamlit not found | Venv not activated, or `pip install streamlit` |
