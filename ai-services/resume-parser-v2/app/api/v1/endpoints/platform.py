"""
Enterprise Platform Operations REST API Endpoints.
Health monitoring, Prometheus metrics, Diagnostics reports, Platform status, Alerts, and Cache stats.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Response, status
from app.platform.pipeline.platform_pipeline import PlatformPipeline
from app.platform.schemas.platform_models import (
    AlertEvent,
    CacheStats,
    DiagnosticsReport,
    PlatformHealthReport,
)
from app.platform.services.platform_service import PlatformServiceRegistry
from schemas.base import BaseResponse

router = APIRouter()

platform_pipeline = PlatformPipeline()
platform_registry = PlatformServiceRegistry.get_instance()


@router.get(
    "/platform/health",
    response_model=BaseResponse[PlatformHealthReport],
    summary="Get Platform Health Report",
    description="Returns aggregate health report across all platform dependencies (DB, Redis, Ollama, Storage, Queue, Workers).",
)
async def get_health() -> BaseResponse[PlatformHealthReport]:
    report = platform_pipeline.get_health_report()
    return BaseResponse(success=True, message=f"Platform health status: {report.overall_status.value}", data=report)


@router.get(
    "/platform/metrics",
    summary="Scrape Prometheus Metrics",
    description="Returns live application and system metrics formatted in Prometheus text exposition standard.",
)
async def get_metrics() -> Response:
    metrics_text = platform_pipeline.get_prometheus_metrics()
    return Response(content=metrics_text, media_type="text/plain; version=0.0.4")


@router.get(
    "/platform/diagnostics",
    response_model=BaseResponse[DiagnosticsReport],
    summary="Get Platform Diagnostics",
    description="Returns complete diagnostic snapshot including health, metrics, cache, performance profiles, circuit breakers, and OWASP audit.",
)
async def get_diagnostics() -> BaseResponse[DiagnosticsReport]:
    report = platform_pipeline.get_diagnostics_report()
    return BaseResponse(success=True, message="Platform diagnostics report generated.", data=report)


@router.get(
    "/platform/status",
    response_model=BaseResponse[Dict[str, Any]],
    summary="Get Platform Status Summary",
    description="Returns overall system status, uptime, version, and live monitoring dashboard parameters.",
)
async def get_status() -> BaseResponse[Dict[str, Any]]:
    summary = platform_pipeline.get_status_summary()
    return BaseResponse(success=True, message="Platform status OK.", data=summary)


@router.get(
    "/platform/alerts",
    response_model=BaseResponse[List[AlertEvent]],
    summary="Get Active & Historical Alerts",
    description="Returns recent alert events fired by metric evaluation rules.",
)
async def get_alerts() -> BaseResponse[List[AlertEvent]]:
    alerts = platform_registry.alert_engine.get_alert_history()
    return BaseResponse(success=True, message=f"Retrieved {len(alerts)} alert events.", data=alerts)


@router.get(
    "/platform/cache/stats",
    response_model=BaseResponse[CacheStats],
    summary="Get Cache Performance Statistics",
    description="Returns in-memory cache statistics (hit ratio, total entries, evictions, memory usage).",
)
async def get_cache_stats() -> BaseResponse[CacheStats]:
    stats = platform_registry.cache_engine.get_stats()
    return BaseResponse(success=True, message="Cache stats retrieved.", data=stats)
