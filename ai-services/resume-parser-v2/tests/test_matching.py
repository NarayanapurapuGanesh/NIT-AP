"""
Pytest integration & unit tests for Phase 8 Enterprise Candidate-Job Matching Engine.
"""

import pytest
from httpx import AsyncClient
from app.information_extraction.schemas.candidate_profile import (
    ContactInfo,
    EducationItem,
    ExperienceItem,
    ExtractedField,
    PublicationItem,
    SkillCategory,
    StructuredCandidateProfile,
)
from app.job_intelligence.schemas.job_models import (
    ExperienceRequirement,
    JobIntelligenceModel,
    PositionInfo,
    QualificationRequirement,
    SkillRequirement,
)
from app.matching.pipeline.matching_pipeline import MatchingPipeline
from app.matching.schemas.match_models import MatchAnalysisRequest


@pytest.fixture
def matching_pipeline():
    return MatchingPipeline()


@pytest.fixture
def mock_candidate():
    contact = ContactInfo(full_name=ExtractedField(value="Dr. Ananya Roy"))
    edu = EducationItem(degree=ExtractedField(value="Ph.D."), institution=ExtractedField(value="IIT Delhi"))
    exp = ExperienceItem(designation=ExtractedField(value="Assistant Professor"), organization=ExtractedField(value="NIT AP"))
    skills = [SkillCategory(category_name="Programming", skills=[ExtractedField(value="Python")])]
    pub = PublicationItem(title=ExtractedField(value="AI Paper"), doi=ExtractedField(value="10.1016/j.artint.2025"))

    return StructuredCandidateProfile(
        document_uuid="cand_match_001",
        filename="ananya_cv.pdf",
        contact=contact,
        education=[edu],
        experience=[exp],
        skills=skills,
        publications=[pub],
    )


@pytest.fixture
def mock_job():
    position = PositionInfo(title="Assistant Professor", academic_rank="Assistant Professor")
    qual = QualificationRequirement(minimum_degree="Ph.D.", is_phd_mandatory=True)
    exp = ExperienceRequirement(min_total_experience_years=2.0)
    skills = SkillRequirement(mandatory_skills=["Python"])

    return JobIntelligenceModel(
        job_uuid="job_match_001",
        filename_or_title="Assistant Professor JD",
        position=position,
        qualification=qual,
        experience=exp,
        skills=skills,
    )


@pytest.mark.anyio
async def test_matching_pipeline_execution(
    matching_pipeline: MatchingPipeline,
    mock_candidate: StructuredCandidateProfile,
    mock_job: JobIntelligenceModel,
):
    request = MatchAnalysisRequest(candidate_profile=mock_candidate, job_profile=mock_job)
    report = await matching_pipeline.match_candidate_to_job(request)

    assert report.candidate_name == "Dr. Ananya Roy"
    assert report.position_title == "Assistant Professor"
    assert report.overall_score >= 0.70
    assert report.score_breakdown.qualification_score == 1.0
    assert len(report.strengths) > 0
    assert len(report.evidence) > 0
    assert report.processing_time_ms > 0


@pytest.mark.anyio
async def test_matching_api_endpoint(
    async_client: AsyncClient,
    mock_candidate: StructuredCandidateProfile,
    mock_job: JobIntelligenceModel,
):
    request = MatchAnalysisRequest(candidate_profile=mock_candidate, job_profile=mock_job)
    payload = request.model_dump(mode="json")

    response = await async_client.post("/api/v1/matching/analyze", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["candidate_name"] == "Dr. Ananya Roy"
    assert json_data["data"]["overall_score"] > 0
    assert "score_breakdown" in json_data["data"]
