"""
Canonical Pydantic v2 Models for Enterprise Recruitment Workflow Orchestrator.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class TaskItem(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = Field(default="Human Review")  # Human Review, AI Review, Approval, Background
    title: str
    assignee_role: str = "Hiring Committee Chair"
    is_completed: bool = False
    due_date: Optional[datetime] = None


class ApprovalRecord(BaseModel):
    approval_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str
    actor_role: str
    action: str  # Approved, Rejected, Overridden, ReEvaluationRequested
    original_ai_decision: str = "Recommended"
    final_human_decision: str = "Recommended"
    comments: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StateTransitionRecord(BaseModel):
    transition_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_state: str
    to_state: str
    triggered_by: str = "system"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NotificationRecord(BaseModel):
    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel: str = "Email"  # Email, SMS, In-App, Webhook
    recipient: str
    subject: str
    body: str
    is_sent: bool = True
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowStatusReport(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_uuid: str
    candidate_uuid: Optional[str] = None
    workflow_type: str = "Faculty Recruitment"
    current_state: str = "Draft"
    completed_steps: List[str] = Field(default_factory=list)
    pending_tasks: List[TaskItem] = Field(default_factory=list)
    approvals: List[ApprovalRecord] = Field(default_factory=list)
    history: List[StateTransitionRecord] = Field(default_factory=list)
    notifications: List[NotificationRecord] = Field(default_factory=list)
    audit: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0


class WorkflowStartRequest(BaseModel):
    job_uuid: str
    candidate_uuid: Optional[str] = None
    workflow_type: str = Field(default="Faculty Recruitment")  # Faculty Recruitment, Research Faculty, Adjunct Faculty, Guest Faculty, Visiting Faculty
    initiator_id: str = Field(default="system_admin")


class WorkflowActionRequest(BaseModel):
    workflow_id: str
    action: str  # Approve, Reject, Override, AdvanceState
    actor_id: str = Field(default="committee_member")
    comments: Optional[str] = ""
    override_decision: Optional[str] = None
