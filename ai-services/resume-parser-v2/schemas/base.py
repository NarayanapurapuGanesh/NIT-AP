"""
Pydantic Base Schemas for Application DTOs and Contracts.
"""

from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Standardized top-level API response envelope."""

    model_config = ConfigDict(frozen=True)

    success: bool = Field(default=True, description="Operation outcome status")
    data: Optional[T] = Field(default=None, description="Payload data")
    message: str = Field(default="Operation completed successfully.", description="Status message")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp"
    )
