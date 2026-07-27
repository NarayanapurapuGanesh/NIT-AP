"""
Version info endpoint.
"""

from typing import Any, Dict
from fastapi import APIRouter
from schemas.base import BaseResponse
from core.constants import API_DESCRIPTION, API_TITLE, API_VERSION

router = APIRouter()


@router.get("/version", response_model=BaseResponse[Dict[str, Any]], summary="API Version Information")
async def version_info() -> BaseResponse[Dict[str, Any]]:
    """Returns application title, description, and semantic versioning details."""
    return BaseResponse(
        success=True,
        message="Version metadata retrieved successfully.",
        data={
            "title": API_TITLE,
            "version": API_VERSION,
            "description": API_DESCRIPTION,
        },
    )
