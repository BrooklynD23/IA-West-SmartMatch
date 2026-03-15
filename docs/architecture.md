# Architecture Overview

> This document will be filled in once the active category is chosen.
> Use the category's PLAN.md as the starting point.

## Placeholder Structure

```
src/
├── app.py          # Streamlit entrypoint — UI and routing
├── llm.py          # LLM client wrapper (OpenAI / OpenRouter)
├── data.py         # Data loading and preprocessing
├── features/       # Feature modules (one per major feature)
│   └── ...
└── utils.py        # Shared helpers
```

## Guiding Principles

1. **Demo-first** — Every architectural decision should make the 5-minute demo better.
2. **Small files** — Keep modules under 400 lines. Extract when they grow.
3. **No secrets in code** — All API keys via `.env` + `python-dotenv`.
4. **Immutable data** — Never mutate DataFrames in-place; always return new copies.

## LLM Integration Pattern

```python
# shared pattern across all categories
from src.llm import call_llm

response = call_llm(
    prompt="...",
    system="...",
    model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
)
```

## Data Flow

```
[Raw Data / User Input]
        ↓
[src/data.py — load + validate]
        ↓
[src/features/* — business logic]
        ↓
[LLM API (optional enrichment)]
        ↓
[src/app.py — Streamlit display]
```

## Deployment

- Streamlit Community Cloud (free tier)
- Secrets via dashboard UI (not committed to git)
- No database required — stateless CSV/in-memory approach
