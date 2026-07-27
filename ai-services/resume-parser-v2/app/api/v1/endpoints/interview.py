"""
Interview Intelligence System Endpoints.
POST /api/v1/interview/plan
POST /api/v1/interview/questions
POST /api/v1/interview/evaluate
GET /api/v1/interview/report/{id}
"""

from typing import List
from fastapi import APIRouter, HTTPException, Path
from app.interview.pipeline.interview_pipeline import InterviewPipeline
from app.interview.schemas.interview_models import (
    EvaluationRequest,
    InterviewEvaluationReport,
    InterviewPlanReport,
    InterviewPlanRequest,
    InterviewQuestion,
    QuestionGenerationRequest,
)
from app.interview.services.interview_service import InterviewRepositoryService
from schemas.base import BaseResponse

router = APIRouter()

interview_pipeline = InterviewPipeline()
repository_service = InterviewRepositoryService.get_instance()


@router.post(
    "/interview/plan",
    response_model=BaseResponse[InterviewPlanReport],
    summary="Generate Comprehensive Faculty Interview Plan",
    description="Generates multi-round interview workflow (Technical, Teaching Demo, Research Presentation, Panel HR) with Bloom's Taxonomy question sets and rubrics.",
)
async def generate_interview_plan(
    request: InterviewPlanRequest,
) -> BaseResponse[InterviewPlanReport]:
    plan = await interview_pipeline.generate_interview_plan(request)

    return BaseResponse(
        success=True,
        message=f"Interview plan for candidate '{plan.candidate_name}' generated successfully ({len(plan.rounds)} rounds).",
        data=plan,
    )


@router.post(
    "/interview/questions",
    response_model=BaseResponse[List[InterviewQuestion]],
    summary="Generate Bloom's Taxonomy Interview Questions",
    description="Generates Bloom's Taxonomy-aligned question sets (Remember, Understand, Apply, Analyze, Evaluate, Create) mapped to difficulty levels.",
)
async def generate_questions(
    request: QuestionGenerationRequest,
) -> BaseResponse[List[InterviewQuestion]]:
    questions = interview_pipeline.question_generator.generate_questions(
        request.candidate_name, request.position_title, request.topics
    )

    return BaseResponse(
        success=True,
        message=f"Generated {len(questions)} Bloom's Taxonomy questions for candidate '{request.candidate_name}'.",
        data=questions,
    )


@router.post(
    "/interview/evaluate",
    response_model=BaseResponse[InterviewEvaluationReport],
    summary="Evaluate Candidate Interview Responses",
    description="Evaluates candidate interview answers against rubrics and returns overall score and updated hiring recommendation.",
)
async def evaluate_interview_responses(
    request: EvaluationRequest,
) -> BaseResponse[InterviewEvaluationReport]:
    eval_report = await interview_pipeline.evaluate_interview(request)

    return BaseResponse(
        success=True,
        message=f"Interview evaluation for '{eval_report.candidate_name}' complete (Overall Score: {eval_report.overall_interview_score}%).",
        data=eval_report,
    )


@router.get(
    "/interview/report/{id}",
    response_model=BaseResponse[InterviewPlanReport],
    summary="Retrieve Interview Plan Report by ID",
    description="Fetches interview plan report, questions, rubrics, and panel assignments.",
)
async def get_interview_report(
    id: str = Path(..., description="Interview Plan ID"),
) -> BaseResponse[InterviewPlanReport]:
    plan = repository_service.get_plan(id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Interview plan with ID '{id}' not found.")

    return BaseResponse(
        success=True,
        message=f"Interview plan '{id}' retrieved.",
        data=plan,
    )
