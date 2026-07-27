"""
Workflow Repository Storage Service.
In-memory and persistent repository storing workflow states, transition logs, and audit records.
"""

from typing import Dict, List, Optional
from app.workflow.schemas.workflow_models import WorkflowStatusReport
from core.logging import get_logger

logger = get_logger("workflow_service")


class WorkflowRepositoryService:
    """Workflow Storage Service."""

    _instance: Optional["WorkflowRepositoryService"] = None

    def __init__(self) -> None:
        self._workflows_by_id: Dict[str, WorkflowStatusReport] = {}

    @classmethod
    def get_instance(cls) -> "WorkflowRepositoryService":
        if cls._instance is None:
            cls._instance = WorkflowRepositoryService()
        return cls._instance

    def save_workflow(self, report: WorkflowStatusReport) -> None:
        self._workflows_by_id[report.workflow_id] = report
        logger.info("Saved workflow status report to repository", workflow_id=report.workflow_id)

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowStatusReport]:
        return self._workflows_by_id.get(workflow_id)
