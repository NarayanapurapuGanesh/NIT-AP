"""
Base interfaces for enterprise services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IService(ABC):
    """Abstract base contract for all injectable domain services."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique service name identifier."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Asynchronous initialization lifecycle hook (lazy model loader readiness)."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean shutdown lifecycle hook."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health status report for service readiness endpoints."""
        pass
