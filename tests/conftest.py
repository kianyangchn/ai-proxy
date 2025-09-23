import pytest

from ai_proxy.core.config import clear_settings_cache
from ai_proxy.core.rate_limit import reset_rate_limiter


@pytest.fixture(autouse=True)
def _configure_settings(monkeypatch):
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-secret")
    monkeypatch.setenv("AUTH_JWT_AUDIENCE", "ai-proxy")
    monkeypatch.setenv("AUTH_JWT_ISSUER", "issuer")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("RATE_LIMIT_RPM", "100")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test-model")
    clear_settings_cache()
    reset_rate_limiter()
    yield
    clear_settings_cache()
    reset_rate_limiter()
