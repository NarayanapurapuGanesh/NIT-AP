"""
FastAPI Dependency Injection functions.
"""

from core.config import Settings, settings
from app.services.registry import ServiceRegistry, service_registry


def get_settings() -> Settings:
    """Dependency provider for application settings."""
    return settings


def get_service_registry() -> ServiceRegistry:
    """Dependency provider for the global service registry."""
    return service_registry
