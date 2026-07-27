# Enterprise Resume Intelligence Agent Guide (`resume-parser-v2`)

> Phase 6 Pipeline introducing the first Local AI Agent in FacultyIQ (`app/resume_agent/`), integrating Ollama LLM models, RAG institutional policy context, evidence citations, and anti-hallucination guardrails.

---

## 🏛️ Local AI Agent Architecture

```
            Candidate Intelligence Report (Phase 5 Output) + Job Description
                                        │
                                        ▼
                        [1. Institutional Policy RAG Engine]         <-- Retrieves hiring rules & guidelines
                                        │
                                        ▼
                         [2. Prompt Builder Engine]                  <-- Builds structured LLM prompt
                                        │
                                        ▼
                     [3. Ollama LLM Connection Adapter]             <-- Connects to llama3.2, qwen2.5, gemma, phi
                                        │
                                        ▼
                        [4. JSON Validator & Auto-Repair]            <-- Enforces Pydantic v2 schema compliance
                                        │
                                        ▼
                       [5. Anti-Hallucination Guardrails]            <-- Rejects unbacked publication claims
                                        │
                                        ▼
                       [6. Evidence Citation Engine]                 <-- Attaches citation IDs & confidence
                                        │
                                        ▼
                    Final AIResumeIntelligenceReport JSON Payload
```

---

## 🔌 API Endpoint

### `POST /api/v1/resume/agent/analyze`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `AgentAnalysisRequest`

#### cURL Example:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/resume/agent/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "intelligence_report": { ... CandidateIntelligenceReport JSON ... },
    "department_name": "Computer Science & Engineering",
    "preferred_model": "llama3.2"
  }'
```

#### Example Output (`AIResumeIntelligenceReport` JSON):

```json
{
  "success": true,
  "message": "Local AI Agent reasoning for candidate 'Dr. Ananya Roy' completed using model 'llama3.2-fallback'.",
  "data": {
    "agent_report_id": "c1f7a2b3-9481-4952-b103-9d18bfa92301",
    "document_uuid": "agent_doc_100",
    "candidate_name": "Dr. Ananya Roy",
    "reasoning": {
      "professional_summary": "Candidate demonstrates strong academic and technical experience.",
      "research_highlights": [
        "Verified scholarly publications with active research focus."
      ],
      "teaching_profile": [
        "Demonstrates core teaching experience in undergraduate curriculum."
      ],
      "academic_strengths": [
        "Strong foundational publications",
        "Verified institutional experience"
      ],
      "areas_for_improvement": [
        "Expand international conference presentations"
      ],
      "interview_preparation_notes": [
        "Assess core research domain vision and departmental teaching load alignment."
      ]
    },
    "citations": [
      {
        "citation_id": "cite_001",
        "source_field": "candidate_name",
        "extracted_value": "Dr. Ananya Roy",
        "confidence": 1.0
      },
      {
        "citation_id": "cite_002",
        "source_field": "research.publication_count",
        "extracted_value": "5",
        "confidence": 1.0
      }
    ],
    "overall_agent_confidence": 0.95,
    "token_metrics": {
      "prompt_tokens": 200,
      "completion_tokens": 150,
      "total_tokens": 350,
      "latency_ms": 1.85,
      "model_name": "llama3.2-fallback"
    },
    "deterministic_score_summary": {
      "resume_quality": 0.92,
      "research_strength": 0.85,
      "teaching_strength": 0.9
    },
    "processing_time_ms": 12.45
  }
}
```
