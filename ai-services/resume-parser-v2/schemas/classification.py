"""
Pydantic v2 Schemas for Document Classification Engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentTypeEnum(str, Enum):
    RESUME = "Resume"
    ACADEMIC_RESUME = "Academic Resume"
    FACULTY_CV = "Faculty CV"
    CURRICULUM_VITAE = "Curriculum Vitae"
    RESEARCH_CV = "Research CV"
    STUDENT_RESUME = "Student Resume"
    INVOICE = "Invoice"
    CERTIFICATE = "Certificate"
    RESEARCH_PAPER = "Research Paper"
    BOOK = "Book"
    COURSE_SYLLABUS = "Course Syllabus"
    QUESTION_PAPER = "Question Paper"
    MARKSHEET = "Marksheet"
    COVER_LETTER = "Cover Letter"
    RECOMMENDATION_LETTER = "Recommendation Letter"
    IDENTITY_DOCUMENT = "Identity Document"
    UNKNOWN = "Unknown"


class NextStageEnum(str, Enum):
    TEXT_EXTRACTION = "TextExtraction"
    SPECIALIZED_HANDLER = "SpecializedHandler"
    REJECTED = "Rejected"


class EvidenceItem(BaseModel):
    rule: str = Field(description="Name or ID of rule that matched")
    weight: float = Field(description="Confidence weight contribution (+/-)")
    matched_text: Optional[str] = Field(default=None, description="Snippet or value triggering rule match")
    source_layer: str = Field(default="rule_engine", description="Pipeline layer originating the evidence")


class ClassificationResult(BaseModel):
    document_type: str = Field(description="Determined document category classification")
    confidence: float = Field(ge=0.0, le=1.0, description="Normalized score between 0.00 and 1.00")
    accepted: bool = Field(description="True if document type is eligible for resume ingestion pipeline")
    reasons: List[str] = Field(default_factory=list, description="Human-readable decision explanation list")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Granular weighted rule evidence items")
    next_stage: str = Field(description="Recommended downstream pipeline stage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extracted file metadata summary")
    processing_time_ms: float = Field(default=0.0, description="Classification engine runtime duration in ms")
