"""
Canonical Pydantic v2 Models for Enterprise Candidate-Job Matching Engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel


class MatchAnalysisRequest(BaseModel):
    candidate_profile: StructuredCandidateProfile
    job_profile: JobIntelligenceModel


class ScoreBreakdown(BaseModel):
    qualification_score: float = Field(default=1.0, ge=0.0, le=1.0)
    experience_score: float = Field(default=1.0, ge=0.0, le=1.0)
    research_score: float = Field(default=1.0, ge=0.0, le=1.0)
    teaching_score: float = Field(default=1.0, ge=0.0, le=1.0)
    skills_score: float = Field(default=1.0, ge=0.0, le=1.0)
    publication_score: float = Field(default=1.0, ge=0.0, le=1.0)
    certification_score: float = Field(default=1.0, ge=0.0, le=1.0)
    domain_score: float = Field(default=1.0, ge=0.0, le=1.0)
    overall_score: float = Field(default=1.0, ge=0.0, le=1.0)


class RequirementMatchItem(BaseModel):
    requirement_name: str
    is_met: bool
    candidate_value: str
    required_value: str
    confidence: float = 1.0


class MatchEvidenceItem(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_field: str
    extracted_text: str
    rule_id: str = "matching_rule"


class CandidateMatchReport(BaseModel):
    match_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_uuid: str
    job_uuid: str
    candidate_name: str
    position_title: str
    overall_score: float = Field(default=1.0, ge=0.0, le=1.0)
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    critical_gaps: List[str] = Field(default_factory=list)
    matched_requirements: List[RequirementMatchItem] = Field(default_factory=list)
    unmatched_requirements: List[RequirementMatchItem] = Field(default_factory=list)
    evidence: List[MatchEvidenceItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
