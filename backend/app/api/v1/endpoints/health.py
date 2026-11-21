"""Service health endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from redis import Redis

from app.core.config import get_settings
from app.db.session import engine

router = APIRouter()


@router.get("/health", summary="Check API health")
def health_check() -> dict[str, str]:
    """Return a lightweight liveness response without requiring external services."""

    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready", summary="Check service readiness")
def readiness_check() -> dict[str, str]:
    """Verify that the API can reach its required data services."""
    settings = get_settings()
    checks: dict[str, str] = {}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # pragma: no cover - depends on deployment services
        checks["database"] = "unavailable"
        raise HTTPException(status_code=503, detail={"status": "not_ready", "checks": checks}) from exc

    try:
        Redis.from_url(settings.redis_url, socket_connect_timeout=1).ping()
        checks["redis"] = "ok"
    except Exception as exc:  # pragma: no cover - depends on deployment services
        checks["redis"] = "unavailable"
        raise HTTPException(status_code=503, detail={"status": "not_ready", "checks": checks}) from exc

    return {"status": "ready", **checks}
