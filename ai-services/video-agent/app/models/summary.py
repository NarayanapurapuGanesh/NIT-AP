"""
FacultyIQ Video Evidence Extraction Service — Teaching Summary Models.

Pydantic v2 models for evidence-based teaching summary generation.
"""

from typing import List

from pydantic import BaseModel, Field


class TeachingSummary(BaseModel):
    """Teaching summary generated exclusively from extracted evidence."""

    short_summary: str = Field(
        ..., description="Concise 2–3 sentence summary of the teaching demonstration"
    )
    topics_covered: List[str] = Field(
        default_factory=list, description="Main topics covered"
    )
    concepts: List[str] = Field(
        default_factory=list, description="Key concepts discussed"
    )
    keywords: List[str] = Field(
        default_factory=list, description="Important keywords extracted"
    )
    technical_terms: List[str] = Field(
        default_factory=list, description="Domain-specific technical terms"
    )
    programming_languages: List[str] = Field(
        default_factory=list, description="Programming languages mentioned"
    )
    algorithms: List[str] = Field(
        default_factory=list, description="Algorithms referenced or discussed"
    )
    subjects: List[str] = Field(
        default_factory=list, description="Academic subjects or fields"
    )
    json_path: str = Field(
        ..., description="Path to summary.json output file"
    )
