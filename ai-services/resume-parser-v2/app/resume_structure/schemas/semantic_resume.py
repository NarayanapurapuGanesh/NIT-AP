"""
Canonical Pydantic v2 Models for Semantic Resume Structure Intelligence Engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.document.schemas.normalized_document import BlockNode, CoordinateBox, EvidencePoint


class HeadingIntelligence(BaseModel):
    canonical_type: str = Field(description="Normalized canonical section category name")
    original_heading: str = Field(description="Raw heading string extracted from document text")
    heading_level: int = Field(default=1, ge=1, le=3, description="Hierarchical level depth (1=H1, 2=H2, 3=H3)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Heading classification confidence score")
    is_misspelled: bool = Field(default=False, description="True if normalized via Levenshtein fuzzy match")
    alias_matched: Optional[str] = Field(default=None, description="Matched taxonomy alias key")


class SectionNode(BaseModel):
    section_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    canonical_type: str = Field(description="Canonical section type (e.g. Professional Experience)")
    original_heading: str = Field(description="Raw section heading text")
    heading_level: int = Field(default=1)
    confidence: float = Field(default=1.0)
    priority: int = Field(default=100)
    page_numbers: List[int] = Field(default_factory=list)
    reading_order_start: int = Field(default=0)
    reading_order_end: int = Field(default=0)
    bounding_boxes: List[CoordinateBox] = Field(default_factory=list)
    blocks: List[BlockNode] = Field(default_factory=list)
    paragraphs_count: int = Field(default=0)
    raw_text: str = Field(default="")
    evidence: List[EvidencePoint] = Field(default_factory=list)


class HierarchyNode(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    level: int = 1
    section_type: str
    children: List["HierarchyNode"] = Field(default_factory=list)
    block_ids: List[str] = Field(default_factory=list)


HierarchyNode.model_rebuild()


class GraphNode(BaseModel):
    node_id: str
    node_type: str = Field(description="section, paragraph, line, word")
    label: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    bounding_box: Optional[CoordinateBox] = None


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation_type: str = Field(description="contains, precedes, parent_of, evidence_for")


class ResumeGraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


class StructureValidationResult(BaseModel):
    is_valid: bool = True
    quality_score: float = 1.0
    missing_sections: List[str] = Field(default_factory=list)
    duplicate_sections: List[str] = Field(default_factory=list)
    broken_flow_warnings: List[str] = Field(default_factory=list)
    orphan_paragraphs_count: int = 0


class SemanticResumeModel(BaseModel):
    document_uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    header_block: Optional[SectionNode] = None
    summary_block: Optional[SectionNode] = None
    sections: List[SectionNode] = Field(default_factory=list)
    hierarchy_tree: HierarchyNode = Field(default_factory=lambda: HierarchyNode(name="Resume", level=0, section_type="Root"))
    structure_graph: ResumeGraph = Field(default_factory=ResumeGraph)
    validation_report: StructureValidationResult = Field(default_factory=StructureValidationResult)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
