# Repository Guidelines

## Project Structure & Module Organization
Service code lives under `src/ai_proxy/`; keep FastAPI routers in `src/ai_proxy/routes/`, outbound adapters in `src/ai_proxy/integrations/`, and shared logic (auth, rate limiting, logging) in `src/ai_proxy/core/`. Persist prompt templates or static fixtures in `src/ai_proxy/assets/`. Tests mirror the package layout inside `tests/` (for example `tests/routes/test_responses.py`). Deployment collateral such as Railway manifests, Docker assets, or Fly.io configs belong in `deploy/`. Place sample configuration in `.env.example` and document required environment variables inline.

## Build, Test, and Development Commands
Use [uv](https://docs.astral.sh/uv/) for environment management. Bootstrap dependencies with `uv sync` (reads `pyproject.toml` and creates an isolated `.venv/`). Run ad-hoc commands through `uv run` so the managed environment is always active:
- `uv run uvicorn src.ai_proxy.main:app --reload` – start the API with live reload
- `uv run ruff check src --fix` then `uv run ruff format` – lint and format
- `uv run pytest -q` – execute the test suite
- `uv lock --upgrade` – refresh dependency pins when updating libraries
Commit the generated `.venv/` hash files (`uv.lock`) but keep the actual virtual environment out of version control.

## Coding Style & Naming Conventions
Stick to PEP 8 with 4-space indentation, type hints on public surfaces, and expressive `snake_case` identifiers. Module names should be narrow and purpose-driven (`rate_limit.py`, `auth_backend.py`). Prefer dataclasses or Pydantic models for request/response contracts and keep schema definitions adjacent to the route that serves them. Docstrings follow Google style, focusing on parameters and return types. Run `uv run ruff format` before opening a PR to ensure consistent styling.

## Testing Guidelines
Write pytest modules named `test_<area>.py`; colocate fixtures in `tests/conftest.py` and mock outbound OpenAI traffic so suites stay deterministic. For features that touch authentication, throttling, or quota tracking, add regression tests and aim for >85% coverage using `uv run pytest --cov=src/ai_proxy --cov-report=term-missing`. Store slower integration or contract tests in `tests/integration/` and tag them with `@pytest.mark.integration` to allow CI selectors.

## Commit & Pull Request Guidelines
Adopt Conventional Commit prefixes (`feat`, `fix`, `chore`, `docs`) and imperative summaries (`feat: add responses proxy route`). Reference related issues or tickets in the body, explicitly note environment or schema changes, and include curl samples when behavior shifts. Pull requests should describe intent, risk, and validation (`uv run pytest`) and link to docs or diagrams when architecture evolves. Request peer review prior to merging, even for operations-focused updates.
