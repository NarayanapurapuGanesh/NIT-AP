"""
Canonical Pydantic v2 Models for Enterprise AI Recruitment Decision Agent.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.matching.schemas.match_models import CandidateMatchReport


class DecisionRequest(BaseModel):
    match_report: CandidateMatchReport
    department_name: Optional[str] = Field(default="Computer Science & Engineering")
    preferred_model: str = Field(default="llama3.2")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)


class SpecialistAgentOpinion(BaseModel):
    agent_name: str
    opinion: str
    confidence: float = 1.0
    recommendation: str = "Recommended"


class RiskAssessment(BaseModel):
    risk_level: str = "Low"  # Low, Medium, High, Critical
    risk_factors: List[str] = Field(default_factory=list)
    mitigation_strategies: List[str] = Field(default_factory=list)


class InterviewFocusArea(BaseModel):
    category: str  # Technical, Research Presentation, Teaching Demonstration, Panel Discussion
    focus_topics: List[str] = Field(default_factory=list)


class RecruitmentDecisionReport(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_uuid: str
    job_uuid: str
    candidate_name: str
    position_title: str
    recommendation: str = "Recommended"  # Highly Recommended, Recommended, Borderline, Requires Manual Review, Not Recommended
    overall_confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    summary: str = ""
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    risks: RiskAssessment = Field(default_factory=RiskAssessment)
    interview_focus: List[InterviewFocusArea] = Field(default_factory=list)
    specialist_opinions: List[SpecialistAgentOpinion] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
