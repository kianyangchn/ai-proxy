# Repository Guidelines

## Project Layout
Application code resides in `src/ai_proxy/`. Group HTTP interfaces in `routes/`, adapters to external services in `integrations/`, and shared auth, rate-limit, or logging helpers in `core/`. Persist prompt templates or static payloads under `assets/`. Tests mirror this layout in `tests/` (for example, `tests/routes/test_responses.py`). Deployment artifacts such as Railway manifests, Dockerfiles, or Fly scripts belong in `deploy/`. Track required environment variables in `.env.example` with short inline notes.

## Setup & Everyday Commands
Use [uv](https://docs.astral.sh/uv/) to manage the toolchain. `uv sync` creates `.venv/` and installs dependencies from `pyproject.toml`/`uv.lock`. Run commands through the managed environment: `uv run uvicorn src.ai_proxy.main:app --reload` for local dev, `uv run ruff check src --fix` followed by `uv run ruff format` for lint+format, and `uv run pytest -q` for fast verification. Refresh pinned versions with `uv lock --upgrade` and commit the updated lockfile when dependency changes ship.

## Style & Naming
Follow PEP 8 with 4-space indentation, comprehensive type hints on public functions, and descriptive snake_case identifiers. Keep modules single-purpose (`rate_limit.py`, `auth_backend.py`). Prefer Pydantic models or dataclasses to document request/response schemas near the route that uses them. Docstrings should follow Google style and explain inputs, side effects, and return values succinctly. Run `uv run ruff format` before submitting changes.

## Testing Expectations
Author pytest suites alongside features, naming files `test_<area>.py`. Store reusable fixtures in `tests/conftest.py` and mock outbound OpenAI calls to keep tests deterministic. For authentication, throttling, or billing paths, extend coverage and target >85% overall using `uv run pytest --cov=src/ai_proxy --cov-report=term-missing`. Place slower or contract tests in `tests/integration/` and tag them with `@pytest.mark.integration` so CI can gate them.

## Git & PR Workflow
Create a feature branch before implementing changes: `git checkout -b feature/<summary>` from up-to-date `main`. Commit in small, logical steps using Conventional Commit prefixes (`feat`, `fix`, `docs`, `chore`) and imperative messages. Push branches to origin (`git push -u origin feature/<summary>`) and open a pull request that outlines intent, risk, validation (`uv run pytest`), and any configuration updates. Reference tickets or design docs, include curl examples when APIs change, and request peer review prior to merge.
