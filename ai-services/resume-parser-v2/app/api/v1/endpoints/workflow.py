"""
Recruitment Workflow Endpoints.
POST /api/v1/workflow/start
POST /api/v1/workflow/action
GET /api/v1/workflow/{workflow_id}
GET /api/v1/workflow/history/{workflow_id}
"""

from typing import List
from fastapi import APIRouter, HTTPException, Path
from app.workflow.pipeline.workflow_pipeline import WorkflowPipeline
from app.workflow.schemas.workflow_models import (
    StateTransitionRecord,
    WorkflowActionRequest,
    WorkflowStartRequest,
    WorkflowStatusReport,
)
from app.workflow.services.workflow_service import WorkflowRepositoryService
from schemas.base import BaseResponse

router = APIRouter()

workflow_pipeline = WorkflowPipeline()
repository_service = WorkflowRepositoryService.get_instance()


@router.post(
    "/workflow/start",
    response_model=BaseResponse[WorkflowStatusReport],
    summary="Start Faculty Recruitment Workflow",
    description="Initiates recruitment lifecycle workflow across 16 formal FSM states.",
)
async def start_workflow(
    request: WorkflowStartRequest,
) -> BaseResponse[WorkflowStatusReport]:
    report = await workflow_pipeline.start_recruitment_workflow(request)

    return BaseResponse(
        success=True,
        message=f"Recruitment workflow '{report.workflow_id}' started (Current State: {report.current_state}).",
        data=report,
    )


@router.post(
    "/workflow/action",
    response_model=BaseResponse[WorkflowStatusReport],
    summary="Execute Human or AI Workflow Action",
    description="Executes workflow action (Approve, Reject, Override, AdvanceState) and advances FSM state.",
)
async def execute_workflow_action(
    request: WorkflowActionRequest,
) -> BaseResponse[WorkflowStatusReport]:
    report = await workflow_pipeline.execute_workflow_action(request)

    return BaseResponse(
        success=True,
        message=f"Workflow action '{request.action}' executed for workflow '{report.workflow_id}' (New State: {report.current_state}).",
        data=report,
    )


@router.get(
    "/workflow/{workflow_id}",
    response_model=BaseResponse[WorkflowStatusReport],
    summary="Retrieve Workflow Status by ID",
    description="Fetches current state, pending tasks, approvals, and notifications.",
)
async def get_workflow_status(
    workflow_id: str = Path(..., description="Unique Workflow ID"),
) -> BaseResponse[WorkflowStatusReport]:
    report = repository_service.get_workflow(workflow_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Workflow with ID '{workflow_id}' not found.")

    return BaseResponse(
        success=True,
        message=f"Workflow '{workflow_id}' status retrieved.",
        data=report,
    )


@router.get(
    "/workflow/history/{workflow_id}",
    response_model=BaseResponse[List[StateTransitionRecord]],
    summary="Retrieve Workflow State History Log",
    description="Fetches complete state transition history log with timestamps and triggers.",
)
async def get_workflow_history(
    workflow_id: str = Path(..., description="Unique Workflow ID"),
) -> BaseResponse[List[StateTransitionRecord]]:
    report = repository_service.get_workflow(workflow_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Workflow with ID '{workflow_id}' not found.")

    return BaseResponse(
        success=True,
        message=f"Workflow '{workflow_id}' history retrieved ({len(report.history)} transitions).",
        data=report.history,
    )
