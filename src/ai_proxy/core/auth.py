"""Authentication helpers for the proxy."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Annotated, Optional

import jwt
from fastapi import Depends, Header, HTTPException, Request, status

from .config import Settings, get_settings


@dataclass(slots=True)
class AuthContext:
    """Details about the authenticated caller."""

    subject: str
    issued_at: Optional[dt.datetime]
    expires_at: Optional[dt.datetime]

    @property
    def client_id(self) -> str:
        return self.subject


def _decode_authorization_header(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header"
        )

    scheme, _, token = authorization.partition(" ")
    if not token or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header"
        )

    return token


async def authenticate_request(
    _: Request,
    authorization: Annotated[Optional[str], Header(alias="Authorization")] = None,
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    """Validate the caller-provided JWT and return the decoded context."""

    if not settings.auth_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication secret not configured",
        )

    token = _decode_authorization_header(authorization)

    options = {"require": ["exp", "iat", "sub"]}
    try:
        payload = jwt.decode(
            token,
            settings.auth_jwt_secret,
            algorithms=[settings.auth_jwt_algorithm],
            audience=settings.auth_jwt_audience,
            issuer=settings.auth_jwt_issuer,
            options=options,
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        ) from exc
    except jwt.InvalidTokenError as exc:  # pragma: no cover - grouping
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject"
        )

    issued_at = _to_datetime(payload.get("iat"))
    expires_at = _to_datetime(payload.get("exp"))

    return AuthContext(subject=subject, issued_at=issued_at, expires_at=expires_at)


def _to_datetime(value: Optional[int]) -> Optional[dt.datetime]:
    if value is None:
        return None
    return dt.datetime.fromtimestamp(value, tz=dt.timezone.utc)
