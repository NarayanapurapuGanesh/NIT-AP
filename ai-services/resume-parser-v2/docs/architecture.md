# `resume-parser-v2` Architecture Specifications

## 🏛️ System Overview

`resume-parser-v2` is an enterprise-grade Academic Resume Intelligence Engine foundation designed using **Clean Architecture** and **Domain-Driven Design (DDD)**. It serves as the dedicated AI worker microservice for FacultyIQ.

---

## 📐 Architecture Layers

```
resume-parser-v2/
├── app/                  # Application Layer (FastAPI endpoints, Middlewares, Lifespan)
│   ├── api/              # Versioned API Routers (v1)
│   ├── services/         # Service Contracts (IService) & ServiceRegistry DI
│   ├── pipelines/        # Pipeline Contracts (IPipelineStep) & PipelineRegistry
│   └── dependencies/     # Dependency Providers
├── core/                 # Infrastructure & Cross-Cutting Concerns
│   ├── config.py         # pydantic-settings v2 Environment loader
│   ├── logging.py        # structlog & Rich console output
│   ├── exceptions.py     # Application domain exception hierarchy
│   ├── middleware.py     # Request ID & Global Exception Handlers
│   └── security.py       # CORS, Trusted Host & Security Headers
├── classifiers/          # Extension Point: Document & Section Classification
├── extractors/            # Extension Point: Entity & Metric Extraction
├── layout/               # Extension Point: Layout Decomposition (PDF/Doc)
├── detectors/            # Extension Point: Table & Bounding Box Detection
├── validators/           # Extension Point: Domain Rule Validation
├── normalizers/          # Extension Point: Taxonomy Normalization
├── ontology/             # Extension Point: Academic Rank Taxonomy
├── llm/                  # Extension Point: Ollama & Local LLM Connectors
├── schemas/              # Pydantic Base DTOs
├── models/               # Domain Entity Models
├── evidence/             # Lineage & Bounding Box Evidence Graph
├── utils/                # Shared Utilities
└── tests/                # Async Pytest Suite
```

---

## ⚡ Extension Pipeline Lifecycle

Every future module registers steps implementing `IPipelineStep`:

```python
class IPipelineStep(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass

    @abstractmethod
    async def execute(self, context: PipelineContext) -> PipelineContext: pass
```

Steps are registered with `pipeline_registry`:
```python
pipeline_registry.register("resume_ingestion_pipeline", [
    LayoutAnalysisStep(),
    ClassifierStep(),
    ExtractorStep(),
    ValidatorStep(),
])
```

Context (`PipelineContext`) carries state immutably through each step with strict error tracking and execution duration recording.
