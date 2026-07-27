"""
Canonical Pydantic v2 Models for Candidate Intelligence Report & Validation Engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ProfileQualityScores(BaseModel):
    completeness_score: float = Field(default=1.0, ge=0.0, le=1.0)
    data_quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    resume_quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    research_strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    teaching_strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    industry_strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    technical_strength_score: float = Field(default=1.0, ge=0.0, le=1.0)
    validation_score: float = Field(default=1.0, ge=0.0, le=1.0)


class TimelineAnalysis(BaseModel):
    total_experience_years: float = 0.0
    relevant_experience_years: float = 0.0
    research_experience_years: float = 0.0
    teaching_experience_years: float = 0.0
    industry_experience_years: float = 0.0
    career_gap_count: int = 0
    career_gaps_months: List[int] = Field(default_factory=list)
    has_education_overlap: bool = False
    has_job_overlap: bool = False
    average_job_tenure_months: float = 0.0


class ResearchIntelligence(BaseModel):
    publication_count: int = 0
    doi_count: int = 0
    citations_total: int = 0
    research_domains: List[str] = Field(default_factory=list)
    has_recent_publication: bool = False
    research_continuity_score: float = 1.0


class TeachingIntelligence(BaseModel):
    has_teaching_experience: bool = False
    highest_academic_rank: Optional[str] = None
    subjects_count: int = 0
    has_administrative_roles: bool = False
    teaching_score: float = 0.0


class ConsistencyReport(BaseModel):
    is_consistent: bool = True
    conflicting_dates: List[str] = Field(default_factory=list)
    duplicate_companies: List[str] = Field(default_factory=list)
    duplicate_skills: List[str] = Field(default_factory=list)
    duplicate_publications: List[str] = Field(default_factory=list)


class AnomalyReport(BaseModel):
    has_anomalies: bool = False
    future_dates: List[str] = Field(default_factory=list)
    negative_durations: List[str] = Field(default_factory=list)
    invalid_cgpa_entries: List[str] = Field(default_factory=list)
    unbacked_evidence_fields: List[str] = Field(default_factory=list)


class CandidateIntelligenceReport(BaseModel):
    report_uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_uuid: str
    filename: str
    candidate_name: str = "Unknown Candidate"
    scores: ProfileQualityScores = Field(default_factory=ProfileQualityScores)
    timeline: TimelineAnalysis = Field(default_factory=TimelineAnalysis)
    research: ResearchIntelligence = Field(default_factory=ResearchIntelligence)
    teaching: TeachingIntelligence = Field(default_factory=TeachingIntelligence)
    consistency: ConsistencyReport = Field(default_factory=ConsistencyReport)
    anomalies: AnomalyReport = Field(default_factory=AnomalyReport)
    recommendations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    metrics_summary: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
