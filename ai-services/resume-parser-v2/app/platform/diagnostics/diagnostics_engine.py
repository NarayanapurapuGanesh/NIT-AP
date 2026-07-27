"""
Diagnostics Engine.
Aggregates health reports, metrics snapshots, cache stats, performance profiles,
circuit breaker states, and OWASP security audit records into a master diagnostic report.
"""

from app.platform.caching.cache_engine import CachingEngine
from app.platform.health.health_engine import HealthCheckEngine
from app.platform.metrics.metrics_engine import MetricsCollectionEngine
from app.platform.performance.performance_engine import PerformanceOptimizationEngine
from app.platform.resilience.resilience_engine import ResilienceEngine
from app.platform.schemas.platform_models import DiagnosticsReport
from app.platform.security.security_hardening import SecurityHardeningEngine
from core.logging import get_logger

logger = get_logger("diagnostics_engine")


class DiagnosticsEngine:
    """Enterprise Platform Diagnostics Engine."""

    def __init__(
        self,
        health_engine: HealthCheckEngine,
        metrics_engine: MetricsCollectionEngine,
        cache_engine: CachingEngine,
        performance_engine: PerformanceOptimizationEngine,
        resilience_engine: ResilienceEngine,
        security_engine: SecurityHardeningEngine,
    ) -> None:
        self.health_engine = health_engine
        self.metrics_engine = metrics_engine
        self.cache_engine = cache_engine
        self.performance_engine = performance_engine
        self.resilience_engine = resilience_engine
        self.security_engine = security_engine

    def generate_diagnostics_report(self) -> DiagnosticsReport:
        health = self.health_engine.run_all_checks()
        metrics = self.metrics_engine.collect_snapshot()
        cache_stats = self.cache_engine.get_stats()
        perf_profiles = self.performance_engine.get_all_profiles()
        cbs = self.resilience_engine.list_circuit_breakers()
        sec_checks = self.security_engine.run_owasp_audit()

        report = DiagnosticsReport(
            health=health,
            metrics=metrics,
            cache_stats=cache_stats,
            performance_profiles=perf_profiles,
            circuit_breakers=cbs,
            security_checks=sec_checks,
        )

        logger.info("Diagnostics report generated successfully", report_id=report.report_id)
        return report
