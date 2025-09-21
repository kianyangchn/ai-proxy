"""Simple health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
