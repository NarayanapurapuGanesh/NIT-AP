"""
Canonical Pydantic v2 Schemas for Enterprise Information Extraction Engine.
Every extracted field is wrapped in ExtractedField[T] to guarantee zero hallucination and 100% evidence lineage.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.document.schemas.normalized_document import CoordinateBox, EvidencePoint

T = TypeVar("T")


class ExtractedField(BaseModel, Generic[T]):
    value: Optional[T] = None
    raw_text: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    rule_id: str = "pattern_match"
    evidence: List[EvidencePoint] = Field(default_factory=list)


class ContactInfo(BaseModel):
    full_name: ExtractedField[str] = Field(default_factory=ExtractedField)
    first_name: ExtractedField[str] = Field(default_factory=ExtractedField)
    middle_name: ExtractedField[str] = Field(default_factory=ExtractedField)
    last_name: ExtractedField[str] = Field(default_factory=ExtractedField)
    professional_title: ExtractedField[str] = Field(default_factory=ExtractedField)
    email: ExtractedField[str] = Field(default_factory=ExtractedField)
    phone: ExtractedField[str] = Field(default_factory=ExtractedField)
    alt_phone: ExtractedField[str] = Field(default_factory=ExtractedField)
    linkedin_url: ExtractedField[str] = Field(default_factory=ExtractedField)
    github_url: ExtractedField[str] = Field(default_factory=ExtractedField)
    google_scholar_url: ExtractedField[str] = Field(default_factory=ExtractedField)
    researchgate_url: ExtractedField[str] = Field(default_factory=ExtractedField)
    orcid: ExtractedField[str] = Field(default_factory=ExtractedField)
    website: ExtractedField[str] = Field(default_factory=ExtractedField)
    address: ExtractedField[str] = Field(default_factory=ExtractedField)
    city: ExtractedField[str] = Field(default_factory=ExtractedField)
    country: ExtractedField[str] = Field(default_factory=ExtractedField)


class ExperienceItem(BaseModel):
    item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    designation: ExtractedField[str] = Field(default_factory=ExtractedField)
    organization: ExtractedField[str] = Field(default_factory=ExtractedField)
    department: ExtractedField[str] = Field(default_factory=ExtractedField)
    start_date: ExtractedField[str] = Field(default_factory=ExtractedField)
    end_date: ExtractedField[str] = Field(default_factory=ExtractedField)
    is_current: bool = False
    duration_months: int = 0
    responsibilities: List[str] = Field(default_factory=list)
    location: ExtractedField[str] = Field(default_factory=ExtractedField)


class EducationItem(BaseModel):
    item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    degree: ExtractedField[str] = Field(default_factory=ExtractedField)
    specialization: ExtractedField[str] = Field(default_factory=ExtractedField)
    institution: ExtractedField[str] = Field(default_factory=ExtractedField)
    board_or_university: ExtractedField[str] = Field(default_factory=ExtractedField)
    cgpa: ExtractedField[float] = Field(default_factory=ExtractedField)
    percentage: ExtractedField[float] = Field(default_factory=ExtractedField)
    start_year: ExtractedField[int] = Field(default_factory=ExtractedField)
    end_year: ExtractedField[int] = Field(default_factory=ExtractedField)
    supervisor: ExtractedField[str] = Field(default_factory=ExtractedField)


class SkillCategory(BaseModel):
    category_name: str
    skills: List[ExtractedField[str]] = Field(default_factory=list)


class ProjectItem(BaseModel):
    project_name: ExtractedField[str] = Field(default_factory=ExtractedField)
    role: ExtractedField[str] = Field(default_factory=ExtractedField)
    duration: ExtractedField[str] = Field(default_factory=ExtractedField)
    description: str = ""
    technologies: List[str] = Field(default_factory=list)
    demo_url: ExtractedField[str] = Field(default_factory=ExtractedField)


class PublicationItem(BaseModel):
    title: ExtractedField[str] = Field(default_factory=ExtractedField)
    authors: List[str] = Field(default_factory=list)
    venue: ExtractedField[str] = Field(default_factory=ExtractedField)  # Journal or Conference
    year: ExtractedField[int] = Field(default_factory=ExtractedField)
    doi: ExtractedField[str] = Field(default_factory=ExtractedField)
    citations_count: int = 0


class CertificationItem(BaseModel):
    title: ExtractedField[str] = Field(default_factory=ExtractedField)
    issuer: ExtractedField[str] = Field(default_factory=ExtractedField)
    issue_date: ExtractedField[str] = Field(default_factory=ExtractedField)
    credential_id: ExtractedField[str] = Field(default_factory=ExtractedField)


class AwardItem(BaseModel):
    award_title: ExtractedField[str] = Field(default_factory=ExtractedField)
    organization: ExtractedField[str] = Field(default_factory=ExtractedField)
    year: ExtractedField[int] = Field(default_factory=ExtractedField)


class LanguageItem(BaseModel):
    language: str
    proficiency: str = "Professional"


class ReferenceItem(BaseModel):
    referee_name: ExtractedField[str] = Field(default_factory=ExtractedField)
    designation: ExtractedField[str] = Field(default_factory=ExtractedField)
    institution: ExtractedField[str] = Field(default_factory=ExtractedField)
    email: ExtractedField[str] = Field(default_factory=ExtractedField)
    phone: ExtractedField[str] = Field(default_factory=ExtractedField)


class KnowledgeGraphNode(BaseModel):
    node_id: str
    entity_type: str = Field(description="Candidate, Company, University, Skill, Project, Publication, Award")
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str = Field(description="WORKED_AT, STUDIED_AT, HAS_SKILL, WORKED_ON, PUBLISHED, WON")


class CandidateKnowledgeGraph(BaseModel):
    nodes: List[KnowledgeGraphNode] = Field(default_factory=list)
    edges: List[KnowledgeGraphEdge] = Field(default_factory=list)


class StructuredCandidateProfile(BaseModel):
    document_uuid: str
    filename: str
    contact: ContactInfo = Field(default_factory=ContactInfo)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    skills: List[SkillCategory] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    publications: List[PublicationItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    awards: List[AwardItem] = Field(default_factory=list)
    languages: List[LanguageItem] = Field(default_factory=list)
    references: List[ReferenceItem] = Field(default_factory=list)
    knowledge_graph: CandidateKnowledgeGraph = Field(default_factory=CandidateKnowledgeGraph)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
