# FacultyIQ Vector Database Architecture

## 🔍 Overview

FacultyIQ uses **Qdrant Vector Database** (`localhost:6333` HTTP / `6334` gRPC) for semantic candidate search, research paper vector embeddings, and RAG (Retrieval-Augmented Generation) dossier matching.

---

## 📐 Collection Specifications

- **Default Collection**: `facultyiq-candidates-v1`
- **Vector Dimension**: `1536` (Compatible with OpenAI / Ollama embeddings)
- **Distance Metric**: `Cosine` similarity
- **Payload Indexing**: Candidate ID, department, research domains, grant history, publication count.

---

## 🔌 Abstraction Layer

- **`IVectorService`**: Abstraction for upserting vector records, querying nearest neighbors (`SearchAsync`), and deleting records.
- **`ICollectionManager`**: Manages collection lifecycle, distance metrics, and vector index configurations.
- **`QdrantHealthCheck`**: Verifies Qdrant gRPC / HTTP endpoint reachability during system startup.
