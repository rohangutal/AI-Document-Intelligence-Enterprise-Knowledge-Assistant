"""Top-level API router."""

from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.legal import router as legal_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.contracts import router as contracts_router
from app.api.v1.endpoints.reviews import router as reviews_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(legal_router)
api_router.include_router(auth_router)
api_router.include_router(contracts_router)
api_router.include_router(reviews_router)
