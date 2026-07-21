# FacultyIQ 🎓🤖

> **Enterprise AI-Powered Faculty Recruitment Platform**  
> An offline-first, AI-native, production-grade SaaS solution designed for higher education institutions to streamline academic hiring, candidate evaluation, research verification, and interview synthesis.

---

## 🌟 Executive Overview

**FacultyIQ** solves the complex challenge of university faculty recruitment by delivering end-to-end automated screening, deep publication analysis, structured interviewing, and institutional compliance scoring. Built with an offline-first philosophy, FacultyIQ enables on-premise AI processing through local LLMs (Ollama) while maintaining enterprise readiness, microservice scalability, and strict security compliance.

---

## 🛠️ Technology Stack

| Layer | Technologies & Frameworks |
| :--- | :--- |
| **Frontend** | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion |
| **Backend API** | ASP.NET Core 9 Web API, Clean Architecture, Domain-Driven Design (DDD), CQRS Ready |
| **Database** | PostgreSQL 16, Entity Framework Core 9 |
| **Caching & PubSub** | Redis 7 |
| **Vector Database** | Qdrant Vector Engine |
| **Object Storage** | MinIO S3-Compatible Storage |
| **AI Processing** | Ollama (Local AI models), LangGraph (Agent workflows), Python AI Services |
| **Containerization** | Docker, Docker Compose, Kubernetes Ready |
| **CI/CD & DevOps** | GitHub Actions, PowerShell & Bash Automation |

---

## 🏗️ Architecture Overview

FacultyIQ uses **Clean Architecture** and **Domain-Driven Design (DDD)** principles to decouple core domain logic from framework implementations.

```
FacultyIQ/
├── frontend/                  # Next.js 15 Web Application
├── backend/                   # ASP.NET Core 9 Web API Solution
│   ├── src/
│   │   ├── FacultyIQ.Domain/           # Core Entities, Aggregates, Value Objects, Domain Events
│   │   ├── FacultyIQ.Application/      # Use Cases, CQRS Handlers, DTOs, Pipeline Behaviors
│   │   ├── FacultyIQ.Infrastructure/   # External Services, Storage, Redis, Qdrant, AI Connectors
│   │   ├── FacultyIQ.Persistence/      # EF Core DbContext, Interceptors, Repositories, Migrations
│   │   ├── FacultyIQ.SharedKernel/     # Result<T> pattern, Base Errors, Common Utilities
│   │   └── FacultyIQ.Api/              # Web API Controllers/Endpoints, Middleware, Swagger
│   └── tests/                          # Unit, Integration, and Functional Test Suites
├── ai-services/               # Microservice foundations for Python AI agent workers
├── docker/                    # Docker Compose stack configurations
├── docs/                      # Enterprise Architecture Specifications & ADRs
│   └── architecture/          # Master blueprints (43 core architecture specifications)
├── datasets/                  # Mock benchmark data and evaluation schemas
├── prompts/                   # Version-controlled AI prompt templates
├── scripts/                   # Cross-platform development automation (PowerShell/Bash)
└── infrastructure/            # Terraform / Helm / Deployment manifests
```

---

## 🚀 Getting Started

### Prerequisites

- [.NET 9 SDK](https://dotnet.microsoft.com/download/dotnet/9.0)
- [Node.js 20+ LTS](https://nodejs.org/) & `npm`
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine
- [PowerShell 7+](https://github.com/PowerShell/PowerShell) (Windows/macOS/Linux) or Bash

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/institution/FacultyIQ.git
cd FacultyIQ

# Copy default environment configuration
cp .env.example .env
```

### 2. Start Infrastructure via Docker Compose

```bash
# Using PowerShell helper script
./scripts/dev.ps1 start

# Or using standard Docker Compose
docker-compose -f docker/docker-compose.yml up -d
```

This starts:
- **PostgreSQL 16**: `localhost:5432`
- **Redis 7**: `localhost:6379`
- **Qdrant Vector DB**: `localhost:6333`
- **MinIO S3**: `localhost:9000` (Console: `localhost:9001`)
- **Ollama AI**: `localhost:11434`

### 3. Run Backend API

```bash
cd backend
dotnet restore
dotnet run --project src/FacultyIQ.Api
```

API Swagger documentation is accessible at `https://localhost:7150/swagger`.

### 4. Run Frontend Application

```bash
cd frontend
npm install
npm run dev
```

Frontend application will be accessible at `http://localhost:3000`.

---

## 🔄 Development Workflow

- **Branching Strategy**: Standard GitFlow (`main`, `develop`, `feature/*`, `bugfix/*`).
- **Code Standards**: Strictly enforced via `.editorconfig`, `.eslintrc.json`, and `.prettierrc`.
- **Formatting & Linting**:
  - Frontend: `npm run lint` & `npm run format`
  - Backend: `dotnet format`

---

## 🗺️ Future Roadmap

- [x] **Phase 1: Foundation Architecture** (Monorepo, Clean Architecture solution, Next.js foundation, EF Core PostgreSQL schema, Dev Environment)
- [ ] **Phase 2: Authentication & Multi-Tenancy** (University Tenant Isolation, RBAC, OAuth2/OIDC)
- [ ] **Phase 3: Dossier & Publication Ingestion Engine** (PDF Parser, Google Scholar / ORCID enrichment)
- [ ] **Phase 4: AI Agent RAG Pipeline** (Qdrant embeddings, Ollama LLM candidate scoring)
- [ ] **Phase 5: Automated Structured Interview Engine** (Video processing, candidate synthesis reports)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
