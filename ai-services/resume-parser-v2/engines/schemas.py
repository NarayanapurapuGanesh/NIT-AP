from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LayoutBlock(BaseModel):
    block_type: str = Field(..., description="text, header, footer, table, sidebar, image")
    bbox: List[float] = Field(default_factory=list, description="[x0, y0, x1, y1]")
    text: str = Field("", description="Text content")
    column_index: int = Field(0, description="0=left, 1=right")
    page_number: int = Field(1, description="1-indexed")
    font_size: float = Field(0.0)
    is_bold: bool = Field(False)
    is_heading: bool = Field(False)

class SectionBlock(BaseModel):
    section_name: str = Field(..., description="Normalized section name (e.g. EDUCATION, PROJECTS)")
    heading_text: str = Field("", description="Original text")
    content_lines: List[str] = Field(default_factory=list)
    column_index: int = Field(0)
    bbox: List[float] = Field(default_factory=list, description="Enclosing bounding box of the section")
    page_number: int = Field(1)

class SpatialLayoutDocument(BaseModel):
    """Engine 1 Output: Structural representation of the document."""
    is_two_column: bool = Field(False)
    column_count: int = Field(1)
    has_sidebar: bool = Field(False)
    has_images: bool = Field(False)
    blocks: List[LayoutBlock] = Field(default_factory=list)
    total_pages: int = Field(1)
    sections: List[SectionBlock] = Field(default_factory=list)
    reading_order_text: str = Field("", description="Full text correctly ordered")
    sidebar_sections: List[SectionBlock] = Field(default_factory=list)
    main_sections: List[SectionBlock] = Field(default_factory=list)
    detected_split_x: float = Field(0.0)
