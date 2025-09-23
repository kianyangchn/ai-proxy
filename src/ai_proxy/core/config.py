"""Application configuration helpers."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven configuration values."""

    openai_api_key: Optional[str] = None
    auth_jwt_secret: Optional[str] = None
    auth_jwt_audience: Optional[str] = None
    auth_jwt_issuer: Optional[str] = None
    auth_jwt_algorithm: str = "HS256"
    rate_limit_rpm: int = 60
    openai_model: str = "gpt-4.1-mini"
    request_timeout_seconds: float = 120.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


def clear_settings_cache() -> None:
    """Reset cached settings (mainly for tests)."""

    get_settings.cache_clear()
