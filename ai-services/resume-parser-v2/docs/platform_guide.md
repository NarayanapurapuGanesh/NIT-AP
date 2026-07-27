# Enterprise Production Hardening Platform Guide (`resume-parser-v2`)

> Phase 15 Hardening Layer providing Security, Observability, OpenTelemetry Tracing, Prometheus Metrics, Health Check Probes, Alerting, Fault-Tolerant Resilience (Circuit Breaker, Retry, Bulkhead), Automated Backup & DR, LRU/TTL Caching, Token Bucket Rate Limiting, Diagnostics, and REST APIs.

---

## 🏛️ Platform Operational Architecture

```
                       Client / Frontend API Requests
                                     │
                                     ▼
                   [Security Hardening & Rate Limiter]
                  (XSS / SQLi / OWASP / Token Bucket)
                                     │
                                     ▼
                   [OpenTelemetry Tracing & Logging]
                    (Correlation ID + JSON Logging)
                                     │
                                     ▼
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        [Resilience Engine]                    [Caching Engine]
       (Circuit Breakers & Retries)            (LRU + TTL Cache)
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                   [Health Probes & Metrics Scraper]
                 (API, DB, Redis, Ollama, Storage, Queue)
```

---

## 🔌 REST API Endpoints

### 1. `GET /api/v1/platform/health`
Returns aggregated health report for all system dependencies.

```json
{
  "overall_status": "healthy",
  "checks": [
    { "service_name": "FastAPI Application", "status": "healthy", "response_time_ms": 1.2 },
    { "service_name": "PostgreSQL Database", "status": "healthy", "response_time_ms": 8.5 },
    { "service_name": "Redis Cache", "status": "healthy", "response_time_ms": 2.1 },
    { "service_name": "Ollama LLM Service", "status": "healthy", "response_time_ms": 45.3 },
    { "service_name": "Object Storage (MinIO)", "status": "healthy", "response_time_ms": 12.0 },
    { "service_name": "Task Queue", "status": "healthy", "response_time_ms": 3.4 },
    { "service_name": "Background Workers", "status": "healthy", "response_time_ms": 1.0 }
  ],
  "uptime_seconds": 1250.45
}
```

### 2. `GET /api/v1/platform/metrics`
Exposes Prometheus text-formatted metric counters, gauges, and histograms for scraping.

### 3. `GET /api/v1/platform/diagnostics`
Generates a complete platform diagnostic snapshot including OWASP Top 10 security audit records, performance profiles, cache statistics, and circuit breaker states.

### 4. `GET /api/v1/platform/status`
Provides high-level system operational status and live monitoring parameters.

### 5. `GET /api/v1/platform/alerts`
Lists active and historical alert events fired by threshold rules.

### 6. `GET /api/v1/platform/cache/stats`
Returns cache efficiency parameters (hit count, miss count, hit ratio %, evictions).

---

## ⚡ Resilience & Fault Tolerance Patterns

| Pattern | Behavior |
|---------|----------|
| **Circuit Breaker** | Automatically trips from `CLOSED` → `OPEN` upon 5 consecutive failures, isolating downstream faults. |
| **Retry with Backoff** | Retries transient failures up to 3 times using exponential backoff delay. |
| **Bulkhead Isolation** | Restricts concurrent resource pools to prevent failure propagation. |
| **Fallback Strategy** | Provides safe degraded fallbacks when circuit breakers are `OPEN`. |
