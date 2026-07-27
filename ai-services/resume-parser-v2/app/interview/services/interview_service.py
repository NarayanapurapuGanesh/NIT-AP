"""
Interview Storage Repository Service.
In-memory and persistent repository service for saving and retrieving InterviewPlanReports and EvaluationReports.
"""

from typing import Dict, Optional
from app.interview.schemas.interview_models import InterviewEvaluationReport, InterviewPlanReport
from core.logging import get_logger

logger = get_logger("interview_service")


class InterviewRepositoryService:
    """Interview Storage Service."""

    _instance: Optional["InterviewRepositoryService"] = None

    def __init__(self) -> None:
        self._plans_by_id: Dict[str, InterviewPlanReport] = {}
        self._evaluations_by_id: Dict[str, InterviewEvaluationReport] = {}

    @classmethod
    def get_instance(cls) -> "InterviewRepositoryService":
        if cls._instance is None:
            cls._instance = InterviewRepositoryService()
        return cls._instance

    def save_plan(self, plan: InterviewPlanReport) -> None:
        self._plans_by_id[plan.plan_id] = plan
        logger.info("Saved interview plan to repository", plan_id=plan.plan_id)

    def get_plan(self, plan_id: str) -> Optional[InterviewPlanReport]:
        return self._plans_by_id.get(plan_id)

    def save_evaluation(self, eval_report: InterviewEvaluationReport) -> None:
        self._evaluations_by_id[eval_report.evaluation_id] = eval_report
        logger.info("Saved interview evaluation report to repository", eval_id=eval_report.evaluation_id)

    def get_evaluation(self, eval_id: str) -> Optional[InterviewEvaluationReport]:
        return self._evaluations_by_id.get(eval_id)
