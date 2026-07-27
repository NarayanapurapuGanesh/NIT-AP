"""
Health check endpoint.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from schemas.base import BaseResponse
from app.dependencies.config import get_settings
from core.config import Settings

router = APIRouter()


@router.get("/health", response_model=BaseResponse[Dict[str, Any]], summary="Liveness Probe")
async def health_check(settings: Settings = Depends(get_settings)) -> BaseResponse[Dict[str, Any]]:
    """Returns application health status and current execution environment."""
    return BaseResponse(
        success=True,
        message="System is operational.",
        data={
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "environment": settings.APP_ENV.value,
            "debug": settings.DEBUG,
        },
    )
