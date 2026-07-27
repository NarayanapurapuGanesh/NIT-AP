# Enterprise Resume Intelligence & Validation Engine Guide (`resume-parser-v2`)

> Phase 5 Pipeline performing 100% deterministic rule-based analysis on `StructuredCandidateProfile` to generate canonical `CandidateIntelligenceReport`.

---

## 🏛️ Pipeline Flowchart

```
                 Structured Candidate Profile (Phase 4 Output)
                                       │
                                       ▼
                         [1. Profile Validator Engine]              <-- Required fields & contact checks
                                       │
                                       ▼
                       [2. Timeline & Gap Analysis Engine]         <-- Total experience, gaps, job & edu overlaps
                                       │
                                       ▼
                       [3. 7-Domain Intelligence Engines]
  ┌───────────────────┬───────────────────┼───────────────────┬───────────────────┐
  │                   │                   │                   │                   │
  ▼                   ▼                   ▼                   ▼                   ▼
[Employment Intel]   [Education Intel]   [Skill Intel]       [Research Intel]   [Teaching Intel]
 (Tenure, stability)  (Highest degree)   (Skill diversity)   (DOIs, citations)   (Academic rank)
  └───────────────────┴───────────────────┼───────────────────┴───────────────────┘
                                          │
                                          ▼
                         [4. Consistency & Anomaly Engine]          <-- Conflicting dates, duplicate jobs/skills
                                          │
                                          ▼
                         [5. Lineage Evidence Verifier]             <-- Flags unbacked values as UNVERIFIED
                                          │
                                          ▼
                        [6. Resume Quality & Scoring Engine]        <-- Mathematical quality & strength scores
                                          │
                                          ▼
                         [7. Deterministic Recommendation]          <-- Gaps, missing URLs, weak evidence recs
                                          │
                                          ▼
                      Final CandidateIntelligenceReport JSON Payload
```

---

## 🔌 API Endpoint

### `POST /api/v1/resume/intelligence`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `StructuredCandidateProfile`

#### cURL Example:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/resume/intelligence' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ ... StructuredCandidateProfile JSON ... }'
```

#### Example Output (`CandidateIntelligenceReport` JSON):

```json
{
  "success": true,
  "message": "Candidate intelligence report generated for 'Dr. Vikram Sharma' (Quality Score: 96%).",
  "data": {
    "report_uuid": "e9a8b7c6-48c2-4b36-a192-3ef4861bc978",
    "document_uuid": "intel_doc_999",
    "filename": "vikram_cv.pdf",
    "candidate_name": "Dr. Vikram Sharma",
    "scores": {
      "completeness_score": 1.0,
      "data_quality_score": 1.0,
      "evidence_strength_score": 0.95,
      "resume_quality_score": 0.96,
      "research_strength_score": 0.5,
      "teaching_strength_score": 0.9,
      "industry_strength_score": 0.3,
      "technical_strength_score": 0.3,
      "validation_score": 1.0
    },
    "timeline": {
      "total_experience_years": 2.0,
      "research_experience_years": 0.0,
      "teaching_experience_years": 2.0,
      "industry_experience_years": 0.0,
      "career_gap_count": 0,
      "has_education_overlap": false,
      "has_job_overlap": false,
      "average_job_tenure_months": 24.0
    },
    "research": {
      "publication_count": 1,
      "doi_count": 1,
      "citations_total": 0,
      "research_domains": ["Computer Science", "Artificial Intelligence"],
      "has_recent_publication": true,
      "research_continuity_score": 0.6
    },
    "teaching": {
      "has_teaching_experience": true,
      "highest_academic_rank": "Professor",
      "subjects_count": 2,
      "has_administrative_roles": false,
      "teaching_score": 0.9
    },
    "consistency": {
      "is_consistent": true,
      "duplicate_companies": [],
      "duplicate_skills": []
    },
    "anomalies": {
      "has_anomalies": false,
      "invalid_cgpa_entries": []
    },
    "recommendations": [
      "Add LinkedIn profile URL to improve candidate contact completeness."
    ],
    "metrics_summary": {
      "years_experience": 2.0,
      "highest_qualification": "Ph.D.",
      "has_phd": true
    },
    "processing_time_ms": 14.85
  }
}
```
