"""
Monitoring Engine.
Provides live metrics aggregation, dependency monitoring, and dashboard data for Grafana integration.
"""

from typing import Any, Dict
from app.platform.health.health_engine import HealthCheckEngine
from app.platform.metrics.metrics_engine import MetricsCollectionEngine
from app.platform.schemas.platform_models import PlatformHealthReport, MetricsSnapshot
from core.logging import get_logger

logger = get_logger("monitoring_engine")


class MonitoringEngine:
    """Enterprise Monitoring & Dashboard Data Provider."""

    def __init__(self) -> None:
        self.health_engine = HealthCheckEngine()
        self.metrics_engine = MetricsCollectionEngine()

    def get_live_dashboard_data(self) -> Dict[str, Any]:
        health_report = self.health_engine.run_all_checks()
        metrics_snapshot = self.metrics_engine.collect_snapshot()

        dashboard = {
            "overall_health": health_report.overall_status.value,
            "uptime_seconds": health_report.uptime_seconds,
            "dependency_count": len(health_report.checks),
            "healthy_dependencies": sum(1 for c in health_report.checks if c.status.value == "healthy"),
            "metric_count": len(metrics_snapshot.metrics),
            "key_metrics": {m.name: m.value for m in metrics_snapshot.metrics[:10]},
        }

        logger.debug("Live dashboard data assembled")
        return dashboard

    def get_health_report(self) -> PlatformHealthReport:
        return self.health_engine.run_all_checks()

    def get_metrics_snapshot(self) -> MetricsSnapshot:
        return self.metrics_engine.collect_snapshot()
