# FacultyIQ Backend Architecture

The backend of FacultyIQ is built using **ASP.NET Core 9** following the principles of **Clean Architecture**, **Domain-Driven Design (DDD)**, and **CQRS readiness**.

## 🏗 Project Structure

```
backend/
├── src/
│   ├── FacultyIQ.Domain/           # Core Entities, Aggregates, Value Objects, Domain Events
│   ├── FacultyIQ.Application/      # Use Cases, CQRS Commands/Queries, DTOs, Validation
│   ├── FacultyIQ.Infrastructure/   # External Integrations, Serilog, Storage, Redis, Qdrant
│   ├── FacultyIQ.Persistence/      # EF Core DbContext, Interceptors, Repositories, Migrations
│   ├── FacultyIQ.SharedKernel/     # Result<T> pattern, Errors, Base Interfaces & Guard clauses
│   └── FacultyIQ.Api/              # ASP.NET Core Web API Endpoints, Middleware, Swagger
└── tests/                          # Test Projects
    ├── FacultyIQ.Domain.UnitTests/
    ├── FacultyIQ.Application.UnitTests/
    ├── FacultyIQ.Infrastructure.IntegrationTests/
    └── FacultyIQ.Api.FunctionalTests/
```

## 🎯 Architecture Responsibilities

- **Domain**: Pure C# domain logic with zero external dependencies. Contains entities, value objects, domain events, and base entity abstractions (`BaseEntity`, `AggregateRoot`).
- **Application**: Application contracts, CQRS abstractions (`ICommand`, `IQuery`), interfaces for external services, pipeline behaviors.
- **Infrastructure**: Concrete implementations of external services (MinIO storage, Redis caching, Qdrant vector database connection, Ollama AI connectors, Serilog structured logging).
- **Persistence**: Database access layer built on EF Core 9 with PostgreSQL. Manages `ApplicationDbContext`, entity configurations, repository abstractions, Unit of Work, soft delete filters, and auditing interceptors.
- **SharedKernel**: Reusable primitives shared across all projects such as `Result<T>`, `Error` records, domain exceptions, and pagination structures.
- **Api**: The entry point exposing REST APIs with API versioning (`/api/v1/...`), global exception handling middleware mapping to RFC 7807 `ProblemDetails`, OpenAPI/Swagger specifications, and health checks.

## 🔌 Extension Points

- **Adding a Domain Feature**:
  1. Define Aggregate/Entities in `FacultyIQ.Domain`.
  2. Define Commands/Queries/Handlers in `FacultyIQ.Application`.
  3. Implement Persistence configurations in `FacultyIQ.Persistence`.
  4. Expose Controller/Endpoint in `FacultyIQ.Api`.
