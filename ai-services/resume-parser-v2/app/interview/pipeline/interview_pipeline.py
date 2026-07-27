"""
End-to-End Enterprise Interview Intelligence & Assessment Pipeline.
Orchestrates Multi-Round Planning, Competency Mapping, Bloom's Taxonomy Question Generation,
Rubric Creation, Panel Assignment, Response Evaluation, and Repository Persistence.
"""

import time
from typing import List
from app.interview.competencies.competency_mapper import CompetencyMappingEngine
from app.interview.evaluation.response_evaluator import ResponseEvaluatorEngine
from app.interview.feedback.feedback_generator import FeedbackGeneratorEngine
from app.interview.panels.panel_manager import PanelManagerEngine
from app.interview.planning.interview_planner import InterviewPlannerEngine
from app.interview.questions.question_generator import QuestionGeneratorEngine
from app.interview.rubrics.rubric_generator import RubricGeneratorEngine
from app.interview.schemas.interview_models import (
    CandidateResponseInput,
    EvaluationRequest,
    InterviewEvaluationReport,
    InterviewPlanReport,
    InterviewPlanRequest,
    QuestionGenerationRequest,
)
from app.interview.services.interview_service import InterviewRepositoryService
from core.logging import get_logger

logger = get_logger("interview_pipeline")


class InterviewPipeline:
    """Enterprise Interview Intelligence Pipeline Engine."""

    def __init__(self) -> None:
        self.planner = InterviewPlannerEngine()
        self.competency_mapper = CompetencyMappingEngine()
        self.question_generator = QuestionGeneratorEngine()
        self.rubric_generator = RubricGeneratorEngine()
        self.panel_manager = PanelManagerEngine()
        self.response_evaluator = ResponseEvaluatorEngine()
        self.feedback_generator = FeedbackGeneratorEngine()
        self.repository_service = InterviewRepositoryService.get_instance()

    async def generate_interview_plan(self, request: InterviewPlanRequest) -> InterviewPlanReport:
        """Generates comprehensive multi-round interview plan."""
        start_time = time.perf_counter()
        decision = request.decision_report

        rounds = self.planner.build_interview_rounds(decision.position_title)
        questions = self.question_generator.generate_questions(
            decision.candidate_name, decision.position_title, ["Computer Science", "Artificial Intelligence"]
        )
        rubrics = self.rubric_generator.generate_rubrics()
        panel = self.panel_manager.assign_panel(request.department_name or "Computer Science")

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        plan = InterviewPlanReport(
            candidate_name=decision.candidate_name,
            position_title=decision.position_title,
            rounds=rounds,
            question_sets=questions,
            rubrics=rubrics,
            panel=panel,
            processing_time_ms=processing_time_ms,
        )

        self.repository_service.save_plan(plan)

        logger.info(
            "Interview plan generated cleanly",
            plan_id=plan.plan_id,
            candidate=plan.candidate_name,
            rounds_count=len(rounds),
            duration_ms=processing_time_ms,
        )

        return plan

    async def evaluate_interview(self, request: EvaluationRequest) -> InterviewEvaluationReport:
        """Evaluates candidate interview responses."""
        start_time = time.perf_counter()
        plan = self.repository_service.get_plan(request.plan_id)
        candidate_name = plan.candidate_name if plan else "Candidate"

        eval_report = self.response_evaluator.evaluate_responses(
            plan_id=request.plan_id,
            candidate_name=candidate_name,
            responses=request.responses,
        )

        eval_report.processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        self.repository_service.save_evaluation(eval_report)

        logger.info(
            "Interview evaluation complete",
            eval_id=eval_report.evaluation_id,
            candidate=candidate_name,
            score=eval_report.overall_interview_score,
        )

        return eval_report
