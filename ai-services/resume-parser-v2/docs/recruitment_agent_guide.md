# Enterprise AI Recruitment Decision Agent Guide (`resume-parser-v2`)

> Phase 9 Pipeline establishing multi-agent AI collaboration across 9 Specialist Agents to produce explainable faculty hiring recommendations backed by evidence provenance.

---

## 🏛️ Multi-Agent Architecture

```
        Candidate Match Report (Phase 8) + Candidate Intelligence (Phase 5) + Job Model (Phase 7)
                                                  │
                                                  ▼
                                     [Coordinator Agent]
  ┌─────────────────┬─────────────────┬───────────┴───────────┬─────────────────┬─────────────────┐
  │                 │                 │                       │                 │                 │
  ▼                 ▼                 ▼                       ▼                 ▼                 ▼
[Qualification]   [Experience]     [Teaching]              [Research]       [Skills]       [Risk Assessment]
 Agent             Agent            Agent                   Agent            Agent          Agent
  └─────────────────┴─────────────────┴───────────┬───────────┴─────────────────┴─────────────────┘
                                                  │
                                                  ▼
                                    [Consensus & Guardrails]             <-- Rejects unsupported claims & gap overrides
                                                  │
                                                  ▼
                                    [Institutional RAG Policy]           <-- Retrieves evaluation rubrics
                                                  │
                                                  ▼
                             Final RecruitmentDecisionReport JSON Payload
```

---

## 🔌 API Endpoint

### `POST /api/v1/recruitment/decision`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `DecisionRequest`

#### cURL Example:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/recruitment/decision' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "match_report": { ... CandidateMatchReport JSON ... },
    "department_name": "Computer Science & Engineering",
    "preferred_model": "llama3.2"
  }'
```

#### Example Output (`RecruitmentDecisionReport` JSON):

```json
{
  "success": true,
  "message": "AI Recruitment Decision for candidate 'Dr. Ananya Roy' complete (Recommendation: Highly Recommended).",
  "data": {
    "decision_id": "b1a2c3d4-5678-90ab-cdef-1234567890ab",
    "document_uuid": "dec_doc_001",
    "job_uuid": "dec_job_001",
    "candidate_name": "Dr. Ananya Roy",
    "position_title": "Assistant Professor",
    "recommendation": "Highly Recommended",
    "overall_confidence": 0.92,
    "summary": "Multi-agent evaluation completed cleanly with evidence provenance.",
    "strengths": [
      "Meets highest academic qualification requirements (Ph.D. degree present)."
    ],
    "weaknesses": [],
    "risks": {
      "risk_level": "Low",
      "risk_factors": ["No critical risks identified."],
      "mitigation_strategies": []
    },
    "interview_focus": [
      {
        "category": "Technical & Research",
        "focus_topics": [
          "Technical Depth & Research Vision",
          "Pedagogical Delivery & Lab Guidance"
        ]
      }
    ],
    "specialist_opinions": [
      {
        "agent_name": "Qualification Agent",
        "opinion": "Academic qualification score is 100%. Meets degree requirements.",
        "confidence": 1.0,
        "recommendation": "Highly Recommended"
      },
      {
        "agent_name": "Research Agent",
        "opinion": "Research score is 85%. Verified scholarly publications.",
        "confidence": 0.85,
        "recommendation": "Highly Recommended"
      }
    ],
    "evidence": [
      "Matching Overall Score: 92%",
      "Qualification Score: 100%",
      "Research Score: 85%",
      "Matched Requirements Count: 1"
    ],
    "processing_time_ms": 15.2
  }
}
```
