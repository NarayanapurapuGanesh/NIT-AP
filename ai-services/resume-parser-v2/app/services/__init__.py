"""
Services Package.
"""

from app.services.base import IService
from app.services.registry import ServiceRegistry, service_registry

__all__ = ["IService", "ServiceRegistry", "service_registry"]
