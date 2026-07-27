"""
Enterprise Candidate Profile Schema Module (Module 11) — v3.0.

Defines the unified, canonical Enterprise Candidate Profile JSON schema.
Integrates candidate entities, education, experience, projects, skills, publications,
discovered profiles, verification report, confidence scores, and evidence lineage graphs.

v3.0 additions:
- Profile summary, address, candidate type in CandidateContact
- Soft skills, categorized achievements in EnterpriseCandidateProfile
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from classifiers.type_detector import ResumeCategory, ResumeTypeResult
from extractors.deterministic_extractor import (
    AchievementEntity,
    EducationEntity,
    ExperienceEntity,
    ProjectEntity,
    PublicationEntity,
)
from extractors.link_discovery import ProfileLinks
from layout.layout_analyzer import StructuralAnalysisResult
from engines.schemas import SpatialLayoutDocument
from services.profile_collector import ProfileEvidencePackage
from validators.file_validator import FileValidationResult
from validators.fraud_detector import FraudDetectionReport
from validators.missing_info_evaluator import QualityEvaluationReport
from validators.profile_verifier import ProfileVerificationReport


class CandidateContact(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = Field(None, description="City/locality/address extracted from resume")
    languages: List[str] = Field(default_factory=list)
    profile_summary: Optional[str] = Field(None, description="Profile/objective/summary paragraph")
    candidate_type: str = Field("Unknown", description="Fresher / Experienced / Academic")


class FieldConfidenceScores(BaseModel):
    name: float = Field(0.0, description="Name extraction confidence [0 - 100%]")
    email: float = Field(0.0, description="Email extraction confidence")
    phone: float = Field(0.0, description="Phone extraction confidence")
    skills: float = Field(0.0, description="Skills confidence")
    education: float = Field(0.0, description="Education confidence")
    experience: float = Field(0.0, description="Work experience confidence")
    publications: float = Field(0.0, description="Publications confidence")
    projects: float = Field(0.0, description="Projects confidence")
    profile_summary: float = Field(0.0, description="Profile summary extraction confidence")
    soft_skills: float = Field(0.0, description="Soft skills extraction confidence")
    address: float = Field(0.0, description="Address extraction confidence")
    overall_average: float = Field(0.0, description="Mean confidence score across all fields")


class FieldEvidenceItem(BaseModel):
    field_name: str = Field(..., description="Target field name (e.g. email, skill, degree)")
    extracted_value: str = Field(..., description="Extracted string value")
    page_number: int = Field(1, description="Source page number (1-indexed)")
    section_header: str = Field("General", description="Source section header block")
    sentence_snippet: str = Field("", description="Exact line/sentence containing the value")
    bounding_box: List[float] = Field(default_factory=list, description="Coordinates [x0, y0, x1, y1]")
    extraction_source: str = Field("DETERMINISTIC", description="DETERMINISTIC, LLM_CALLBACK, OCR")
    confidence: float = Field(1.0, description="Field level confidence")


class EvidencePackageGraph(BaseModel):
    total_evidence_nodes: int = Field(0, description="Count of lineage evidence nodes tracked")
    evidence_nodes: List[FieldEvidenceItem] = Field(default_factory=list, description="List of fine-grained evidence records")


class EnterpriseCandidateProfile(BaseModel):
    """Complete Enterprise Candidate Profile Data Transfer Object (DTO)."""

    file_meta: FileValidationResult = Field(..., description="File validation metadata")
    resume_type: ResumeTypeResult = Field(..., description="Resume type classification")
    layout_structure: Union[StructuralAnalysisResult, SpatialLayoutDocument] = Field(..., description="Structural layout analysis")
    candidate: CandidateContact = Field(..., description="Candidate contact details")
    education: List[EducationEntity] = Field(default_factory=list, description="Education entries")
    experience: List[ExperienceEntity] = Field(default_factory=list, description="Work experience entries")
    projects: List[ProjectEntity] = Field(default_factory=list, description="Project entries")
    skills: List[str] = Field(default_factory=list, description="Technical skills inventory")
    soft_skills: List[str] = Field(default_factory=list, description="Soft/interpersonal skills")
    publications: List[PublicationEntity] = Field(default_factory=list, description="Publications & patents")
    patents: List[str] = Field(default_factory=list, description="Patents")
    awards: List[str] = Field(default_factory=list, description="Honors & awards (flat list)")
    categorized_awards: List[AchievementEntity] = Field(default_factory=list, description="Categorized achievements")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    profiles: ProfileLinks = Field(..., description="Discovered social and research profile links")
    external_evidence: ProfileEvidencePackage = Field(..., description="Collected external profile evidence")
    verification: ProfileVerificationReport = Field(..., description="Cross-verification report")
    fraud_report: FraudDetectionReport = Field(..., description="Fraud detection & integrity report")
    quality_evaluation: QualityEvaluationReport = Field(..., description="Profile completeness & suggestions")
    confidence: FieldConfidenceScores = Field(..., description="Field-level confidence scores")
    evidence: EvidencePackageGraph = Field(..., description="Audit evidence graph lineage")
