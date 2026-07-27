# Enterprise Interview Intelligence & Assessment System Guide (`resume-parser-v2`)

> Phase 11 Pipeline generating multi-round interview plans, Bloom's Taxonomy-aligned question sets, 5-level evaluation rubrics, panel assignments, and AI-assisted response scoring.

---

## 🏛️ System Architecture

```
                  Recruitment Decision Report (Phase 9 Output)
                                       │
                                       ▼
                     [1. Multi-Round Workflow Planner]              <-- Technical, Teaching Demo, Research, HR
                                       │
                                       ▼
                     [2. Bloom's Taxonomy Question Generator]       <-- Remember, Apply, Analyze, Evaluate, Create
                                       │
                                       ▼
                     [3. 5-Level Rubric Generator]                  <-- 1 (Unsatisfactory) to 5 (Exemplary)
                                       │
                                       ▼
                     [4. Panel Management Engine]                   <-- Department & External Experts
                                       │
                                       ▼
                     [5. Response Evaluator & Scoring Engine]       <-- Aggregates scores & updates recommendation
                                       │
                                       ▼
                      Final InterviewPlanReport JSON Payload
```

---

## 🔌 API Endpoints

### 1. `POST /api/v1/interview/plan`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `InterviewPlanRequest`

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/interview/plan' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "decision_report": { ... RecruitmentDecisionReport JSON ... },
    "department_name": "Computer Science & Engineering"
  }'
```

---

### 2. `POST /api/v1/interview/questions`

Generates Bloom's Taxonomy questions mapped to candidate profile topics.

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/interview/questions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "candidate_name": "Dr. Vikram Sharma",
    "position_title": "Professor",
    "topics": ["Distributed Systems", "Machine Learning"]
  }'
```

---

### 3. `POST /api/v1/interview/evaluate`

Evaluates panel scores and candidate interview responses.

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/interview/evaluate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "plan_id": "f8e7d6c5-4321-8765-09ba-fedcba987654",
    "responses": [
      { "question_id": "q1", "candidate_answer_text": "Detailed distributed architecture...", "score": 4 }
    ]
  }'
```

---

### 4. `GET /api/v1/interview/report/{id}`

Fetches complete interview plan report and rubrics.

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/interview/report/f8e7d6c5-4321-8765-09ba-fedcba987654'
```

---

#### Example Output (`InterviewPlanReport` JSON):

```json
{
  "success": true,
  "message": "Interview plan for candidate 'Dr. Vikram Sharma' generated successfully (4 rounds).",
  "data": {
    "plan_id": "f8e7d6c5-4321-8765-09ba-fedcba987654",
    "candidate_name": "Dr. Vikram Sharma",
    "position_title": "Professor",
    "rounds": [
      { "round_name": "Technical Interview", "duration_mins": 45 },
      { "round_name": "Teaching Demonstration", "duration_mins": 30 },
      { "round_name": "Research Presentation", "duration_mins": 45 },
      { "round_name": "Panel Discussion & HR", "duration_mins": 30 }
    ],
    "question_sets": [
      {
        "category": "Technical",
        "question_text": "How would you design a distributed indexing pipeline...",
        "competency": "Problem Solving & Algorithm Design",
        "difficulty": "Hard",
        "blooms_level": "Apply",
        "expected_duration_mins": 8,
        "expected_answer_guidelines": "Candidate should outline inverted indexing..."
      }
    ],
    "rubrics": [
      { "dimension_name": "Subject Matter Knowledge", "description": "Evaluates candidate's level..." }
    ],
    "panel": [
      { "name": "Prof. HOD", "role": "Panel Chair", "institution": "NIT AP" }
    ],
    "processing_time_ms": 14.2
  }
}
```
