"""
Canonical Pydantic v2 Models for Enterprise Production Hardening Platform.
Health, Metrics, Tracing, Alerts, Resilience, Caching, Rate Limiting,
Backup, Recovery, Diagnostics, Security, and Performance Profiling.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


# --- Enums ---

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class BackupType(str, Enum):
    DATABASE = "database"
    CONFIGURATION = "configuration"
    AUDIT = "audit"
    WORKFLOW = "workflow"
    DOCUMENTS = "documents"
    MODEL_CONFIG = "model_config"


# --- Health Check Models ---

class HealthCheckResult(BaseModel):
    service_name: str
    status: HealthStatus = HealthStatus.HEALTHY
    response_time_ms: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PlatformHealthReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    overall_status: HealthStatus = HealthStatus.HEALTHY
    checks: List[HealthCheckResult] = Field(default_factory=list)
    uptime_seconds: float = 0.0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- Metrics Models ---

class MetricDataPoint(BaseModel):
    name: str
    value: float
    unit: str = ""
    labels: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetricsSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metrics: List[MetricDataPoint] = Field(default_factory=list)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- Tracing Models ---

class TraceSpan(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: Optional[str] = None
    operation_name: str
    service_name: str = "facultyiq"
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0
    status: str = "ok"
    attributes: Dict[str, Any] = Field(default_factory=dict)


# --- Alert Models ---

class AlertRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    metric_name: str
    condition: str  # gt, lt, eq
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    is_active: bool = True


class AlertEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    current_value: float
    threshold: float
    message: str
    fired_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- Resilience Models ---

class CircuitBreakerState(BaseModel):
    service_name: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_at: Optional[datetime] = None
    last_state_change: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RetryPolicy(BaseModel):
    policy_name: str
    max_retries: int = 3
    base_delay_ms: int = 500
    max_delay_ms: int = 10000
    exponential_backoff: bool = True


# --- Caching Models ---

class CacheEntry(BaseModel):
    key: str
    value: Any
    ttl_seconds: int = 300
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CacheStats(BaseModel):
    total_entries: int = 0
    hit_count: int = 0
    miss_count: int = 0
    hit_ratio: float = 0.0
    eviction_count: int = 0
    memory_used_bytes: int = 0


# --- Rate Limiting Models ---

class RateLimitRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scope: str  # user, tenant, ip, api
    target: str
    max_requests: int = 100
    window_seconds: int = 60
    burst_limit: int = 20


class RateLimitStatus(BaseModel):
    client_key: str
    remaining_requests: int
    total_limit: int
    window_seconds: int
    reset_at: datetime


# --- Backup & Recovery Models ---

class BackupRecord(BaseModel):
    backup_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    backup_type: BackupType
    file_path: str
    size_bytes: int = 0
    checksum: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False


class RecoveryResult(BaseModel):
    recovery_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    backup_id: str
    status: str = "success"
    records_restored: int = 0
    duration_ms: float = 0.0
    validated: bool = False


# --- Security Models ---

class SecurityAuditRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    check_name: str
    passed: bool
    severity: str = "info"
    recommendation: str = ""


# --- Diagnostics & Performance Models ---

class PerformanceProfile(BaseModel):
    endpoint: str
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    avg_ms: float = 0.0
    throughput_rps: float = 0.0
    total_requests: int = 0


class DiagnosticsReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    health: Optional[PlatformHealthReport] = None
    metrics: Optional[MetricsSnapshot] = None
    cache_stats: Optional[CacheStats] = None
    performance_profiles: List[PerformanceProfile] = Field(default_factory=list)
    circuit_breakers: List[CircuitBreakerState] = Field(default_factory=list)
    security_checks: List[SecurityAuditRecord] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
