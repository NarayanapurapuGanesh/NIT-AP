# FacultyIQ Infrastructure Containers

Contains Docker Compose and Dockerfile configurations for containerizing FacultyIQ services.

## 📦 Container Services

- **PostgreSQL 16**: Relational database storage.
- **Redis 7**: Distributed caching and session management.
- **Qdrant**: High-performance vector database for RAG candidate retrieval.
- **MinIO**: S3-compatible object store for resumes, publication PDFs, and interview recordings.
- **Ollama**: Local AI LLM engine for offline inference.

## 🚀 Execution

```bash
docker-compose -f docker/docker-compose.yml up -d
```
