"""
Matching Endpoint.
POST /api/v1/matching/analyze
Receives MatchAnalysisRequest payload and returns CandidateMatchReport.
"""

from fastapi import APIRouter
from app.matching.pipeline.matching_pipeline import MatchingPipeline
from app.matching.schemas.match_models import CandidateMatchReport, MatchAnalysisRequest
from schemas.base import BaseResponse

router = APIRouter()

matching_pipeline = MatchingPipeline()


@router.post(
    "/matching/analyze",
    response_model=BaseResponse[CandidateMatchReport],
    summary="Match Candidate Profile against Job Profile",
    description="Calculates deterministic weighted match score (0-100%), gap analysis, ranking features, and evidence provenance.",
)
async def analyze_candidate_match(
    request: MatchAnalysisRequest,
) -> BaseResponse[CandidateMatchReport]:
    match_report = await matching_pipeline.match_candidate_to_job(request)

    return BaseResponse(
        success=True,
        message=f"Matching for '{match_report.candidate_name}' against '{match_report.position_title}' complete (Overall Score: {int(match_report.overall_score * 100)}%).",
        data=match_report,
    )
