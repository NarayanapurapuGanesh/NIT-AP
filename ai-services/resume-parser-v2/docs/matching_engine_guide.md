# Enterprise Candidate–Job Matching Engine Guide (`resume-parser-v2`)

> Phase 8 Pipeline comparing `StructuredCandidateProfile` against `JobIntelligenceModel` to generate a 100% deterministic, explainable `CandidateMatchReport`.

---

## 🏛️ Pipeline Architecture

```
         Candidate Profile (Phase 4/5 Output)  +  Job Profile (Phase 7 Output)
                                           │
                                           ▼
                      [1. 8 Deterministic Component Matchers]
  ┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
  │                      │                      │                      │                      │
  ▼                      ▼                      ▼                      ▼                      ▼
[Qualification Matcher]  [Experience Matcher]    [Skills Matcher]      [Research Matcher]     [Teaching Matcher]
 (Degree & Ph.D. check) (Tenure threshold check)(Mandatory skills %)(Publications & DOIs) (Subject overlap)
  └──────────────────────┴──────────────────────┼──────────────────────┴──────────────────────┘
                                                │
                                                ▼
                             [2. Gap Analysis Engine]                 <-- Identifies Ph.D. & experience deficits
                                                │
                                                ▼
                             [3. Weighted Scoring Engine]             <-- Calculates Overall Score (0-100%)
                                                │
                                                ▼
                             [4. Ranking Feature Generator]           <-- Strengths, weaknesses & critical gaps
                                                │
                                                ▼
                             [5. Match Evidence Attacher]             <-- Field citations & confidence scores
                                                │
                                                ▼
                            Final CandidateMatchReport JSON Payload
```

---

## 🔌 API Endpoint

### `POST /api/v1/matching/analyze`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `MatchAnalysisRequest`

#### cURL Example:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/matching/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "candidate_profile": { ... StructuredCandidateProfile JSON ... },
    "job_profile": { ... JobIntelligenceModel JSON ... }
  }'
```

#### Example Output (`CandidateMatchReport` JSON):

```json
{
  "success": true,
  "message": "Matching for 'Dr. Ananya Roy' against 'Assistant Professor' complete (Overall Score: 84%).",
  "data": {
    "match_id": "a9b8c7d6-1234-5678-90ab-cdef12345678",
    "document_uuid": "cand_match_001",
    "job_uuid": "job_match_001",
    "candidate_name": "Dr. Ananya Roy",
    "position_title": "Assistant Professor",
    "overall_score": 0.84,
    "score_breakdown": {
      "qualification_score": 1.0,
      "experience_score": 1.0,
      "research_score": 0.6,
      "teaching_score": 1.0,
      "skills_score": 1.0,
      "publication_score": 1.0,
      "certification_score": 0.7,
      "domain_score": 0.95,
      "overall_score": 0.84
    },
    "strengths": [
      "Meets highest academic qualification requirements (Ph.D. degree present)."
    ],
    "weaknesses": [],
    "critical_gaps": [],
    "matched_requirements": [
      {
        "requirement_name": "Ph.D. Qualification",
        "is_met": true,
        "candidate_value": "Ph.D. Degree present",
        "required_value": "Ph.D. Mandatory",
        "confidence": 1.0
      }
    ],
    "unmatched_requirements": [],
    "evidence": [
      {
        "evidence_id": "e1f2g3h4-...",
        "source_field": "education.degree",
        "extracted_text": "Ph.D.",
        "rule_id": "degree_matching"
      }
    ],
    "processing_time_ms": 14.5
  }
}
```
