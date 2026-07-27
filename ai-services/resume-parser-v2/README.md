# Academic Resume Intelligence Engine (`resume-parser-v2`) 🎓🤖

> Enterprise-grade Python 3.12+ FastAPI Phase 1 foundation for multi-agent faculty recruitment and candidate analysis.

---

## 🌟 Architecture Highlights

- **Clean Architecture & SOLID**: Decoupled core engine, pipelines, service contracts, and extension points.
- **Pydantic v2 & `pydantic-settings`**: Type-safe central configuration management across Development, Testing, and Production environments.
- **Structured Logging (`structlog`)**: Rich colored console logs in development mode and JSON logs in production.
- **Dynamic Pipeline Framework**: Thread-safe step orchestrator (`PipelineRegistry`) and service registry (`ServiceRegistry`).
- **Production Middlewares**: Automatic `X-Request-ID` propagation, execution timing, security headers, CORS, trusted hosts, and global exception handling.
- **Fully Async**: Powered by ASGI FastAPI & `pytest-asyncio` testing suite.

---

## 📁 Directory Structure

```
resume-parser-v2/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── health.py
│   │   │   │   ├── version.py
│   │   │   │   └── readiness.py
│   │   │   └── router.py
│   ├── dependencies/
│   │   └── config.py
│   ├── pipelines/
│   │   ├── base.py
│   │   └── registry.py
│   ├── services/
│   │   ├── base.py
│   │   └── registry.py
│   └── main.py
├── core/
│   ├── config.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── logging.py
│   ├── middleware.py
│   └── security.py
├── classifiers/      # Base interfaces for classification plugins
├── extractors/       # Base interfaces for feature extraction
├── layout/           # Base interfaces for document layout decomposition
├── detectors/        # Base interfaces for section/table boundary detection
├── validators/       # Base interfaces for domain validation
├── normalizers/      # Base interfaces for canonical taxonomy normalization
├── ontology/         # Base interfaces for academic rank taxonomy
├── llm/              # Base interfaces for local LLM (Ollama) integration
├── schemas/          # Base response envelopes & Pydantic DTOs
├── models/           # Domain entity base models
├── evidence/         # Lineage & evidence graph tracking
├── utils/            # Shared helper functions
├── tests/            # Pytest test suite
├── docs/             # Technical architecture blueprints
├── .env.example
├── pyproject.toml
└── ruff.toml
```

---

## 🚀 Quickstart & Execution Commands

### 1. Environment Setup

Using `uv` (recommended):
```bash
uv venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

Using `pip`:
```bash
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.example .env
```

### 3. Run FastAPI Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access Swagger UI Documentation: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

### 4. Run Pytest Suite

```bash
pytest tests/ -v
```

---

## 🔒 Endpoints Overview

- `GET /api/v1/health`: Liveness probe.
- `GET /api/v1/version`: Version metadata.
- `GET /api/v1/readiness`: Readiness probe & downstream service checks.
