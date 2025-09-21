"""Routes that proxy OpenAI's Responses API."""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from ..core.auth import AuthContext, authenticate_request
from ..core.config import Settings, get_settings
from ..core.rate_limit import get_rate_limiter
from ..integrations.openai_client import forward_response_request

logger = logging.getLogger("ai_proxy.routes.responses")

router = APIRouter(prefix="/v1", tags=["responses"])


@router.post("/responses")
async def proxy_responses_endpoint(
    request: Request,
    auth: AuthContext = Depends(authenticate_request),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    payload: Dict[str, Any] = await request.json()
    client_id = auth.client_id
    user_api_key = request.headers.get("X-OpenAI-API-Key")
    effective_api_key = user_api_key or settings.openai_api_key

    limiter = get_rate_limiter(settings.rate_limit_rpm)
    await limiter.hit(client_id)

    logger.info(
        "Forwarding responses request",
        extra={"client_id": client_id, "model": payload.get("model")},
    )

    allowed_header_subset = {
        key: value
        for key, value in request.headers.items()
        if key in {"OpenAI-Beta", "OpenAI-Organization"}
    }

    upstream_response = await forward_response_request(
        payload=payload,
        api_key=effective_api_key,
        timeout_seconds=settings.request_timeout_seconds,
        extra_headers=allowed_header_subset,
    )

    return JSONResponse(content=upstream_response)
