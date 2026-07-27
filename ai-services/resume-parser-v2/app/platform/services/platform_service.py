"""
Platform Service Registry.
Singleton access to all Enterprise Production Hardening Platform engines.
"""

from typing import Optional
from app.platform.alerts.alert_engine import AlertEngine
from app.platform.backup.backup_engine import BackupEngine
from app.platform.caching.cache_engine import CachingEngine
from app.platform.diagnostics.diagnostics_engine import DiagnosticsEngine
from app.platform.health.health_engine import HealthCheckEngine
from app.platform.logging.logging_engine import StructuredLoggingEngine
from app.platform.metrics.metrics_engine import MetricsCollectionEngine
from app.platform.monitoring.monitoring_engine import MonitoringEngine
from app.platform.performance.performance_engine import PerformanceOptimizationEngine
from app.platform.rate_limiting.rate_limiter import RateLimiterEngine
from app.platform.recovery.recovery_engine import DisasterRecoveryEngine
from app.platform.resilience.resilience_engine import ResilienceEngine
from app.platform.security.security_hardening import SecurityHardeningEngine
from app.platform.tracing.tracing_engine import TracingEngine
from core.logging import get_logger

logger = get_logger("platform_service")


class PlatformServiceRegistry:
    """Central Platform Service Registry Singleton."""

    _instance: Optional["PlatformServiceRegistry"] = None

    def __init__(self) -> None:
        self.security_engine = SecurityHardeningEngine()
        self.tracing_engine = TracingEngine()
        self.logging_engine = StructuredLoggingEngine()
        self.metrics_engine = MetricsCollectionEngine()
        self.health_engine = HealthCheckEngine()
        self.monitoring_engine = MonitoringEngine()
        self.alert_engine = AlertEngine()
        self.resilience_engine = ResilienceEngine()
        self.backup_engine = BackupEngine()
        self.recovery_engine = DisasterRecoveryEngine(self.backup_engine)
        self.performance_engine = PerformanceOptimizationEngine()
        self.cache_engine = CachingEngine()
        self.rate_limiter = RateLimiterEngine()
        self.diagnostics_engine = DiagnosticsEngine(
            self.health_engine,
            self.metrics_engine,
            self.cache_engine,
            self.performance_engine,
            self.resilience_engine,
            self.security_engine,
        )

    @classmethod
    def get_instance(cls) -> "PlatformServiceRegistry":
        if cls._instance is None:
            cls._instance = PlatformServiceRegistry()
        return cls._instance
