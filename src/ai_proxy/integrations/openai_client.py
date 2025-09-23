"""OpenAI client helpers built on the official SDK."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from openai import APIStatusError, AsyncOpenAI, OpenAIError

logger = logging.getLogger("ai_proxy.openai")

_ALLOWED_FORWARD_HEADERS = {"OpenAI-Beta", "OpenAI-Organization"}


async def forward_response_request(
    payload: Dict[str, Any],
    api_key: str,
    *,
    timeout_seconds: float,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Forward the Responses API payload to OpenAI and return the JSON body."""

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OpenAI key missing"
        )

    allowed_headers = (
        {k: v for k, v in extra_headers.items() if k in _ALLOWED_FORWARD_HEADERS}
        if extra_headers
        else None
    )

    client = AsyncOpenAI(api_key=api_key)

    try:
        response = await client.responses.create(
            **payload,
            extra_headers=allowed_headers,
            timeout=timeout_seconds,
        )
    except APIStatusError as exc:
        logger.warning("OpenAI API error %s", exc.message)
        detail: Any = exc.message
        if exc.response is not None:
            try:
                body_bytes = await exc.response.aread()
                detail = json.loads(body_bytes.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                detail = {"error": exc.message}
        raise HTTPException(status_code=exc.status_code, detail=detail) from exc
    except OpenAIError as exc:  # pragma: no cover - rare SDK errors
        logger.exception("Unexpected OpenAI client error")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected OpenAI client error",
        ) from exc

    return response.model_dump()
