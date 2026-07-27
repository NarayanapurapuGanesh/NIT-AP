# Enterprise Job Description Intelligence Engine Guide (`resume-parser-v2`)

> Phase 7 Pipeline converting raw Faculty Job Descriptions into structured `JobIntelligenceModel` representations with requirement weights and evidence lineage.

---

## 🏛️ Pipeline Architecture

```
                      Raw Job Description (PDF / DOCX / TXT / HTML)
                                            │
                                            ▼
                           [1. JD Section Detector Engine]          <-- Identifies Qualifications, Skills, Research
                                            │
                                            ▼
                       [2. 10 Requirement Extractor Modules]
  ┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
  │                      │                      │                      │                      │
  ▼                      ▼                      ▼                      ▼                      ▼
[Qualification Extractor] [Experience Extractor]  [Skill Extractor]     [Research Extractor]  [Teaching Extractor]
 (Ph.D., M.Tech, Branch) (Min total/teach yrs)  (Mandatory/preferred)  (Scopus/SCI, patents)  (Subjects & labs)
  └──────────────────────┴──────────────────────┼──────────────────────┴──────────────────────┘
                                                │
                                                ▼
                             [3. Requirement Weight Engine]          <-- Deterministic matching weight matrix
                                                │
                                                ▼
                             [4. Evidence Provenance Linker]         <-- Line evidence attachment
                                                │
                                                ▼
                           Final JobIntelligenceModel JSON Payload
```

---

## 🔌 API Endpoint

### `POST /api/v1/job/analyze`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `JobAnalysisRequest`

#### cURL Example:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/job/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "job_description_text": "NIT AP Recruitment for Assistant Professor in CSE. Ph.D. mandatory. Minimum 3 years experience. Python, Machine Learning required.",
    "job_title": "Assistant Professor in CSE"
  }'
```

#### Example Output (`JobIntelligenceModel` JSON):

```json
{
  "success": true,
  "message": "Job Description for 'Assistant Professor in CSE' analyzed successfully (Ph.D. minimum qualification).",
  "data": {
    "job_uuid": "f18a2b3c-49d2-4b71-b921-8e9d8c7b6a54",
    "filename_or_title": "Assistant Professor in CSE",
    "institution": {
      "name": "NIT Andhra Pradesh",
      "department": "Computer Science & Engineering",
      "institution_type": "University"
    },
    "position": {
      "title": "Assistant Professor in CSE",
      "employment_type": "Full-Time",
      "academic_rank": "Assistant Professor"
    },
    "qualification": {
      "minimum_degree": "Ph.D.",
      "preferred_degree": "Ph.D.",
      "branch_or_specialization": ["Computer Science & Engineering"],
      "is_phd_mandatory": true
    },
    "experience": {
      "min_total_experience_years": 3.0,
      "min_teaching_experience_years": 3.0,
      "min_research_experience_years": 0.0,
      "min_industry_experience_years": 0.0
    },
    "skills": {
      "mandatory_skills": ["Python", "Machine Learning"],
      "preferred_skills": []
    },
    "research": {
      "min_publications_count": 3,
      "scopus_sci_mandatory": true,
      "patents_required": false,
      "funded_projects_required": false,
      "preferred_research_domains": ["Computer Science", "Artificial Intelligence"]
    },
    "teaching": {
      "subjects": ["Data Structures & Algorithms"],
      "course_levels": ["UG", "PG"],
      "lab_guidance_required": false
    },
    "responsibilities": {
      "teaching_responsibilities": ["Deliver undergraduate and postgraduate lectures."],
      "research_responsibilities": ["Conduct independent research and publish in indexed journals."],
      "administrative_responsibilities": ["Participate in departmental committee work."]
    },
    "weights": {
      "education_weight": 0.3,
      "experience_weight": 0.15,
      "research_weight": 0.25,
      "teaching_weight": 0.15,
      "skills_weight": 0.15
    },
    "processing_time_ms": 11.25
  }
}
```
