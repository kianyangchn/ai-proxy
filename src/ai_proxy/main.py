"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.config import get_settings
from .routes import health, responses

logger = logging.getLogger("ai_proxy")


@asynccontextmanager
async def lifespan(_app: FastAPI):  # pragma: no cover - log side effect only
    settings = get_settings()
    logger.info("AI Proxy ready", extra={"rate_limit_rpm": settings.rate_limit_rpm})
    yield


def create_application() -> FastAPI:
    app = FastAPI(
        title="AI Proxy",
        description="Gateway service that proxies OpenAI's Responses API.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(health.router)
    app.include_router(responses.router)

    return app


app = create_application()
