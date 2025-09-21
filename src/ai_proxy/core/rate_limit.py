"""Simple in-memory rate limiting for per-client control."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, status


class RateLimiter:
    """Token-bucket style limiter that tracks requests per minute per client."""

    def __init__(self, requests_per_minute: int) -> None:
        self.requests_per_minute = requests_per_minute
        self._history: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def hit(self, client_id: str) -> None:
        """Record a call for the given client, raising if over limit."""

        if self.requests_per_minute <= 0:
            return

        now = time.monotonic()
        window_start = now - 60

        async with self._lock:
            bucket = self._history[client_id]
            while bucket and bucket[0] < window_start:
                bucket.popleft()

            if len(bucket) >= self.requests_per_minute:
                retry_after = max(0.0, 60 - (now - bucket[0]))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": f"{retry_after:.0f}"},
                )

            bucket.append(now)


_rate_limiter: RateLimiter | None = None


def get_rate_limiter(requests_per_minute: int) -> RateLimiter:
    """Return a shared limiter keyed by configuration value."""

    global _rate_limiter
    if _rate_limiter is None or _rate_limiter.requests_per_minute != requests_per_minute:
        _rate_limiter = RateLimiter(requests_per_minute)
    return _rate_limiter


def reset_rate_limiter() -> None:
    """Clear the global limiter (mainly for tests)."""

    global _rate_limiter
    _rate_limiter = None
