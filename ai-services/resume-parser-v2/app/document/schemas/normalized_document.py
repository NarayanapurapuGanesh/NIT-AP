"""
Canonical Pydantic v2 Models for Normalized Document Representation.
Every extracted node preserves exact bounding box coordinates and line-by-line evidence provenance.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class CoordinateBox(BaseModel):
    model_config = ConfigDict(frozen=True)

    page_number: int = Field(default=1, description="Page index (1-based)")
    x0: float = Field(default=0.0, description="Top-left X coordinate in points")
    y0: float = Field(default=0.0, description="Top-left Y coordinate in points")
    x1: float = Field(default=0.0, description="Bottom-right X coordinate in points")
    y1: float = Field(default=0.0, description="Bottom-right Y coordinate in points")
    width: float = Field(default=0.0, description="Box width in points")
    height: float = Field(default=0.0, description="Box height in points")


class EvidencePoint(BaseModel):
    page_number: int = Field(default=1)
    line_number: int = Field(default=1)
    char_offset: int = Field(default=0)
    word_index: int = Field(default=0)
    bounding_box: CoordinateBox = Field(default_factory=CoordinateBox)
    source_engine: str = Field(default="pymupdf", description="Extraction engine (pymupdf, pdfplumber, ocr, docx)")


class CharacterNode(BaseModel):
    char: str
    font_name: Optional[str] = None
    font_size: float = 10.0
    is_bold: bool = False
    is_italic: bool = False
    color: Optional[str] = None
    coordinates: CoordinateBox = Field(default_factory=CoordinateBox)


class WordNode(BaseModel):
    word_index: int = Field(default=0)
    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    coordinates: CoordinateBox = Field(default_factory=CoordinateBox)
    evidence: EvidencePoint = Field(default_factory=EvidencePoint)


class LineNode(BaseModel):
    line_number: int = Field(default=1)
    text: str
    words: List[WordNode] = Field(default_factory=list)
    coordinates: CoordinateBox = Field(default_factory=CoordinateBox)
    evidence: EvidencePoint = Field(default_factory=EvidencePoint)


class ParagraphNode(BaseModel):
    paragraph_number: int = Field(default=1)
    text: str
    lines: List[LineNode] = Field(default_factory=list)
    coordinates: CoordinateBox = Field(default_factory=CoordinateBox)
    style: Optional[str] = None


class BlockNode(BaseModel):
    block_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    block_type: str = Field(default="text", description="text, heading, list, table, header, footer, sidebar")
    reading_order: int = Field(default=0)
    text: str
    paragraphs: List[ParagraphNode] = Field(default_factory=list)
    coordinates: CoordinateBox = Field(default_factory=CoordinateBox)


class TableCell(BaseModel):
    row_index: int
    col_index: int
    text: str
    row_span: int = 1
    col_span: int = 1
    coordinates: CoordinateBox = Field(default_factory=CoordinateBox)


class TableNode(BaseModel):
    table_index: int = 1
    rows_count: int = 0
    cols_count: int = 0
    headers: List[str] = Field(default_factory=list)
    cells: List[TableCell] = Field(default_factory=list)
    coordinates: CoordinateBox = Field(default_factory=CoordinateBox)


class ImageNode(BaseModel):
    image_index: int = 1
    image_type: str = Field(default="figure", description="profile_photo, logo, chart, graph, signature, figure")
    dimensions: Dict[str, float] = Field(default_factory=dict)
    image_hash: str = Field(default="")
    page_number: int = 1
    coordinates: CoordinateBox = Field(default_factory=CoordinateBox)


class PageNode(BaseModel):
    page_number: int = 1
    width: float = 612.0
    height: float = 792.0
    text: str = ""
    blocks: List[BlockNode] = Field(default_factory=list)
    tables: List[TableNode] = Field(default_factory=list)
    images: List[ImageNode] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    document_uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_hash: str = ""
    author: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    producer: Optional[str] = None
    creator: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    page_count: int = 1
    language: str = "en"
    encoding: str = "utf-8"
    pdf_version: Optional[str] = None


class DocumentStatistics(BaseModel):
    word_count: int = 0
    char_count: int = 0
    paragraph_count: int = 0
    line_count: int = 0
    avg_font_size: float = 10.0
    avg_line_spacing: float = 1.2
    language_confidence: float = 1.0
    ocr_confidence: float = 1.0
    extraction_confidence: float = 1.0


class NormalizedDocument(BaseModel):
    document_uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    format_type: str
    classification_type: str = "Native PDF"
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    statistics: DocumentStatistics = Field(default_factory=DocumentStatistics)
    pages: List[PageNode] = Field(default_factory=list)
    reading_order_blocks: List[BlockNode] = Field(default_factory=list)
    tables: List[TableNode] = Field(default_factory=list)
    images: List[ImageNode] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
