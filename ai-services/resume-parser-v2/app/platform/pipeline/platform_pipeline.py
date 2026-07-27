"""
Platform Operations Pipeline Orchestrator.
Orchestrates health monitoring, metric exports, diagnostics generation, and platform status reports.
"""

from typing import Any, Dict
from app.platform.schemas.platform_models import DiagnosticsReport, PlatformHealthReport
from app.platform.services.platform_service import PlatformServiceRegistry
from core.logging import get_logger

logger = get_logger("platform_pipeline")


class PlatformPipeline:
    """Enterprise Platform Operations Pipeline."""

    def __init__(self) -> None:
        self.registry = PlatformServiceRegistry.get_instance()

    def get_health_report(self) -> PlatformHealthReport:
        return self.registry.health_engine.run_all_checks()

    def get_prometheus_metrics(self) -> str:
        return self.registry.metrics_engine.export_prometheus_format()

    def get_diagnostics_report(self) -> DiagnosticsReport:
        return self.registry.diagnostics_engine.generate_diagnostics_report()

    def get_status_summary(self) -> Dict[str, Any]:
        health = self.get_health_report()
        dashboard = self.registry.monitoring_engine.get_live_dashboard_data()
        return {
            "status": health.overall_status.value,
            "uptime_seconds": health.uptime_seconds,
            "version": "2.0.0",
            "active_alerts_count": len(self.registry.alert_engine.get_alert_history()),
            "dashboard_summary": dashboard,
        }
