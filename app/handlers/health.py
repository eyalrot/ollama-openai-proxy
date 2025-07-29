"""Health check endpoint handler."""

from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    environment: str
    timestamp: str


# Create router for health endpoints
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> Dict[str, Any]:
    """Health check endpoint.

    Returns:
        Health status with version and environment information.
    """
    response = {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    logger.debug("health_check_requested", response=response)

    return response
