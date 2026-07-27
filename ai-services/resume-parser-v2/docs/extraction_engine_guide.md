# Enterprise Deterministic Information Extraction Engine Guide (`resume-parser-v2`)

> Phase 4 Pipeline converting `SemanticResumeModel` into canonical `StructuredCandidateProfile` & `CandidateKnowledgeGraph` with zero hallucination and 100% evidence lineage.

---

## 🏛️ Pipeline Architecture

```
                    Semantic Resume Model (Phase 3 Output)
                                       │
                                       ▼
                     [10 Domain Extractors Pipeline]
  ┌────────────────────────────────────┼──────────────────────────────────┐
  │                                    │                                  │
  ▼                                    ▼                                  ▼
[Contact Extractor]          [Experience Extractor]           [Education Extractor]
 (Name, Email, Phone,         (Title, Org, Dates,              (Degree, Inst, CGPA,
  LinkedIn, ORCID, Scholar)    Current, Duration)               Supervisors, Years)
  │                                    │                                  │
  ▼                                    ▼                                  ▼
[Skill Extractor]            [Project Extractor]              [Publication Extractor]
 (Languages, Frameworks,      (Title, Role, Tech,              (Paper Title, Authors,
  Databases, Cloud, AI/ML)     Demo URLs)                       Venue, Year, DOI)
  │                                    │                                  │
  ▼                                    ▼                                  ▼
[Certifications Extractor]   [Award Extractor]                [Reference Extractor]
 (Title, Issuer, ID)          (Title, Year, Org)               (Name, Title, Email)
  └────────────────────────────────────┬──────────────────────────────────┘
                                       │
                                       ▼
                       [Relationship & KG Engine]
                   (Candidate -> WorkedAt -> StudiedAt -> HasSkill)
                                       │
                                       ▼
                  Final StructuredCandidateProfile JSON Payload
```

---

## 🔒 Zero-Hallucination & Evidence Provenance Guarantee

Every extracted field is wrapped in `ExtractedField[T]`:
```json
{
  "value": "r.kumar@nitap.ac.in",
  "raw_text": "email: r.kumar@nitap.ac.in",
  "normalized_value": "r.kumar@nitap.ac.in",
  "confidence": 0.98,
  "rule_id": "pattern_match",
  "evidence": [
    {
      "page_number": 1,
      "line_number": 3,
      "bounding_box": { "x0": 50.0, "y0": 50.0, "x1": 550.0, "y1": 70.0 }
    }
  ]
}
```
If no explicit evidence exists in text, the engine returns `null` or an empty list.

---

## 🔌 API Endpoint

### `POST /api/v1/resume/extract`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `SemanticResumeModel`

#### cURL Example:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/resume/extract' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ ... SemanticResumeModel JSON ... }'
```

#### Example Output (`StructuredCandidateProfile` JSON):

```json
{
  "success": true,
  "message": "Candidate profile for 'dr_rajesh_cv.pdf' extracted cleanly (1 jobs, 1 degrees).",
  "data": {
    "document_uuid": "test_doc_extract_999",
    "filename": "dr_rajesh_cv.pdf",
    "contact": {
      "full_name": { "value": "Rajesh Kumar", "confidence": 0.92 },
      "email": { "value": "r.kumar@nitap.ac.in", "confidence": 0.98 },
      "phone": { "value": "+91-9876543210", "confidence": 0.95 },
      "orcid": { "value": "0000-0002-1825-0097", "confidence": 0.99 }
    },
    "education": [
      {
        "degree": { "value": "Ph.D.", "confidence": 0.95 },
        "institution": { "value": "Indian Institute of Technology Delhi", "confidence": 0.90 },
        "cgpa": { "value": 9.4, "confidence": 0.98 }
      }
    ],
    "experience": [
      {
        "designation": { "value": "Professor", "confidence": 0.90 },
        "organization": { "value": "NIT Andhra Pradesh", "confidence": 0.88 },
        "is_current": true
      }
    ],
    "skills": [
      {
        "category_name": "Programming Languages",
        "skills": [{ "value": "Python", "confidence": 0.98 }, { "value": "Java", "confidence": 0.98 }]
      }
    ],
    "publications": [
      {
        "title": { "value": "Kumar, R. (2025). Multi-Agent Systems in Recruitment...", "confidence": 0.85 },
        "doi": { "value": "10.1016/j.artint.2025.10398", "confidence": 0.99 }
      }
    ],
    "knowledge_graph": {
      "nodes": [
        { "node_id": "cand_test_doc", "entity_type": "Candidate", "name": "Candidate Profile" },
        { "node_id": "org_1a2b3c4d", "entity_type": "Company", "name": "NIT Andhra Pradesh" },
        { "node_id": "sk_python", "entity_type": "Skill", "name": "Python" }
      ],
      "edges": [
        { "source_id": "cand_test_doc", "target_id": "org_1a2b3c4d", "relation": "WORKED_AT" },
        { "source_id": "cand_test_doc", "target_id": "sk_python", "relation": "HAS_SKILL" }
      ]
    },
    "processing_time_ms": 15.65
  }
}
```
