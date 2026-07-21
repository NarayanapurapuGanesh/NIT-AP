# FacultyIQ DevOps & Observability Architecture

## 🚀 Overview

FacultyIQ provides a production-grade containerized infrastructure stack managed via Docker Compose, monitored with **Prometheus** and **Grafana**, and verified through **GitHub Actions CI/CD**.

---

## 📊 Container Services Matrix

| Service | Port | Image | Purpose |
| :--- | :--- | :--- | :--- |
| **PostgreSQL 16** | 5432 | `postgres:16-alpine` | Relational Persistence & Identity DB |
| **Redis 7** | 6379 | `redis:7-alpine` | Distributed Caching & Rate Limiting |
| **Qdrant** | 6333 / 6334 | `qdrant/qdrant:v1.11.0` | Vector Database for Candidate Search |
| **MinIO** | 9000 / 9001 | `minio/minio` | S3 Object Store for Resumes & Media |
| **Ollama** | 11434 | `ollama/ollama:latest` | Local LLM Inference Engine |
| **Prometheus** | 9090 | `prom/prometheus:latest` | Metrics Scraping & Aggregation |
| **Grafana** | 3000 | `grafana/grafana:latest` | Real-time Observability Dashboards |

---

## 📈 Monitoring Stack

- **Prometheus**: Configured via `docker/prometheus.yml` to scrape system metrics and API endpoints.
- **Grafana**: Automated datasource provisioning (`docker/grafana/provisioning/datasources/prometheus.yml`) connecting to Prometheus on startup.
- **Serilog**: Structured JSON request logging enriched with machine name, environment, and HTTP context.

---

## 🔄 CI/CD Automation

The GitHub Actions workflow (`.github/workflows/ci.yml`) executes on every push and pull request:
1. `.NET 9` SDK restore, Release build, and unit test execution.
2. `Next.js 15` production build and TypeScript type checking.
3. `Docker Compose` specification linting and validation.
