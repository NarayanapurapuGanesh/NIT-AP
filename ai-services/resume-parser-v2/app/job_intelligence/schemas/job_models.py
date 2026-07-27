"""
Canonical Pydantic v2 Models for Enterprise Job Description Intelligence Engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class InstitutionInfo(BaseModel):
    name: str = Field(default="Unknown Institution")
    department: str = Field(default="Computer Science & Engineering")
    location: str = Field(default="")
    institution_type: str = Field(default="University")  # University, NIT, IIT, Private College, Government


class PositionInfo(BaseModel):
    title: str = Field(default="Assistant Professor")
    employment_type: str = Field(default="Full-Time")  # Permanent, Contract, Adjunct, Guest, Visiting
    academic_rank: str = Field(default="Assistant Professor")  # Assistant Professor, Associate Professor, Professor
    pay_scale: Optional[str] = None


class QualificationRequirement(BaseModel):
    minimum_degree: str = Field(default="Ph.D.")
    preferred_degree: str = Field(default="Ph.D.")
    branch_or_specialization: List[str] = Field(default_factory=list)
    is_phd_mandatory: bool = True


class ExperienceRequirement(BaseModel):
    min_total_experience_years: float = 0.0
    min_teaching_experience_years: float = 0.0
    min_research_experience_years: float = 0.0
    min_industry_experience_years: float = 0.0


class SkillRequirement(BaseModel):
    mandatory_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)


class ResearchRequirement(BaseModel):
    min_publications_count: int = 0
    scopus_sci_mandatory: bool = False
    patents_required: bool = False
    funded_projects_required: bool = False
    preferred_research_domains: List[str] = Field(default_factory=list)


class TeachingRequirement(BaseModel):
    subjects: List[str] = Field(default_factory=list)
    course_levels: List[str] = Field(default_factory=list)  # UG, PG, PhD
    lab_guidance_required: bool = False


class ResponsibilityRequirement(BaseModel):
    teaching_responsibilities: List[str] = Field(default_factory=list)
    research_responsibilities: List[str] = Field(default_factory=list)
    administrative_responsibilities: List[str] = Field(default_factory=list)


class RequirementWeightMap(BaseModel):
    education_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    experience_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    research_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    teaching_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    skills_weight: float = Field(default=0.15, ge=0.0, le=1.0)


class JobIntelligenceModel(BaseModel):
    job_uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename_or_title: str = "Job Description"
    institution: InstitutionInfo = Field(default_factory=InstitutionInfo)
    position: PositionInfo = Field(default_factory=PositionInfo)
    qualification: QualificationRequirement = Field(default_factory=QualificationRequirement)
    experience: ExperienceRequirement = Field(default_factory=ExperienceRequirement)
    skills: SkillRequirement = Field(default_factory=SkillRequirement)
    research: ResearchRequirement = Field(default_factory=ResearchRequirement)
    teaching: TeachingRequirement = Field(default_factory=TeachingRequirement)
    responsibilities: ResponsibilityRequirement = Field(default_factory=ResponsibilityRequirement)
    weights: RequirementWeightMap = Field(default_factory=RequirementWeightMap)
    raw_text: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0


class JobAnalysisRequest(BaseModel):
    job_description_text: str = Field(description="Raw text of Faculty Job Description")
    job_title: Optional[str] = Field(default="Faculty Recruitment")
