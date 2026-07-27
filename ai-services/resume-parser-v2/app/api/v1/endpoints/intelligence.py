"""
Resume Intelligence & Validation Endpoint (Resume Intelligence Agent v2.0 Enterprise Edition).

POST /api/v1/intelligence/analyze
Receives file upload and returns full Enterprise Candidate Profile.
"""

from fastapi import APIRouter, File, UploadFile
from schemas.base import BaseResponse
from schemas.enterprise_profile import EnterpriseCandidateProfile
from services.document_intelligence import DocumentIntelligenceOrchestrator

router = APIRouter()
engine = DocumentIntelligenceOrchestrator(offline_mode=False)


@router.post(
    "/intelligence/analyze",
    response_model=BaseResponse[EnterpriseCandidateProfile],
    summary="Analyze Candidate Resume (v3.1 Document AI Micro-Architecture)",
    description="Executes 5-engine micro-architecture pipeline: Document AI (layout), Parsing Engine, Enrichment Engine, Verification, and Qwen Callback.",
)
async def analyze_candidate_resume(
    file: UploadFile = File(...),
) -> BaseResponse[EnterpriseCandidateProfile]:
    file_bytes = await file.read()
    profile = await engine.analyze_candidate_file(file_bytes, file.filename or "uploaded_resume.pdf")

    if not profile.file_meta.is_valid:
        return BaseResponse(
            success=False,
            message=profile.file_meta.error_message or "File validation failed.",
            data=profile,
        )

    return BaseResponse(
        success=True,
        message=f"Successfully generated Enterprise Candidate Profile for '{profile.candidate.name or profile.file_meta.file_name}' ({profile.resume_type.category.value}).",
        data=profile,
    )


from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.pipeline.intelligence_pipeline import ResumeIntelligencePipeline
from app.resume_intelligence.schemas.intelligence_report import CandidateIntelligenceReport

intelligence_pipeline = ResumeIntelligencePipeline()


@router.post(
    "/resume/intelligence",
    response_model=BaseResponse[CandidateIntelligenceReport],
    summary="Generate Resume Intelligence & Validation Report",
    description="Processes Structured Candidate Profile to generate quality scores, audit timeline, and research metrics.",
)
async def generate_resume_intelligence(
    profile: StructuredCandidateProfile,
) -> BaseResponse[CandidateIntelligenceReport]:
    report = await intelligence_pipeline.generate_intelligence_report(profile)
    return BaseResponse(
        success=True,
        message=f"Resume intelligence report generated for '{report.candidate_name}'.",
        data=report,
    )

