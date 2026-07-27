"""
Job Intelligence Endpoint.
POST /api/v1/job/analyze
Receives raw text or document payload of Job Description and returns structured JobIntelligenceModel.
"""

from fastapi import APIRouter
from app.job_intelligence.pipeline.job_pipeline import JobIntelligencePipeline
from app.job_intelligence.schemas.job_models import JobAnalysisRequest, JobIntelligenceModel
from schemas.base import BaseResponse

router = APIRouter()

job_pipeline = JobIntelligencePipeline()


@router.post(
    "/job/analyze",
    response_model=BaseResponse[JobIntelligenceModel],
    summary="Analyze Job Description Intelligence",
    description="Transforms raw Job Description into a structured machine-readable JobIntelligenceModel with requirement weights and evidence.",
)
async def analyze_job_description(
    request: JobAnalysisRequest,
) -> BaseResponse[JobIntelligenceModel]:
    job_model = await job_pipeline.process_job_description(request)

    return BaseResponse(
        success=True,
        message=f"Job Description for '{job_model.position.title}' analyzed successfully ({job_model.qualification.minimum_degree} minimum qualification).",
        data=job_model,
    )
