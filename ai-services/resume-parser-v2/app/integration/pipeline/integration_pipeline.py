"""
Integration Pipeline Orchestrator.
Orchestrates events, webhooks, plugin execution, AI completions, and university connectors.
"""

from typing import Any, Dict, List, Optional
from app.integration.schemas.integration_models import (
    AIAdapterConfig,
    AIProviderType,
    EventEnvelope,
    EventType,
    ExportRequest,
    ExportResult,
    ImportRequest,
    ImportResult,
    PluginInstance,
)
from app.integration.services.integration_service import IntegrationServiceRegistry
from core.logging import get_logger

logger = get_logger("integration_pipeline")


class IntegrationPipeline:
    """Enterprise Integration Pipeline Facade."""

    def __init__(self) -> None:
        self.registry = IntegrationServiceRegistry.get_instance()
        self._setup_event_hooks()

    def _setup_event_hooks(self) -> None:
        """Subscribes webhook engine to all event bus topics."""
        def webhook_dispatcher(event: EventEnvelope) -> None:
            self.registry.webhook_engine.dispatch_event(event)

        for event_type in EventType:
            self.registry.event_bus.subscribe(event_type, webhook_dispatcher)

    def publish_system_event(self, event_type: EventType, payload: Dict[str, Any]) -> EventEnvelope:
        return self.registry.event_bus.publish(event_type, payload)

    def generate_ai_completion(self, provider_type: AIProviderType, model_name: str, prompt: str) -> str:
        config = AIAdapterConfig(provider_type=provider_type, api_base="http://localhost:11434", model_name=model_name)
        adapter = self.registry.ai_factory.create_adapter(config)
        return adapter.generate_completion(prompt)

    def list_installed_plugins(self) -> List[PluginInstance]:
        return self.registry.plugin_manager.list_plugins()
