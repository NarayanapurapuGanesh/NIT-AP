"""
Readiness probe endpoint checking registered downstream dependencies.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from schemas.base import BaseResponse
from app.dependencies.config import get_service_registry
from app.services.registry import ServiceRegistry

router = APIRouter()


@router.get("/readiness", response_model=BaseResponse[Dict[str, Any]], summary="Readiness Probe")
async def readiness_check(
    registry: ServiceRegistry = Depends(get_service_registry),
) -> BaseResponse[Dict[str, Any]]:
    """Checks service registry state and downstream component status for traffic routing."""
    services_health = await registry.get_all_health()
    all_healthy = all(s.get("status") == "healthy" for s in services_health.values()) if services_health else True

    return BaseResponse(
        success=all_healthy,
        message="System readiness evaluation completed.",
        data={
            "ready": all_healthy,
            "registered_services": len(services_health),
            "services": services_health,
        },
    )
