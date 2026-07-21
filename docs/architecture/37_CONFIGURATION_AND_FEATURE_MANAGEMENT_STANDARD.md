# CONFIGURATION AND FEATURE MANAGEMENT STANDARD

## DOCUMENT CONTROL
| Document ID | FACULTYIQ-CFG-001 |
|---|---|
| **Version** | 1.0.0 |
| **Status** | **APPROVED / BINDING** |
| **Classification** | Enterprise Confidential |
| **Owner** | Platform Configuration Council |

> [!CAUTION]
> **AUTHORITATIVE CONFIGURATION SPECIFICATION**
> This document enforces strict Twelve-Factor App compliance for FacultyIQ. Hardcoding configuration values (URLs, thresholds, API keys, AI model names) into compiled C# or Python code is strictly forbidden and will result in immediate CI/CD rejection.

---

## 1 Executive Summary

### 1.1 Purpose
FacultyIQ is a multi-tenant platform spanning diverse university environments. The Configuration Standard ensures that the identical Docker image can be deployed to University A (using Azure, high concurrency) and University B (using on-premise hardware, low concurrency) by mutating configuration only.

### 1.2 Configuration Philosophy
- **Immutable Infrastructure**: Once built, a Docker container is immutable. It adapts to its environment strictly via injected configuration at runtime.
- **Offline First**: Configuration management tools (e.g., Vault, Consul) MUST be capable of running entirely within an air-gapped local network.

---

## 2 Configuration Principles

1. **Separation of Code and Configuration**: If a value might change between Staging and Production, it belongs in configuration, not code.
2. **Runtime Configurability**: Non-structural changes (e.g., disabling a specific AI Agent or changing a UI banner) MUST not require a pod restart.
3. **Auditability**: Every change to an environment variable, feature flag, or LLM threshold MUST be logged and attributable to a specific human administrator.

---

## 3 Configuration Architecture

### 3.1 Topology
```mermaid
graph TD
    subgraph "Configuration Stores"
        Consul[HashiCorp Consul (KV)]
        Vault[HashiCorp Vault (Secrets)]
        DB[(PostgreSQL - Feature Flags)]
    end
    
    subgraph "FacultyIQ Runtime"
        API[C# API]
        Python[Python Celery Workers]
        NextJS[Next.js Frontend]
    end
    
    Consul -->|Injects AppSettings| API
    Consul -->|Injects Env Vars| Python
    Vault -->|Injects Secrets| API
    DB -->|Toggles Features| NextJS
```

---

## 4 Configuration Hierarchy

Configuration values are resolved in a strict "Last-Write-Wins" cascading order to allow granular overriding:
1. **Global Default**: Hardcoded default in code (Lowest priority).
2. **Environment**: `appsettings.Production.json` or `.env` files.
3. **Consul KV**: Distributed Key-Value store overrides.
4. **Institution Override**: PostgreSQL tenant-specific configuration.
5. **Runtime Override**: Live admin dashboard overrides (Highest priority).

---

## 5 Environment Management

- **Development**: Local `docker-compose.yml` optimized for fast reloading. Secrets use dummy values.
- **Staging**: Identical infrastructure topology to Production but scaled down. Used for Golden Dataset benchmarking.
- **Production**: Full High-Availability mode. Secrets are exclusively pulled from Vault. Direct database access is blocked.

---

## 6 Feature Flag Framework

- **AI Feature Flags**: Because AI models are unpredictable, new agents (e.g., the Coding Agent) are deployed behind an "Experimental Flag." If it begins hallucinating in Production, the kill switch is triggered via the Admin UI, reverting evaluation back to human-only workflow.
- **Progressive Rollouts**: Feature flags support percentage-based rollouts (e.g., Enable new RAG pipeline for 10% of resumes).

---

## 7 Runtime Configuration

- **Hot Reload (C#)**: The core API uses `.NET IOptionsSnapshot<T>`. When the Consul KV store changes, the API automatically binds the new configuration payload on the very next HTTP request without dropping active connections.
- **Fallback Defaults**: If the Configuration Service (Consul) goes offline, the application MUST cache the last known good configuration in memory to prevent catastrophic failure.

---

## 8 AI Configuration

The following parameters are extracted into dynamic configuration to allow real-time tuning by the AI Engineering team:
- **`AI_MODEL_ROUTING`**: Which Ollama model handles which task (e.g., `resume=qwen2.5:3b`, `code=qwen2.5-coder:7b`).
- **`AI_MAX_CONTEXT_TOKENS`**: The threshold before a chunk is truncated.
- **`AI_TEMPERATURE`**: Hardcoded limit between `0.0` and `0.2`.
- **`AI_CONFIDENCE_THRESHOLD`**: If the Decision Agent's confidence drops below this configurable float (e.g., `0.85`), the workflow routes to Human Review.

---

## 9 Workflow Configuration

- **Retry Policies**: Configured via Celery/RabbitMQ settings. 
  - `MAX_RETRIES=3`
  - `BACKOFF_FACTOR=2` (Exponential backoff).
- **Concurrency**: `CELERY_WORKER_CONCURRENCY=5` (Tightly coupled to VRAM availability, requiring strict governance).

---

## 10 Infrastructure Configuration

- **Docker Definitions**: The `docker-compose.production.yml` strictly defines memory limits (e.g., `mem_limit: 8g`) to prevent a runaway Python process from starving the PostgreSQL container.
- **Logging Level**: Configurable dynamically (e.g., shifting from `Warning` to `Debug` in Production for 15 minutes to diagnose a live issue, then shifting back).

---

## 11 Secret Management

### 11.1 HashiCorp Vault Integration
- **Mandate**: API Keys, Database Passwords, and Cryptographic Signing Keys SHALL NOT be stored in environment variables (`.env`). 
- **Rotation**: FacultyIQ implements dynamic credentials. The C# API authenticates to PostgreSQL using short-lived credentials generated by Vault that automatically expire every 60 minutes.

---

## 12 Validation Framework

- **Startup Validation**: C# `IHostedService` validates all strongly-typed configuration objects using Data Annotations (e.g., `[Required]`, `[Range]`) at startup. If the configuration is missing or invalid (e.g., `AI_TEMPERATURE = 5.0`), the application immediately crashes with a fatal log before accepting traffic.

---

## 13 Versioning

- **Configuration-as-Code**: All base environment configurations (Terraform, Consul bootstrap JSONs) are stored in a dedicated `facultyiq-infrastructure` Git repository. Changes require Pull Request approvals.

---

## 14 Security

- **Tamper Detection**: Critical AI configuration values (like the Golden Prompt IDs) are cryptographically hashed. If a malicious actor alters the value directly in the PostgreSQL database, the runtime validation hash check will fail, and the system will shut down.

---

## 15 Monitoring

- **Configuration Drift**: A daily cron job compares the live Consul KV store against the `main` branch of the infrastructure repository. Any manual deviations made outside of CI/CD trigger a High Severity Slack alert to the DevOps team.

---

## 16 Configuration APIs

- **REST Endpoints**: Secure endpoints (`/api/v1/config/reload`) protected by OAuth2 scopes (`config:write`) to allow the React Admin Dashboard to trigger runtime reloads.

---

## 17 Administration

- **Feature Dashboard**: A visual matrix in the SuperAdmin UI showing the status of all Feature Flags across all University Tenants, allowing support engineers to toggle features for specific failing departments.

---

## 18 Testing

- **Chaos Testing**: During CI/CD, the testing framework purposely deletes a required environment variable to verify that the application fails fast during startup rather than throwing a `NullReferenceException` deep in the execution pipeline.

---

## 19 Governance

- **Ownership**: The Platform Engineering team owns Infrastructure Configuration. The AI Engineering team owns AI Configuration. Changing `AI_TEMPERATURE` requires sign-off from the AI Engineering Lead.

---

## 20 Architecture Decision Records

- **ADR-CFG-001: HashiCorp Stack over Native Kubernetes ConfigMaps**
  - *Decision*: We will use HashiCorp Consul and Vault for distributed configuration and secrets.
  - *Context*: FacultyIQ Phase 1 relies on Docker Compose (Offline First). We cannot rely on Kubernetes ConfigMaps/Secrets. Consul/Vault run cleanly as sidecar containers in `docker-compose`.

---

## 21 Traceability Matrix

| Requirement | Configuration Key | Validation Rule | Hot Reload |
|---|---|---|---|
| Adjust Hallucination Gate | `AI:ConfidenceThreshold` | `Float (0.0-1.0)` | Yes |
| Secure DB Access | `DB:ConnectionString` | `Vault Dynamic Secret` | No (Requires Restart) |

---

## 22 Future Evolution

- **Autonomous Configuration**: In Phase 5, the Platform will implement self-tuning configurations, automatically lowering `CELERY_WORKER_CONCURRENCY` if it detects GPU thermal throttling, or switching to smaller models if Qdrant query latency spikes.

---

## 23 Glossary

- **Twelve-Factor App**: A methodology for building software-as-a-service applications, emphasizing declarative setup and clean separation of config from code.
- **Hot Reload**: The ability for an application to adopt new configuration parameters without restarting the application process.

---

## 24 Revision History

| Version | Date | Status | Approvals |
|---|---|---|---|
| **1.0.0** | 2026-07-19 | **APPROVED** | Platform Configuration Council |
