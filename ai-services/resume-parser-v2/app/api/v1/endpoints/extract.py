"""
Information Extraction Endpoint.
POST /api/v1/resume/extract
Receives SemanticResumeModel payload and returns evidence-backed StructuredCandidateProfile & Knowledge Graph.
"""

from fastapi import APIRouter
from app.information_extraction.pipeline.extraction_pipeline import InformationExtractionPipeline
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_structure.schemas.semantic_resume import SemanticResumeModel
from schemas.base import BaseResponse

router = APIRouter()

extraction_pipeline = InformationExtractionPipeline()


@router.post(
    "/resume/extract",
    response_model=BaseResponse[StructuredCandidateProfile],
    summary="Extract Structured Candidate Profile",
    description="Extracts contact details, experience, education, skills, projects, publications, awards, and knowledge graph without LLM hallucination.",
)
async def extract_candidate_info(
    semantic_model: SemanticResumeModel,
) -> BaseResponse[StructuredCandidateProfile]:
    profile = await extraction_pipeline.extract_candidate_profile(semantic_model)

    return BaseResponse(
        success=True,
        message=f"Candidate profile for '{semantic_model.filename}' extracted cleanly ({len(profile.experience)} jobs, {len(profile.education)} degrees).",
        data=profile,
    )
