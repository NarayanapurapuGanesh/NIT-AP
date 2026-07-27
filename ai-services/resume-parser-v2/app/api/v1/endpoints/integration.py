"""
Enterprise Integration Platform REST API Endpoints.
Plugins, Webhooks, University Connectors, Import/Export & Plugin Marketplace.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.integration.pipeline.integration_pipeline import IntegrationPipeline
from app.integration.schemas.integration_models import (
    EventType,
    ExportRequest,
    ExportResult,
    ImportRequest,
    ImportResult,
    MarketplaceListing,
    PluginInstance,
    PluginMetadata,
    WebhookSubscription,
)
from app.integration.services.integration_service import IntegrationServiceRegistry
from schemas.base import BaseResponse

router = APIRouter()

integration_pipeline = IntegrationPipeline()
integration_registry = IntegrationServiceRegistry.get_instance()


# --- Plugin Endpoints ---

@router.get(
    "/plugins",
    response_model=BaseResponse[List[PluginInstance]],
    summary="List Installed Plugins",
    description="Returns all installed, active, and disabled plugins.",
)
async def list_plugins() -> BaseResponse[List[PluginInstance]]:
    plugins = integration_pipeline.list_installed_plugins()
    return BaseResponse(success=True, message=f"Retrieved {len(plugins)} installed plugins.", data=plugins)


@router.post(
    "/plugins/install",
    response_model=BaseResponse[PluginInstance],
    summary="Install or Register Plugin",
    description="Installs a new plugin instance after validating version compatibility.",
)
async def install_plugin(metadata: PluginMetadata) -> BaseResponse[PluginInstance]:
    try:
        instance = integration_registry.plugin_manager.install_plugin(metadata)
        return BaseResponse(success=True, message=f"Plugin '{metadata.name}' installed successfully.", data=instance)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- Webhooks Endpoints ---

@router.post(
    "/webhooks",
    response_model=BaseResponse[WebhookSubscription],
    summary="Register Webhook Subscription",
    description="Registers a new target URL endpoint to receive HMAC-signed event webhooks.",
)
async def register_webhook(
    target_url: str,
    events: List[EventType] = Query(...),
    tenant_id: str = Query("default_university"),
) -> BaseResponse[WebhookSubscription]:
    sub = integration_registry.webhook_engine.register_webhook(target_url=target_url, events=events, tenant_id=tenant_id)
    return BaseResponse(success=True, message="Webhook subscription registered successfully.", data=sub)


# --- Connector Endpoints ---

@router.get(
    "/connectors",
    response_model=BaseResponse[Dict[str, Any]],
    summary="List University Connectors",
    description="Returns all active ERP, LMS, Identity, and Notification connector configurations.",
)
async def list_connectors() -> BaseResponse[Dict[str, Any]]:
    connectors = {
        "erp": integration_registry.erp_connector.list_connectors(),
        "lms": integration_registry.lms_connector.list_lms_connectors(),
        "identity": integration_registry.identity_connector.list_identity_connectors(),
        "notifications": integration_registry.notification_connector.list_notification_connectors(),
    }
    return BaseResponse(success=True, message="University connectors retrieved.", data=connectors)


# --- Import / Export Endpoints ---

@router.post(
    "/import",
    response_model=BaseResponse[ImportResult],
    summary="Execute Batch Import",
    description="Imports candidates, jobs, departments, users, or configurations in batch.",
)
async def batch_import(request: ImportRequest) -> BaseResponse[ImportResult]:
    result = integration_registry.import_export_engine.execute_import(request)
    return BaseResponse(success=True, message=f"Import completed ({result.imported_count} imported).", data=result)


@router.post(
    "/export",
    response_model=BaseResponse[ExportResult],
    summary="Execute Batch Export",
    description="Exports analytics reports, interview results, audit logs, or candidates in JSON/CSV format.",
)
async def batch_export(request: ExportRequest) -> BaseResponse[ExportResult]:
    sample_data = [{"id": "101", "name": "Candidate A", "status": "shortlisted"}]
    result = integration_registry.import_export_engine.execute_export(request, sample_data)
    return BaseResponse(success=True, message=f"Export completed ({result.record_count} records).", data=result)


# --- Marketplace Endpoints ---

@router.get(
    "/marketplace",
    response_model=BaseResponse[List[MarketplaceListing]],
    summary="Search Plugin Marketplace",
    description="Returns available plugins from the FacultyIQ marketplace directory.",
)
async def search_marketplace(query: Optional[str] = Query(None)) -> BaseResponse[List[MarketplaceListing]]:
    listings = integration_registry.marketplace_engine.search_marketplace(query=query)
    return BaseResponse(success=True, message=f"Found {len(listings)} marketplace listings.", data=listings)
