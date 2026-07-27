# Enterprise Recruitment Workflow Orchestrator Guide (`resume-parser-v2`)

> Phase 12 Pipeline coordinating the complete faculty recruitment lifecycle across 16 formal FSM states, human-in-the-loop approvals, event publishing, multi-channel notifications, and audit logging.

---

## 🏛️ State Machine & Workflow Architecture

```
                                  16 Formal FSM States
  ┌───────────┐      ┌───────────┐      ┌───────────────────┐      ┌───────────┐
  │   Draft   │ ---> │ Published │ ---> │ Applications Open │ ---> │ Screening │
  └───────────┘      └───────────┘      └───────────────────┘      └───────────┘
                                                                         │
  ┌───────────────────┐      ┌────────────┐      ┌───────────┐          │
  │ Human Review / AI │ <--- │ AI Review  │ <--- │ Matching  │ <────────┘
  └───────────────────┘      └────────────┘      └───────────┘
            │
            ▼
  ┌─────────────────────┐      ┌─────────────────────┐      ┌──────────────────┐
  │ Interview Scheduled │ ---> │ Interview Completed │ ---> │ Committee Review │
  └─────────────────────┘      └─────────────────────┘      └──────────────────┘
                                                                      │
  ┌────────┐      ┌────────────────┐      ┌───────────────┐          │
  │ Closed │ <--- │ Offer Accepted │ <--- │ Offer Pending │ <────────┘
  └────────┘      └────────────────┘      └───────────────┘
```

---

## 🔌 API Endpoints

### 1. `POST /api/v1/workflow/start`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `WorkflowStartRequest`

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/workflow/start' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "job_uuid": "job_101",
    "candidate_uuid": "cand_101",
    "workflow_type": "Faculty Recruitment"
  }'
```

---

### 2. `POST /api/v1/workflow/action`

Executes a human or AI workflow action and advances FSM state.

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/workflow/action' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "workflow_id": "wf_101",
    "action": "Override",
    "actor_id": "dean_academic",
    "override_decision": "Recommended",
    "comments": "Approved after reviewing publication impact."
  }'
```

---

### 3. `GET /api/v1/workflow/{workflow_id}`

Fetches current state, pending tasks, approvals, and notifications.

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/workflow/wf_101'
```

---

### 4. `GET /api/v1/workflow/history/{workflow_id}`

Fetches complete state transition history log with timestamps and triggers.

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/workflow/history/wf_101'
```

---

#### Example Output (`WorkflowStatusReport` JSON):

```json
{
  "success": true,
  "message": "Recruitment workflow 'wf_101' started (Current State: Applications Open).",
  "data": {
    "workflow_id": "wf_101",
    "job_uuid": "job_101",
    "candidate_uuid": "cand_101",
    "workflow_type": "Faculty Recruitment",
    "current_state": "Applications Open",
    "completed_steps": ["Draft"],
    "pending_tasks": [
      {
        "task_id": "t1",
        "task_type": "Approval",
        "title": "Publish Job Description",
        "assignee_role": "Dean Academic",
        "is_completed": false
      }
    ],
    "approvals": [],
    "history": [
      {
        "transition_id": "tr_1",
        "from_state": "Published",
        "to_state": "Applications Open",
        "triggered_by": "system_admin"
      }
    ],
    "notifications": [
      {
        "channel": "Email",
        "recipient": "committee@nitap.ac.in",
        "subject": "New Workflow Started: Faculty Recruitment",
        "is_sent": true
      }
    ],
    "processing_time_ms": 16.4
  }
}
```
