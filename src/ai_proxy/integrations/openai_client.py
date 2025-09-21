"""OpenAI HTTP client helpers."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

logger = logging.getLogger("ai_proxy.openai")

_API_BASE_URL = "https://api.openai.com/v1"
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

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if extra_headers:
        headers.update({k: v for k, v in extra_headers.items() if k in _ALLOWED_FORWARD_HEADERS})

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.post(f"{_API_BASE_URL}/responses", json=payload, headers=headers)

    if response.status_code >= 400:
        logger.warning("OpenAI error %s", response.text)
        try:
            detail = response.json()
        except ValueError:
            detail = {"error": response.text}
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()
