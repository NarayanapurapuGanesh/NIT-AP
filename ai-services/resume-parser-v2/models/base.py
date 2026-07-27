"""
Domain Models Base Interface.
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class BaseModelEntity(ABC):
    """Base domain entity with unique identifier and lifecycle timestamps."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
