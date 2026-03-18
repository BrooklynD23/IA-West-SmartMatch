# Gemini Provider Decision — 2026-03-18

## Decision

The planned provider for new LLM work in Category 3 is the Gemini Developer API via Google AI Studio, not OpenAI.

This is a documentation-level decision only. The checked-in Python code still uses OpenAI-specific config and clients until the implementation migration is completed.

## Recommended Models

### Text generation, extraction, and explanations

Use `gemini-2.5-flash-lite`.

This is the recommended default for:

- match explanation cards
- structured event extraction from scraped pages
- outreach email generation

Why this model:

- It is the cheapest currently practical stable text model for this project.
- It has a free tier in the Gemini Developer API / AI Studio flow.
- Its published standard paid pricing is $0.10 per 1M input tokens and $0.40 per 1M output tokens.
- It is a better migration target than `gemini-2.0-flash-lite`, which is already on a published shutdown path for June 1, 2026.

### Embeddings

Use `gemini-embedding-001`.

Why this model:

- It is the stable text embedding model in the Gemini API.
- It supports controllable embedding size, so we can keep `output_dimensionality=1536` and avoid unnecessary downstream shape changes in the current codebase.
- Its published standard paid pricing is $0.15 per 1M input tokens.
- It is the direct replacement path for older Google text embedding models.

## Cost Recommendation

For this project, the cheapest model I recommend adopting is `gemini-2.5-flash-lite`.

I am not recommending `gemini-2.0-flash-lite` even though it is listed at a lower token price of $0.075 per 1M input tokens and $0.30 per 1M output tokens, because as of March 18, 2026 it has a published shutdown date of June 1, 2026. That is too close for a new migration target.

Use this pairing:

- `gemini-2.5-flash-lite` for all text generation tasks
- `gemini-embedding-001` for all embedding generation tasks

Published shutdown dates to plan around:

- `gemini-2.5-flash-lite`: July 22, 2026
- `gemini-embedding-001`: July 14, 2026
- `gemini-2.0-flash-lite`: June 1, 2026

## Suggested Environment Target

When the code migration starts, target variables like:

```dotenv
GEMINI_API_KEY=...
GEMINI_TEXT_MODEL=gemini-2.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIMENSION=1536
```

## Migration Path

### Lowest-code-churn path

Because the current codebase already uses the `openai` Python client, the fastest migration path is to use Gemini's OpenAI-compatible endpoint first:

- keep the existing client pattern temporarily
- switch API key source to Gemini
- set the base URL to `https://generativelanguage.googleapis.com/v1beta/openai/`
- replace model names with Gemini model names

This is the fastest path if the goal is to switch providers with minimal code churn.

### Preferred long-term path

For a cleaner provider-native integration, migrate to the official `google-genai` SDK after the first cutover.

Reasons:

- it is Google's recommended SDK
- it exposes Gemini-native features directly
- it avoids depending on compatibility behavior for newer features
- install target: `pip install google-genai`

## Embedding Task-Type Note

The current matching engine compares speaker, event, and course texts symmetrically with cosine similarity. My recommendation is to start with `SEMANTIC_SIMILARITY` for `gemini-embedding-001`.

That is an inference from the current project design, not a direct requirement from the Gemini docs. If we later split the system into query-vs-document retrieval, we should reevaluate task types such as `RETRIEVAL_QUERY` and `RETRIEVAL_DOCUMENT`.

## Official References

- Pricing: https://ai.google.dev/gemini-api/docs/pricing
- Rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
- Deprecations: https://ai.google.dev/gemini-api/docs/deprecations
- Gemini embeddings: https://ai.google.dev/gemini-api/docs/embeddings
- OpenAI compatibility: https://ai.google.dev/gemini-api/docs/openai
- Gemini SDK libraries: https://ai.google.dev/gemini-api/docs/libraries
