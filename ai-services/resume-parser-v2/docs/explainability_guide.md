# Enterprise Explainability, Audit & Evidence Intelligence Engine Guide (`resume-parser-v2`)

> Phase 10 Pipeline establishing complete transparency, auditability, legal defensibility, and evidence lineage for faculty recruitment decisions.

---

## 🏛️ Governance Architecture

```
                    Recruitment Decision Report (Phase 9 Output)
                                         │
                                         ▼
                           [1. Audit Engine]                       <-- Immutable audit record, hash, LLM model version
                                         │
                                         ▼
                           [2. 9-Stage Timeline Builder]          <-- Complete processing chronology
                                         │
                                         ▼
                           [3. Traceability Engine]               <-- Maps score explanations to evidence
                                         │
                                         ▼
                           [4. Compliance Validator]              <-- Verifies evidence completeness & policies
                                         │
                                         ▼
                           [5. Report Generator Engine]           <-- Multi-audience report synthesis
                                         │
                                         ▼
                           [6. Audit Repository Service]          <-- In-memory & persistent storage
                                         │
                                         ▼
                    Final ExplainabilityReport JSON Payload
```

---

## 🔌 API Endpoints

### 1. `POST /api/v1/explainability/report`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `ExplainabilityRequest`

#### cURL Example:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/explainability/report' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "decision_report": { ... RecruitmentDecisionReport JSON ... },
    "initiator_id": "admin_user_1"
  }'
```

---

### 2. `GET /api/v1/audit/{decision_id}`

Fetches immutable audit log containing timestamp, configuration hash, model version, and citation IDs.

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/audit/test_dec_007'
```

---

### 3. `GET /api/v1/evidence/{candidate_id}`

Fetches complete evidence citations and pipeline stage timeline.

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/evidence/test_dec_007'
```

---

#### Example Output (`ExplainabilityReport` JSON):

```json
{
  "success": true,
  "message": "Explainability and audit report for candidate 'Dr. Vikram Sharma' generated successfully.",
  "data": {
    "report_id": "7a8b9c0d-1234-5678-90ab-cdef12345678",
    "decision_id": "test_dec_007",
    "document_uuid": "doc_exp_007",
    "candidate_name": "Dr. Vikram Sharma",
    "position_title": "Professor",
    "decision_summary": {
      "candidate_name": "Dr. Vikram Sharma",
      "position_title": "Professor",
      "recommendation": "Highly Recommended",
      "confidence_pct": 95,
      "summary": "Candidate meets all qualifications.",
      "risk_level": "Low"
    },
    "explanations": [
      {
        "metric_name": "Final Recommendation",
        "score_or_value": "Highly Recommended",
        "explanation_text": "Synthesized by Multi-Agent Consensus with confidence 95%.",
        "supporting_evidence": [
          "Matching Overall Score: 95%",
          "Qualification Score: 100%"
        ]
      }
    ],
    "audit": {
      "audit_id": "e1f2g3h4-5678-90ab-cdef-1234567890ab",
      "decision_id": "test_dec_007",
      "candidate_name": "Dr. Vikram Sharma",
      "initiator_id": "admin_user_1",
      "config_hash": "v2.0.0-sha256",
      "prompt_version": "v1.0",
      "llm_model": "llama3.2",
      "rag_sources_count": 3
    },
    "timeline": [
      { "stage_number": 1, "stage_name": "Document Upload & Fingerprinting", "status": "COMPLETED" },
      { "stage_number": 9, "stage_name": "Multi-Agent Recruitment Decision Agent", "status": "COMPLETED" }
    ],
    "compliance": {
      "is_compliant": true,
      "evidence_completeness_pct": 100.0,
      "policy_violations": [],
      "unbacked_claims": []
    },
    "versioning": {
      "system_version": "2.0.0",
      "pipeline_build": "FacultyIQ-V2-Production",
      "python_version": "3.12"
    },
    "processing_time_ms": 11.8
  }
}
```
