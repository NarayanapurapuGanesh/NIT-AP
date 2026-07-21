# RAG, KNOWLEDGE BASE, AND INFORMATION RETRIEVAL STANDARD

## DOCUMENT CONTROL
| Document ID | FACULTYIQ-RAG-001 |
|---|---|
| **Version** | 1.0.0 |
| **Status** | **APPROVED / BINDING** |
| **Classification** | Enterprise Confidential |
| **Owner** | Knowledge Engineering Council |

> [!CAUTION]
> **AUTHORITATIVE RAG SPECIFICATION**
> This document dictates the absolute boundaries for Information Retrieval in FacultyIQ. Because local Small Language Models (SLMs) like Qwen2.5 3B lack vast parametric knowledge, the intelligence of FacultyIQ is entirely dependent on the quality of its RAG pipelines. Feeding poorly chunked or irrelevant context to an LLM is treated as a critical architectural failure.

---

## 1 Executive Summary

### 1.1 Purpose
The RAG and Information Retrieval Standard ensures that FacultyIQ AI Agents base their scoring decisions strictly on verified University Rubrics and accurate Resume parsing, virtually eliminating model hallucination.

### 1.2 Knowledge Vision
- **Retrieval First**: If the answer is not in the retrieved context, the LLM MUST refuse to answer.
- **Offline First**: All embedding generation (converting text to mathematical vectors) MUST occur locally on University hardware. Calling OpenAI's `text-embedding-3-small` is strictly forbidden.

---

## 2 Knowledge Engineering Principles

1. **Evidence Before Generation**: Every AI response must cite the exact `chunk_id` and `document_id` used to generate the conclusion.
2. **Single Source of Truth**: Qdrant (Vector DB) is an index. The ultimate source of truth for the raw text remains in PostgreSQL (for rubrics) or MinIO (for PDFs).
3. **Deterministic Retrieval**: RAG search algorithms (Hybrid BM25 + Dense) must return the exact same top-K documents for the exact same query, every time.

---

## 3 Enterprise Knowledge Architecture

### 3.1 RAG Topology
```mermaid
graph TD
    subgraph "Ingestion Pipeline"
        PDF[PDF Upload] --> OCR[PyMuPDF OCR]
        OCR --> Chunking[Semantic Chunking]
        Chunking --> EmbedModel[Local Embedding Model]
        EmbedModel --> Qdrant[(Qdrant Vector DB)]
    end
    
    subgraph "Retrieval Pipeline"
        UserQuery[Agent Query] --> QueryEmbed[Embed Query]
        QueryEmbed --> Search[Hybrid Search]
        Search --> Qdrant
        Qdrant --> ReRank[Cross-Encoder Re-Ranking]
        ReRank --> LLM[Context Injection (LLM)]
    end
```

---

## 4 Knowledge Acquisition

- **Supported Formats**: PDF (Resumes, Research Papers), DOCX (Course Syllabi), and Markdown (Institutional Policies).
- **OCR Engine**: PyMuPDF is the standard for extracting structural text (preserving tables and bullet points). Tesseract is used as a fallback for scanned image-only PDFs.

---

## 5 Document Processing Pipeline

1. **File Validation**: Reject any file containing active macros, javascript, or exceeding 20MB.
2. **Cleaning**: Strip invisible watermarks, normalize unicode characters, and remove excessive whitespace.
3. **Metadata Extraction**: Append `CreationDate`, `Author`, and `TenantID` to the parsed text payload.

---

## 6 Chunking Strategy

- **Semantic Chunking**: Documents are split at semantic boundaries (paragraphs, markdown headers) rather than arbitrary character counts.
- **Limits**: Maximum chunk size is `512 tokens`.
- **Overlap**: `50 tokens` of overlap between chunks to ensure concepts split across paragraphs retain their contextual meaning.
- **Hierarchical Chunking**: A parent chunk (the entire section) is linked to smaller child chunks. If a child chunk is retrieved, the RAG pipeline expands the context to include the parent chunk before feeding it to the LLM.

---

## 7 Embedding Pipeline

- **Embedding Model**: `BAAI/bge-base-en-v1.5` (768 dimensions). Chosen for its optimal balance of retrieval accuracy and low VRAM requirements for local execution.
- **Batch Processing**: When indexing large university course catalogs, embeddings are processed in batches of 32 to maximize GPU utilization without causing OOM.

---

## 8 Vector Database Standards (Qdrant)

- **Collections**: Data is segmented into distinct Qdrant Collections (e.g., `resumes_col`, `rubrics_col`).
- **Metadata Payloads**: Every vector in Qdrant MUST contain a JSON payload with `tenant_id` and `department_id`.
- **Partitioning**: Multi-tenant isolation is enforced at query time using Qdrant's payload filtering. A query MUST always include a `tenant_id` filter.

---

## 9 Retrieval Strategies

### 9.1 Hybrid Retrieval
FacultyIQ mandates a Hybrid Search approach for all RAG pipelines:
1. **Dense Retrieval (Vector)**: Finds conceptually similar matches (e.g., "Web Developer" matches "Frontend Engineer").
2. **Sparse Retrieval (BM25)**: Finds exact keyword matches (e.g., "Kubernetes", "AWS").
3. **Fusion**: Reciprocal Rank Fusion (RRF) combines the scores from both methods to determine the final top-K candidates.

---

## 10 Knowledge Ranking (Re-Ranking)

- **Cross-Encoders**: RRF is fast but imprecise. The top-20 results from Qdrant MUST be passed through a local Cross-Encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`).
- **Operation**: The Cross-Encoder scores the exact relationship between the Query and the Chunk, yielding the final top-5 chunks that are actually injected into the LLM prompt.

---

## 11 Knowledge Validation

- **Duplicate Detection**: Hashes of raw text chunks are checked against PostgreSQL. If a duplicate exists, the embedding generation is skipped to save GPU cycles.
- **Semantic Drift**: If a Department updates a hiring rubric, all previous vector embeddings for that rubric MUST be immediately invalidated and re-computed.

---

## 12 Context Assembly

- **Context Ordering**: Retrieved chunks are injected into the LLM prompt in order of relevance, with the most relevant chunk placed at the very top (or very bottom, depending on the specific LLM's attention bias).
- **Token Budgeting**: The total injected context MUST NOT exceed 75% of the LLM's context window (e.g., ~6,000 tokens for Qwen2.5), leaving 25% for the instruction and generation.

---

## 13 Knowledge Versioning

- **Embedding Versions**: Because changing the embedding model (e.g., upgrading from `bge-base` to `bge-large`) alters the mathematical vector space, all 768-dimension vectors become incompatible with the new model.
- **Migration**: When an embedding model is upgraded, a background Celery worker MUST re-embed the entire PostgreSQL database into a new Qdrant collection, hot-swapping the collections only when 100% complete.

---

## 14 Knowledge Governance

- **Ownership**: Department Heads own their respective Rubrics.
- **Publishing**: Rubrics cannot be ingested into the Vector database until they are cryptographically signed/approved by the University HR compliance board.

---

## 15 Knowledge Security

- **Data Leakage Prevention**: RAG Context Assembly MUST strip Candidate PII (Names, Emails, Phone Numbers) using a local NER (Named Entity Recognition) model *before* embedding the resume chunks into Qdrant. This ensures the Vector DB contains only anonymized skills and experiences.

---

## 16 Performance Optimization

- **Caching**: Identical RAG queries (e.g., querying the standard "Computer Science Core Requirements" rubric) are cached in Redis for 24 hours to bypass the embedding and retrieval pipeline entirely.
- **Qdrant Optimization**: HNSW (Hierarchical Navigable Small World) indices are used to ensure sub-millisecond vector search times even with millions of vectors.

---

## 17 Monitoring

- **Query Latency**: The complete Retrieval pipeline (Embedding ➔ Search ➔ Re-rank) MUST execute in < 500ms.
- **Dashboards**: Grafana dashboards track the average BM25 vs Vector score distributions to ensure Hybrid Search is functioning optimally.

---

## 18 Testing

- **Retrieval Tests**: A Golden Dataset of 500 Queries mapped to known Ground-Truth Documents.
- **Metrics**: 
  - `Recall@5` MUST be > 95% (The correct document is in the top 5 results 95% of the time).
  - `MRR` (Mean Reciprocal Rank) MUST be > 0.85.

---

## 19 Architecture Decision Records

- **ADR-RAG-001: Qdrant over Milvus / Pinecone**
  - *Decision*: Adopt Qdrant (Rust-based) as the vector database.
  - *Context*: Pinecone violates the Offline-First mandate. Milvus requires too many microservices (Etcd, MinIO, Pulsar) for local developer environments. Qdrant runs as a single lightweight binary/container.

---

## 20 Traceability Matrix

| Source | Processing | Vector Index | Retrieval | AI Agent |
|---|---|---|---|---|
| Candidate Resume (PDF) | PyMuPDF | `resumes_col` | Hybrid (BM25 + Dense) | Resume Agent |
| Dept Rubric (DOCX) | Markdown Parser | `rubrics_col` | Semantic (Dense) | Bloom Agent |

---

## 21 Future Evolution

- **GraphRAG**: Evolving beyond vector similarity to extract Entity-Relationship Knowledge Graphs from resumes (e.g., `[Candidate] --WORKED_AT--> [Company] --USED--> [Technology]`). This allows complex multi-hop queries that standard Vector databases struggle with.

---

## 22 Glossary

- **Cross-Encoder**: A model that takes both the query and the document simultaneously to compute an highly accurate relevance score, used for re-ranking.
- **Dense Retrieval**: Searching using mathematical embeddings in vector space (captures meaning/semantics).
- **Sparse Retrieval**: Searching using exact keyword frequencies (like TF-IDF or BM25).

---

## 23 Revision History

| Version | Date | Status | Approvals |
|---|---|---|---|
| **1.0.0** | 2026-07-19 | **APPROVED** | Knowledge Engineering Council |
