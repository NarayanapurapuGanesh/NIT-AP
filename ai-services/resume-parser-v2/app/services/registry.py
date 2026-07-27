"""
Thread-safe Service Registration Framework for Dependency Injection.
"""

import asyncio
from typing import Any, Dict, List, Type, TypeVar
from core.exceptions import ServiceNotFoundError
from core.logging import get_logger
from app.services.base import IService

logger = get_logger("service_registry")

T = TypeVar("T", bound=IService)


class ServiceRegistry:
    """Central container for managing service singletons and lifecycle handlers."""

    def __init__(self) -> None:
        self._services: Dict[str, IService] = {}
        self._lock = asyncio.Lock()

    async def register(self, service: IService) -> None:
        """Registers and initializes a service instance."""
        async with self._lock:
            if service.name in self._services:
                logger.warning("Overwriting existing service", service_name=service.name)
            await service.initialize()
            self._services[service.name] = service
            logger.info("Service registered successfully", service_name=service.name)

    def get(self, name: str) -> IService:
        """Retrieves a registered service by name."""
        if name not in self._services:
            raise ServiceNotFoundError(name)
        return self._services[name]

    def get_by_type(self, service_type: Type[T]) -> T:
        """Retrieves a registered service by class type."""
        for service in self._services.values():
            if isinstance(service, service_type):
                return service  # type: ignore[return-value]
        raise ServiceNotFoundError(service_type.__name__)

    async def shutdown_all(self) -> None:
        """Invokes shutdown lifecycle hook on all registered services."""
        async with self._lock:
            for name, service in self._services.items():
                try:
                    await service.shutdown()
                    logger.info("Service shut down cleanly", service_name=name)
                except Exception as exc:
                    logger.error("Error shutting down service", service_name=name, error=str(exc))
            self._services.clear()

    async def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        """Aggregates health reports across all services."""
        reports: Dict[str, Dict[str, Any]] = {}
        for name, service in self._services.items():
            try:
                reports[name] = await service.health_check()
            except Exception as exc:
                reports[name] = {"status": "unhealthy", "error": str(exc)}
        return reports


# Global Singleton Registry Instance
service_registry = ServiceRegistry()
