"""
Validators Interface Package.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IValidator(ABC):
    """Abstract interface for schema and domain data verification."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def validate(self, payload: Dict[str, Any]) -> bool:
        """Validates payload against domain rules and schema specifications."""
        pass
