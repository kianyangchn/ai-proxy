from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from ai_proxy.main import app

SECRET = "test-secret"
AUDIENCE = "ai-proxy"
ISSUER = "issuer"


def _build_token(sub: str = "suite") -> str:
    now = datetime.now(tz=timezone.utc)
    claims = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
        "aud": AUDIENCE,
        "iss": ISSUER,
    }
    return jwt.encode(claims, SECRET, algorithm="HS256")


@pytest.mark.asyncio
async def test_proxy_requires_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/v1/responses", json={"model": "gpt-test"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_proxy_forwards_payload():
    mocked_upstream = AsyncMock(return_value={"id": "resp_123", "output": []})

    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {_build_token()}", "X-Client-Id": "ignored"}
    with patch("ai_proxy.routes.responses.forward_response_request", new=mocked_upstream):
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/v1/responses",
                headers=headers,
                json={"model": "gpt", "input": [{"role": "user", "content": "hi"}]},
            )

    assert response.status_code == 200
    assert response.json()["id"] == "resp_123"
    mocked_upstream.assert_awaited_once()
    _, kwargs = mocked_upstream.call_args
    assert kwargs["payload"]["model"] == "gpt"
    assert kwargs["api_key"] == "test-openai-key"
