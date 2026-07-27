"""
Integration Service Registry.
Singleton access to all Enterprise Integration Platform engines.
"""

from typing import Optional
from app.integration.adapters.ai_adapters import AIAdapterFactory
from app.integration.connectors.erp.erp_connector import UniversityERPConnectorEngine
from app.integration.connectors.identity.identity_connector import IdentityConnectorEngine
from app.integration.connectors.lms.lms_connector import LMSConnectorEngine
from app.integration.connectors.notifications.notification_connector import NotificationConnectorEngine
from app.integration.events.event_bus import EventBusEngine
from app.integration.gateway.api_gateway import APIGatewayEngine
from app.integration.import_export.import_export_engine import ImportExportEngine
from app.integration.marketplace.marketplace_engine import MarketplaceEngine
from app.integration.plugins.plugin_manager import PluginManagerEngine
from app.integration.webhooks.webhook_engine import WebhookEngine
from core.logging import get_logger

logger = get_logger("integration_service")


class IntegrationServiceRegistry:
    """Central Integration Service Registry Singleton."""

    _instance: Optional["IntegrationServiceRegistry"] = None

    def __init__(self) -> None:
        self.gateway_engine = APIGatewayEngine()
        self.plugin_manager = PluginManagerEngine()
        self.event_bus = EventBusEngine()
        self.webhook_engine = WebhookEngine()
        self.erp_connector = UniversityERPConnectorEngine()
        self.lms_connector = LMSConnectorEngine()
        self.identity_connector = IdentityConnectorEngine()
        self.notification_connector = NotificationConnectorEngine()
        self.import_export_engine = ImportExportEngine()
        self.marketplace_engine = MarketplaceEngine()
        self.ai_factory = AIAdapterFactory()

    @classmethod
    def get_instance(cls) -> "IntegrationServiceRegistry":
        if cls._instance is None:
            cls._instance = IntegrationServiceRegistry()
        return cls._instance
