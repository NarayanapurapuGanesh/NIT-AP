# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## DOCUMENT CONTROL
| Document ID | FACULTYIQ-SRS-001 |
|---|---|
| **Version** | 1.0.0 |
| **Status** | **APPROVED / BINDING** |
| **Classification** | Enterprise Confidential |

> [!CAUTION]
> **ENGINEERING CONTRACT**
> This Software Requirements Specification (SRS) serves as the definitive engineering contract. It complies with IEEE 29148 standards. All requirements defined herein using "SHALL" are mandatory. Any deviation requires formal architectural approval.

---

## 1. Introduction

### Purpose
The purpose of this document is to explicitly define the software requirements for FacultyIQ, an Enterprise AI-Powered Faculty Recruitment Platform. It dictates exactly *what* the software shall do before architectural blueprints determine *how* it will be built.

### Scope
This SRS governs the initial foundation and subsequent maturity phases of FacultyIQ. It spans the core web application, the offline-first local AI processing pipelines, the secure ephemeral coding sandboxes, and the underlying data layer.

### Audience
This document is written for Software Architects, Backend/Frontend Engineers, AI Researchers, QA Engineers, DevOps Engineers, and Product Managers.

### Definitions & Abbreviations
- **SRS**: Software Requirements Specification.
- **LLM**: Large Language Model.
- **XAI**: Explainable AI.
- **OCR**: Optical Character Recognition.
- **ATS**: Applicant Tracking System.

### References
- `00_PROJECT_CHARTER.md`
- `01_PRODUCT_REQUIREMENTS_DOCUMENT.md`
- IEEE 29148:2018 Systems and software engineering — Life cycle processes — Requirements engineering.

### Document Overview
Chapters 2-8 provide systemic context. Chapters 9-20 define specific Functional Requirements. Chapters 21-29 define Non-Functional Requirements. Chapters 30-34 provide traceability, risk management, and glossaries.

---

## 2. Product Overview

### Business Context
Universities face unscalable recruitment pipelines relying on biased, manual evaluation of multi-modal data (resumes, teaching videos, code).

### System Context
FacultyIQ is a standalone **Modular Monolith** communicating asynchronously with independent Python AI Workers, operating entirely on-premise or in isolated Virtual Private Clouds (VPCs).

### Research Context
The platform strictly adheres to "Evidence-First" AI principles, requiring deterministic validation of LLM outputs to prevent hallucination in high-stakes hiring scenarios.

### Future SaaS Vision
The architecture shall be designed to eventually support multi-tenancy, enabling smaller institutions to use FacultyIQ as a cloud-based SaaS without hosting their own local models.

---

## 3. Product Perspective

### System Boundary
The system encompasses the Web UI, API Gateway, Application Logic, Database, Message Broker, Storage, and Local AI Runtimes.

### External Systems
- Candidate Identity Providers (Future SSO).
- University LMS (Future Integrations).
- External Job Boards (Read-only scraping / Webhooks).

### Third-party Dependencies
- **Ollama**: For local LLM inference.
- **Docker**: For ephemeral code execution sandboxes.
- **Qdrant**: For vector storage and semantic RAG retrieval.

---

## 4. Product Functions

1. **Authentication**: Secure JWT-based access control with RBAC.
2. **Candidate Management**: ATS-style kanban boards and candidate profiles.
3. **Resume Intelligence**: Deterministic extraction of PDF resumes into structured schemas.
4. **Knowledge Base (RAG)**: Indexing of institutional hiring criteria.
5. **Interview Engine**: Generation of dynamic questions based on Bloom's Taxonomy.
6. **Coding Assessment**: Execution of untrusted code in a secure environment.
7. **Code Explanation**: AI critique of submitted code architecture.
8. **Video Intelligence**: Transcription and pedagogical analysis of candidate videos.
9. **Decision Engine**: Rule-based aggregation of subjective AI scoring.
10. **Reporting**: PDF and web-based explainability reports.

---

## 5. User Classes

| Class | Responsibilities | Permissions | Goals |
|---|---|---|---|
| **Recruiter** | Manage requisitions, communicate with candidates. | `Read`, `Write` (non-admin). | Filter candidates quickly. |
| **Dept Head** | Review AI scores, make final hiring choices. | `Read`, `Override`. | Deep technical evaluation. |
| **Candidate** | Upload resumes, complete tests. | `Submit`, `View Own`. | Seamless application process. |
| **Admin** | System config, LLM Modelfile updates. | `Full Access`. | Maintain uptime and security. |

---

## 6. Operating Environment

- **Production**: On-premise enterprise Linux servers or AWS/Azure VPCs.
- **Offline Mode**: The system SHALL function without outbound internet access for core AI processing.
- **Hardware Requirements**: Minimum 16GB VRAM (e.g., RTX 4090) required per AI worker node for Qwen 2.5 3B inference.

---

## 7. Constraints

- **Technology**: The backend SHALL be implemented in ASP.NET Core 9.
- **Offline AI**: Proprietary cloud APIs (OpenAI) SHALL NOT be used for PII data.
- **Privacy**: The system SHALL comply with GDPR "Right to be Forgotten".
- **Performance**: AI evaluation of a single candidate SHALL NOT exceed 2 minutes.

---

## 8. Assumptions

- Institutions possess the necessary on-premise hardware to run quantized local LLMs, or are willing to provision dedicated cloud GPUs.
- Candidates have access to webcams and microphones for video assessments.

---

## 9. Functional Requirements (Format)

All requirements follow this template:
- **ID**: Unique Identifier.
- **Description**: "The system SHALL..."
- **Priority**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low).
- **Acceptance Criteria**: Verifiable conditions.

---

## 10. Authentication Requirements

### FR-AUTH-01: User Login
- **Description**: The system SHALL authenticate users via email and password, returning a JWT access token and a secure HTTP-only refresh token.
- **Priority**: P0
- **Acceptance Criteria**: Tokens comply with RFC 7519. Passwords are hashed via Argon2id.

### FR-AUTH-02: Role-Based Access Control
- **Description**: The system SHALL restrict API endpoints based on JWT role claims (`Admin`, `Recruiter`, `Panel`, `Candidate`).
- **Priority**: P0

---

## 11. Candidate Management Requirements

### FR-CAND-01: Resume Upload
- **Description**: The system SHALL allow candidates to upload PDF/DOCX files up to 10MB.
- **Priority**: P0
- **Preconditions**: User is authenticated as `Candidate`.
- **Postconditions**: File is securely stored in MinIO; `ResumeUploaded` event published to RabbitMQ.

---

## 12. Resume Intelligence Requirements

### FR-RES-01: Document OCR
- **Description**: The AI Worker SHALL extract raw text from PDF files using OCR fallback if text layers are missing.
- **Priority**: P0

### FR-RES-02: Information Extraction
- **Description**: The system SHALL extract Education, Experience, and Skills using the local LLM and map them to a strict JSON schema.
- **Priority**: P0
- **Business Rule**: If JSON mapping fails schema validation 3 times, the candidate is flagged for `Manual Review`.

### FR-RES-03: Evidence Graph
- **Description**: Every extracted skill SHALL include a citation pointer to the original sentence in the resume.
- **Priority**: P0

---

## 13. Knowledge System Requirements

### FR-KNOW-01: Document Ingestion
- **Description**: The system SHALL allow Admins to upload Department Rubrics (PDF/TXT).
- **Priority**: P1
- **Postconditions**: Documents are chunked, embedded via a local embedding model, and stored in Qdrant.

---

## 14. Interview Requirements

### FR-INT-01: Adaptive Questions
- **Description**: The system SHALL generate 5 interview questions dynamically based on the candidate's extracted Resume JSON and the Requisition requirements.
- **Priority**: P1
- **Traceability**: FR-RES-02.

---

## 15. Coding Assessment Requirements

### FR-CODE-01: Secure Execution
- **Description**: The system SHALL execute candidate code within an ephemeral Docker container lacking outbound network access.
- **Priority**: P0
- **Failure Conditions**: Execution exceeding 10 seconds SHALL trigger a SIGKILL and assign a score of 0.

### FR-CODE-02: Hidden Test Cases
- **Description**: The system SHALL compile and run the code against 5 hidden unit tests, returning Pass/Fail ratios.
- **Priority**: P0

---

## 16. Code Explanation Requirements

### FR-EXP-01: Complexity Analysis
- **Description**: The AI (Qwen2.5-Coder) SHALL analyze passing code and output an estimated Big-O time and space complexity.
- **Priority**: P1
- **Acceptance Criteria**: LLM output must be bounded to specific Enum values (O(1), O(N), O(N^2), etc).


---

## 17. Video Evaluation Requirements

### FR-VID-01: Transcription
- **Description**: The system SHALL transcribe uploaded video MP4s using local Whisper models.
- **Priority**: P1
- **Business Rule**: Transcripts must include speaker diarization (interviewer vs interviewee).

### FR-VID-02: Teaching Effectiveness
- **Description**: The system SHALL evaluate the transcript against standard pedagogical rubrics (e.g., clarity of explanation, use of analogy).
- **Priority**: P1

---

## 18. Bloom Taxonomy Requirements

### FR-BLOOM-01: Question Classification
- **Description**: Every AI-generated technical question SHALL be tagged with a Bloom's Taxonomy tier (Remember, Understand, Apply, Analyze, Evaluate, Create).
- **Priority**: P1

### FR-BLOOM-02: Coverage Analysis
- **Description**: The Decision Engine SHALL ensure that Senior-level requisitions mandate scores in the `Evaluate` and `Create` tiers.
- **Priority**: P0

---

## 19. Decision Engine Requirements

### FR-DEC-01: Evidence Aggregation
- **Description**: The system SHALL aggregate numeric scores from Resume (0-100), Video (0-100), and Code (0-100) using weights defined by the Requisition.
- **Priority**: P0

### FR-DEC-02: Human Override
- **Description**: A user with the `Panel` or `Admin` role SHALL be able to manually override the final AI Recommendation.
- **Priority**: P0
- **Audit Rule**: Overrides must require a mandatory text justification and be logged in the Audit Trail.

---

## 20. Reporting Requirements

### FR-REP-01: Explainability Report
- **Description**: The system SHALL generate a PDF report for every candidate containing the final score, the AI justifications, and verbatim evidence citations.
- **Priority**: P1

---

## 21. Non-Functional Requirements

### NFR-PERF-01: UI Latency
- **Description**: 95% of all synchronous API requests SHALL return within 200ms.

### NFR-AVAIL-01: Uptime
- **Description**: The core web API SHALL support 99.9% uptime. (AI Workers may experience queue delays, but the UI must remain responsive).

### NFR-SCAL-01: Horizontal Scaling
- **Description**: The Python AI Workers SHALL be stateless and capable of horizontal scaling across multiple GPU nodes.

### NFR-OFFLINE-01: Air-Gapped Operation
- **Description**: The entire system, including all AI inference, SHALL be capable of functioning on an air-gapped network with zero external HTTP requests.

---

## 22. Security Requirements

### SEC-01: Encryption at Rest
- **Description**: PostgreSQL and MinIO volumes SHALL utilize AES-256 encryption at the disk level.

### SEC-02: Secure File Upload
- **Description**: The API SHALL validate MIME types, extensions, and file signatures before accepting uploads. Executable binaries (.exe, .sh) SHALL be rejected.

### SEC-03: Rate Limiting
- **Description**: The API Gateway SHALL enforce a rate limit of 100 requests per IP per minute.

---

## 23. AI Requirements

### AI-01: Deterministic Before LLM
- **Description**: The system SHALL use deterministic parsers for structured metadata (emails, phone numbers, dates) and only invoke LLMs for semantic extraction.

### AI-02: Hallucination Prevention
- **Description**: The system SHALL enforce an `Evidence Extraction` phase before `Synthesis`. Evaluative claims without a direct citation SHALL be rejected by the validation pipeline.

### AI-03: Model Versioning
- **Description**: Every evaluation record in PostgreSQL SHALL log the exact model name, version, and Modelfile hash used to generate it.

---

## 24. Data Requirements

### DAT-01: Deletion
- **Description**: A `DeleteCandidate` command SHALL trigger a cascading hard-delete across PostgreSQL, MinIO, Qdrant, and Redis to comply with GDPR.

---

## 25. External Interface Requirements

### EXT-01: RabbitMQ Interface
- **Description**: The ASP.NET Backend and Python AI Workers SHALL communicate exclusively via RabbitMQ using strictly versioned JSON payload contracts.

### EXT-02: Ollama Interface
- **Description**: Python Workers SHALL communicate with Ollama instances via local HTTP REST, utilizing streaming for large context generation.

---

## 26. Error Handling Requirements

### ERR-01: AI Retries
- **Description**: If Ollama returns a 500 error or malformed JSON, the Python worker SHALL retry up to 3 times with exponential backoff before placing the message in a Dead Letter Queue (DLQ).

---

## 27. Logging Requirements

### LOG-01: Structured Logging
- **Description**: All system components SHALL output logs in JSON format.

### LOG-02: Traceability
- **Description**: Every HTTP request originating at the Gateway SHALL generate a `TraceId`, which MUST be propagated through RabbitMQ to the AI Workers for distributed tracing.

---

## 28. Monitoring Requirements

### MON-01: Health Checks
- **Description**: Every container SHALL expose a `/health` endpoint returning 200 OK if internal dependencies (DB, Redis) are reachable.

---

## 29. Testing Requirements

### TST-01: Unit Testing
- **Description**: Business logic domains (ASP.NET Core) SHALL maintain a minimum of 80% code coverage.

### TST-02: AI Regression Testing
- **Description**: Updates to system prompts or model weights SHALL require passing an automated LLM-as-a-Judge regression suite using a golden dataset of 100 historically graded resumes.

---

## 30. Traceability Matrix

| Business Goal | Product Requirement | Functional Requirement | Implementation Module |
|---|---|---|---|
| Reduce Time-to-Hire | Resume Parsing | FR-RES-02: Extraction | `FacultyIQ.Python.ResumeWorker` |
| Zero Bias | Explainable AI | FR-DEC-02: Human Override | `FacultyIQ.Domain.DecisionEngine` |
| Security | Secure Code Exec | FR-CODE-01: Docker Sandbox | `FacultyIQ.Python.Sandbox` |


---

## 31. Risks

| Risk | Mitigation |
|---|---|
| **Technical**: Docker Sandbox Escape | Use gVisor or strict seccomp profiles limiting syscalls in the runner container. |
| **AI**: VRAM Exhaustion | Enforce strict batch size limits and queue throttling in RabbitMQ. |
| **Business**: Low User Adoption | Provide extensive onboarding and ensure UI hides AI complexity. |

---

## 32. Future Requirements

### FUT-01: Multi-Tenancy
- **Description**: The database schema SHALL isolate data by `TenantId` to prepare for future SaaS capabilities, even in initial single-tenant deployments.

### FUT-02: Plugin Ecosystem
- **Description**: The AI worker architecture SHALL be designed to accept external Python modules dynamically for custom institutional evaluations.

---

## 33. Glossary

- **Evidence Graph**: A JSON structure linking a generated AI assertion directly to a byte-offset or substring in the original source document.
- **Modular Monolith**: An architectural pattern where all business logic resides in a single deployable backend, but is strictly isolated into namespaces/modules.
- **RAG**: Retrieval-Augmented Generation.

---

## 34. Appendices

### A. Approval Matrix
| Role | Signature | Date |
|---|---|---|
| CTO / Chief Software Architect | *System Approved* | 2026-07-19 |
| Product Manager | *System Approved* | 2026-07-19 |

### B. Standards Compliance
This document adheres to IEEE 29148:2018 guidelines for Software Requirements Specifications.

***END OF SOFTWARE REQUIREMENTS SPECIFICATION***

