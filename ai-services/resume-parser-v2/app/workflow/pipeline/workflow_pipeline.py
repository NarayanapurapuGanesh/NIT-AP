"""
End-to-End Enterprise Recruitment Workflow Pipeline.
Orchestrates 16-State FSM, Multi-Workflow Execution, Human Approvals, Event Bus Publishing,
Notifications, Escalation Monitoring, and Persistent History Audit Logging.
"""

import time
from typing import Optional
from app.workflow.approvals.approval_engine import HumanApprovalEngine
from app.workflow.escalation.escalation_engine import EscalationEngine
from app.workflow.events.event_bus import EventBusEngine
from app.workflow.notifications.notification_engine import NotificationEngine
from app.workflow.orchestrator.workflow_orchestrator import WorkflowOrchestratorEngine
from app.workflow.rules.rule_engine import WorkflowRuleEngine
from app.workflow.schemas.workflow_models import (
    WorkflowActionRequest,
    WorkflowStartRequest,
    WorkflowStatusReport,
)
from app.workflow.services.workflow_service import WorkflowRepositoryService
from app.workflow.state_machine.state_machine import RecruitmentStateMachine
from core.logging import get_logger

logger = get_logger("workflow_pipeline")


class WorkflowPipeline:
    """Enterprise Recruitment Workflow Pipeline Engine."""

    def __init__(self) -> None:
        self.state_machine = RecruitmentStateMachine()
        self.orchestrator = WorkflowOrchestratorEngine()
        self.approval_engine = HumanApprovalEngine()
        self.event_bus = EventBusEngine()
        self.notification_engine = NotificationEngine()
        self.escalation_engine = EscalationEngine()
        self.rule_engine = WorkflowRuleEngine()
        self.repository_service = WorkflowRepositoryService.get_instance()

    async def start_recruitment_workflow(
        self, request: WorkflowStartRequest
    ) -> WorkflowStatusReport:
        """Starts a new recruitment workflow."""
        start_time = time.perf_counter()

        status_report = self.orchestrator.initialize_workflow(
            job_uuid=request.job_uuid,
            candidate_uuid=request.candidate_uuid,
            workflow_type=request.workflow_type,
        )

        # Transition to Applications Open
        t_record = self.state_machine.transition_state("Published", "Applications Open", request.initiator_id)
        status_report.current_state = "Applications Open"
        status_report.history.append(t_record)

        # Publish Event & Notify
        self.event_bus.publish_event("WorkflowStarted", {"workflow_id": status_report.workflow_id, "job_uuid": request.job_uuid})
        notif = self.notification_engine.send_notification("committee@nitap.ac.in", f"New Workflow Started: {request.workflow_type}", "Recruitment workflow initiated cleanly.")
        status_report.notifications.append(notif)

        status_report.processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        self.repository_service.save_workflow(status_report)

        logger.info(
            "Workflow started cleanly",
            workflow_id=status_report.workflow_id,
            state=status_report.current_state,
            duration_ms=status_report.processing_time_ms,
        )

        return status_report

    async def execute_workflow_action(
        self, request: WorkflowActionRequest
    ) -> WorkflowStatusReport:
        """Executes a human or system workflow action."""
        start_time = time.perf_counter()
        status_report = self.repository_service.get_workflow(request.workflow_id)

        if not status_report:
            raise ValueError(f"Workflow with ID '{request.workflow_id}' not found.")

        current_st = status_report.current_state
        next_st = self.state_machine.get_next_state(current_st)

        # Record Approval Action
        appr_record = self.approval_engine.record_approval_action(
            actor_id=request.actor_id,
            actor_role="Committee Member",
            action=request.action,
            original_ai_decision="Recommended",
            final_human_decision=request.override_decision or "Recommended",
            comments=request.comments or "",
        )
        status_report.approvals.append(appr_record)

        # Transition State
        t_record = self.state_machine.transition_state(current_st, next_st, request.actor_id)
        status_report.current_state = next_st
        status_report.completed_steps.append(current_st)
        status_report.history.append(t_record)

        # Publish Event
        self.event_bus.publish_event("WorkflowActionExecuted", {"workflow_id": request.workflow_id, "action": request.action, "new_state": next_st})

        status_report.processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        self.repository_service.save_workflow(status_report)

        logger.info(
            "Workflow action executed cleanly",
            workflow_id=status_report.workflow_id,
            action=request.action,
            new_state=next_st,
        )

        return status_report
