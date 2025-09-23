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
async def test_menu_requires_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/v1/menu", json={"texts": ["Hello world"]})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_menu_forwards_payload():
    mocked_upstream = AsyncMock(return_value={"id": "resp_123", "output": []})

    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {_build_token()}", "X-Client-Id": "ignored"}
    with patch("ai_proxy.routes.menu.forward_response_request", new=mocked_upstream):
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/v1/menu",
                headers=headers,
                json={"texts": ["Intro text", "Another insight"]},
            )

    assert response.status_code == 200
    assert response.json()["id"] == "resp_123"
    mocked_upstream.assert_awaited_once()
    _, kwargs = mocked_upstream.call_args
    called_payload = kwargs["payload"]
    assert called_payload["model"] == "gpt-test-model"
    system_message = called_payload["input"][0]["content"][0]["text"]
    assert "JSON" in system_message
    user_message = called_payload["input"][1]["content"][0]["text"]
    assert "Menu text 1" in user_message and "Intro text" in user_message
    assert "Menu text 2" in user_message and "Another insight" in user_message
    assert called_payload["response_format"]["type"] == "json_schema"
    assert kwargs["api_key"] == "test-openai-key"


@pytest.mark.asyncio
async def test_menu_rejects_empty_texts():
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {_build_token()}"}
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/v1/menu",
            headers=headers,
            json={"texts": [""]},
        )

    assert response.status_code == 422
