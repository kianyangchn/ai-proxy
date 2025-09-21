# ai-proxy
This is a Python-based AI proxy. It is deployed on Railway as a gatekeeper for calling LLM models.

1. The API key is managed centrally as Railway variables so users do not need to have an LLM API key to use the services.
2. It exposes an OpenAI-compatible endpoint supporting the [Responses API](https://platform.openai.com/docs/api-reference/responses).
3. Authentication protects the proxy endpoint so only trusted apps can call it.
4. Logging and rate limits can be applied per user at the proxy layer.
5. The proxy can optionally forward user-supplied keys, but defaults to the shared key.

## Getting Started
1. Install Python 3.10+ and [uv](https://docs.astral.sh/uv/).
2. Copy `.env.example` to `.env` and fill in the `AUTH_JWT_*` values.
3. Export your OpenAI key in the shell (for example `export OPENAI_API_KEY=sk-your-key`) or set it as a Railway secret.
4. Install dependencies and create a virtual environment with `uv sync`.
5. Launch the API locally: `uv run uvicorn src.ai_proxy.main:app --reload`.
6. Run tests and lint checks with `uv run pytest` and `uv run ruff check`.

The proxy listens on `http://127.0.0.1:8000/v1/responses` and accepts OpenAI-compatible request bodies. Callers must send an `Authorization: Bearer <jwt>` header signed by your backend and can optionally include `X-OpenAI-API-Key` to forward their own key; otherwise the proxy reads `OPENAI_API_KEY` from the process environment (e.g., macOS shell or Railway variables).
