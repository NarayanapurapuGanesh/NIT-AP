"""
Pytest integration & unit tests for Phase 16 Enterprise Integration Platform.
Plugin SDK & Lifecycle, Event Bus, Webhook Signing & Dispatch, Connectors (ERP, LMS, Identity, Notifications),
AI Provider Adapters, Import/Export, Marketplace & REST APIs.
"""

import pytest
from httpx import AsyncClient
from app.integration.pipeline.integration_pipeline import IntegrationPipeline
from app.integration.schemas.integration_models import (
    AIProviderType,
    EventType,
    ImportRequest,
    PluginCategory,
    PluginMetadata,
)
from app.integration.services.integration_service import IntegrationServiceRegistry


@pytest.fixture
def integration_pipeline():
    return IntegrationPipeline()


@pytest.fixture
def integration_registry():
    return IntegrationServiceRegistry.get_instance()


@pytest.mark.anyio
async def test_plugin_lifecycle_and_sdk(integration_registry: IntegrationServiceRegistry):
    mgr = integration_registry.plugin_manager
    plugins = mgr.list_plugins()
    assert len(plugins) >= 1

    # Install new plugin
    meta = PluginMetadata(
        plugin_id="test_parser_plugin",
        name="Test Parser Plugin",
        version="1.0.0",
        category=PluginCategory.DOCUMENT_PARSER,
        author="Unit Test",
    )
    inst = mgr.install_plugin(meta)
    assert inst.status.value == "installed"

    # Enable plugin
    enabled_inst = mgr.enable_plugin(inst.instance_id)
    assert enabled_inst.status.value == "enabled"


@pytest.mark.anyio
async def test_event_bus_publish_and_subscribe(integration_registry: IntegrationServiceRegistry):
    bus = integration_registry.event_bus
    received_events = []

    def callback(evt):
        received_events.append(evt)

    bus.subscribe(EventType.CANDIDATE_CREATED, callback)
    published_evt = bus.publish(EventType.CANDIDATE_CREATED, {"candidate_name": "Dr. Alice Smith"})

    assert len(received_events) == 1
    assert received_events[0].event_id == published_evt.event_id


@pytest.mark.anyio
async def test_webhook_signing_and_dispatch(integration_registry: IntegrationServiceRegistry):
    wh = integration_registry.webhook_engine
    sub = wh.register_webhook("https://webhook.site/test", [EventType.MATCHING_COMPLETED])
    assert sub.is_active is True

    # Dispatch event
    bus = integration_registry.event_bus
    bus.publish(EventType.MATCHING_COMPLETED, {"match_score": 92.4})

    logs = wh.get_delivery_logs(sub.subscription_id)
    assert len(logs) > 0
    assert logs[0].success is True


@pytest.mark.anyio
async def test_ai_provider_adapters(integration_pipeline: IntegrationPipeline):
    # Ollama Adapter
    ollama_res = integration_pipeline.generate_ai_completion(AIProviderType.OLLAMA, "llama3:8b", "Analyze resume")
    assert "[Ollama response" in ollama_res

    # OpenAI Adapter
    openai_res = integration_pipeline.generate_ai_completion(AIProviderType.OPENAI, "gpt-4o", "Analyze resume")
    assert "[OpenAI response" in openai_res


@pytest.mark.anyio
async def test_university_connectors(integration_registry: IntegrationServiceRegistry):
    erp_res = integration_registry.erp_connector.sync_faculty_records("SAP")
    assert erp_res["status"] == "success"

    lms_res = integration_registry.lms_connector.fetch_teaching_history("faculty@nitandhra.ac.in", "Moodle")
    assert lms_res["lms"] == "Moodle"

    sso_res = integration_registry.identity_connector.authenticate_sso("AzureAD", "valid_token")
    assert sso_res["authenticated"] is True


@pytest.mark.anyio
async def test_integration_api_plugins(async_client: AsyncClient):
    res = await async_client.get("/api/v1/plugins")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1


@pytest.mark.anyio
async def test_integration_api_connectors(async_client: AsyncClient):
    res = await async_client.get("/api/v1/connectors")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "erp" in data["data"]
    assert "lms" in data["data"]


@pytest.mark.anyio
async def test_integration_api_marketplace(async_client: AsyncClient):
    res = await async_client.get("/api/v1/marketplace")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
