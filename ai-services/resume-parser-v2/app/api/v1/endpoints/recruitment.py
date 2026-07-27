"""
Recruitment Decision Endpoint.
POST /api/v1/recruitment/decision
Receives DecisionRequest payload and returns canonical RecruitmentDecisionReport.
"""

from fastapi import APIRouter
from app.recruitment_agent.pipeline.decision_pipeline import RecruitmentDecisionPipeline
from app.recruitment_agent.schemas.decision_models import DecisionRequest, RecruitmentDecisionReport
from schemas.base import BaseResponse

router = APIRouter()

decision_pipeline = RecruitmentDecisionPipeline()


@router.post(
    "/recruitment/decision",
    response_model=BaseResponse[RecruitmentDecisionReport],
    summary="Generate AI Recruitment Decision",
    description="Orchestrates 9 Specialist AI Agents to generate an explainable faculty hiring recommendation with risk analysis, interview topics, and evidence citations.",
)
async def generate_recruitment_decision(
    request: DecisionRequest,
) -> BaseResponse[RecruitmentDecisionReport]:
    report = await decision_pipeline.evaluate_candidate_decision(request)

    return BaseResponse(
        success=True,
        message=f"AI Recruitment Decision for candidate '{report.candidate_name}' complete (Recommendation: {report.recommendation}).",
        data=report,
    )
