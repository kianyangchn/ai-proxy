from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from ai_proxy.assets.prompts import SYSTEM_INSTRUCTIONS
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
        response = await client.post("/v1/menu", json={"texts": ["Hello world"], "lang_out": "en"})

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
                json={
                    "texts": ["Intro text", "Another insight"],
                    "lang_in": "zh-Hans",
                    "lang_out": "en",
                },
            )

    assert response.status_code == 200
    assert response.json()["id"] == "resp_123"
    mocked_upstream.assert_awaited_once()
    _, kwargs = mocked_upstream.call_args
    called_payload = kwargs["payload"]
    assert called_payload["model"] == "gpt-test-model"
    assert called_payload["instructions"] == SYSTEM_INSTRUCTIONS
    user_prompt = called_payload["input"]
    assert "Input language: zh-Hans" in user_prompt
    assert "Output language: en" in user_prompt
    assert "Menu text 1" in user_prompt and "Intro text" in user_prompt
    assert "Menu text 2" in user_prompt and "Another insight" in user_prompt
    assert called_payload["response_format"]["type"] == "json_schema"
    schema_props = called_payload["response_format"]["json_schema"]["schema"]["items"]["properties"]
    assert set(schema_props.keys()) == {"original_name", "translated_name", "description"}
    assert called_payload["reasoning"] == {"effort": "minimal"}
    assert called_payload["text"] == {"verbosity": "low"}
    assert kwargs["api_key"] == "test-openai-key"


@pytest.mark.asyncio
async def test_menu_rejects_empty_texts():
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {_build_token()}"}
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/v1/menu",
            headers=headers,
            json={"texts": [""], "lang_out": "en"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_menu_requires_output_language():
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {_build_token()}"}
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/v1/menu",
            headers=headers,
            json={"texts": ["Menu item"], "lang_out": "   "},
        )

    assert response.status_code == 422
