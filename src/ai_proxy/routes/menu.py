"""Routes that convert OCR menu text into structured menu JSON."""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from ..assets.prompts import (
    RESPONSE_JSON_SCHEMA,
    SYSTEM_INSTRUCTIONS,
    build_user_prompt,
)
from ..core.auth import AuthContext, authenticate_request
from ..core.config import Settings, get_settings
from ..core.rate_limit import get_rate_limiter
from ..integrations.openai_client import forward_response_request

logger = logging.getLogger("ai_proxy.routes.menu")

router = APIRouter(prefix="/v1", tags=["menu"])


class MenuExtractionPayload(BaseModel):
    """Validated payload containing OCR-derived menu text snippets."""

    texts: list[str] = Field(..., description="Text snippets that require analysis.")

    @field_validator("texts", mode="after")
    @classmethod
    def _validate_texts(cls, texts: list[str]) -> list[str]:
        cleaned = [text.strip() for text in texts if text and text.strip()]
        if not cleaned:
            raise ValueError("texts must include at least one non-empty entry")
        return cleaned


@router.post("/menu", summary="Convert menu text snippets into structured JSON items")
async def generate_menu(
    menu_payload: MenuExtractionPayload,
    request: Request,
    auth: AuthContext = Depends(authenticate_request),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    client_id = auth.client_id
    user_api_key = request.headers.get("X-OpenAI-API-Key")
    effective_api_key = user_api_key or settings.openai_api_key

    limiter = get_rate_limiter(settings.rate_limit_rpm)
    await limiter.hit(client_id)

    logger.info("Generating menu", extra={"client_id": client_id, "model": settings.openai_model})

    allowed_header_subset = {
        key: value
        for key, value in request.headers.items()
        if key in {"OpenAI-Beta", "OpenAI-Organization"}
    }

    payload: Dict[str, Any] = {
        "model": settings.openai_model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "text", "text": SYSTEM_INSTRUCTIONS}],
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": build_user_prompt(menu_payload.texts)}],
            },
        ],
        "response_format": RESPONSE_JSON_SCHEMA,
    }

    upstream_response = await forward_response_request(
        payload=payload,
        api_key=effective_api_key,
        timeout_seconds=settings.request_timeout_seconds,
        extra_headers=allowed_header_subset,
    )

    return JSONResponse(content=upstream_response)
