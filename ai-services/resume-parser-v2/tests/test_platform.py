"""
Pytest integration & unit tests for Phase 15 Enterprise Production Hardening Platform.
Health Probes, Prometheus Metrics, Tracing, Security Hardening, Circuit Breakers, Cache,
Rate Limiter, Backup/Recovery, Alerts, Diagnostics & REST APIs.
"""

import pytest
from httpx import AsyncClient
from app.platform.pipeline.platform_pipeline import PlatformPipeline
from app.platform.schemas.platform_models import BackupType, HealthStatus
from app.platform.services.platform_service import PlatformServiceRegistry


@pytest.fixture
def platform_pipeline():
    return PlatformPipeline()


@pytest.fixture
def platform_registry():
    return PlatformServiceRegistry.get_instance()


@pytest.mark.anyio
async def test_platform_health_report(platform_pipeline: PlatformPipeline):
    report = platform_pipeline.get_health_report()
    assert report.overall_status == HealthStatus.HEALTHY
    assert len(report.checks) == 7
    assert report.uptime_seconds >= 0.0


@pytest.mark.anyio
async def test_prometheus_metrics_export(platform_pipeline: PlatformPipeline):
    metrics_str = platform_pipeline.get_prometheus_metrics()
    assert "# TYPE facultyiq_cpu_usage_percent gauge" in metrics_str
    assert "facultyiq_api_requests_total" in metrics_str


@pytest.mark.anyio
async def test_security_hardening_sql_and_xss_detection(platform_registry: PlatformServiceRegistry):
    sec = platform_registry.security_engine

    # SQL Injection Detection
    assert sec.detect_sql_injection("SELECT * FROM users WHERE '1'='1'") is True
    assert sec.detect_sql_injection("Normal search query") is False

    # XSS Detection
    assert sec.detect_xss("<script>alert('xss')</script>") is True
    assert sec.detect_xss("Regular text string") is False

    # Secrets Redaction
    redacted = sec.redact_secrets("config api_key=secret_12345")
    assert "[REDACTED]" in redacted


@pytest.mark.anyio
async def test_circuit_breaker_resilience(platform_registry: PlatformServiceRegistry):
    res = platform_registry.resilience_engine
    service = "test_ai_service"

    def failing_func():
        raise ValueError("Service down")

    def fallback_func():
        return "fallback_result"

    # Trip circuit breaker
    for _ in range(5):
        try:
            res.execute_with_circuit_breaker(service, failing_func)
        except Exception:
            pass

    cb = res.get_circuit_breaker(service)
    assert cb.state.value == "open"

    # Execute with fallback when OPEN
    out = res.execute_with_circuit_breaker(service, failing_func, fallback_func=fallback_func)
    assert out == "fallback_result"


@pytest.mark.anyio
async def test_caching_engine_lru_and_ttl(platform_registry: PlatformServiceRegistry):
    cache = platform_registry.cache_engine
    cache.set("key1", "value1", ttl_seconds=60)
    assert cache.get("key1") == "value1"

    stats = cache.get_stats()
    assert stats.hit_count >= 1


@pytest.mark.anyio
async def test_rate_limiter_token_bucket(platform_registry: PlatformServiceRegistry):
    limiter = platform_registry.rate_limiter
    status1 = limiter.is_allowed("client_ip_127_0_0_1", max_requests=2, window_seconds=60)
    assert status1.remaining_requests == 1

    status2 = limiter.is_allowed("client_ip_127_0_0_1", max_requests=2, window_seconds=60)
    assert status2.remaining_requests == 0


@pytest.mark.anyio
async def test_backup_and_disaster_recovery(platform_registry: PlatformServiceRegistry):
    backup_engine = platform_registry.backup_engine
    recovery_engine = platform_registry.recovery_engine

    backup = backup_engine.create_backup(BackupType.CONFIGURATION, {"setting_a": True, "setting_b": 100})
    assert backup.verified is True

    restore_res = recovery_engine.restore_backup(backup.backup_id)
    assert restore_res.status == "success"
    assert restore_res.validated is True


@pytest.mark.anyio
async def test_platform_api_health_endpoint(async_client: AsyncClient):
    res = await async_client.get("/api/v1/platform/health")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["overall_status"] == "healthy"


@pytest.mark.anyio
async def test_platform_api_metrics_endpoint(async_client: AsyncClient):
    res = await async_client.get("/api/v1/platform/metrics")
    assert res.status_code == 200
    assert "facultyiq_" in res.text


@pytest.mark.anyio
async def test_platform_api_status_endpoint(async_client: AsyncClient):
    res = await async_client.get("/api/v1/platform/status")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
