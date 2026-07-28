from typing import List, Optional
from pydantic import BaseModel, Field


class PageOCR(BaseModel):
    page_index: int
    image_path: str
    raw_text: str
    cleaned_text: str
    confidence: float
    titles: List[str] = Field(default_factory=list)
    headings: List[str] = Field(default_factory=list)
    bullet_points: List[str] = Field(default_factory=list)
    code_snippets: List[str] = Field(default_factory=list)
    equations: List[str] = Field(default_factory=list)


class OCRResult(BaseModel):
    total_pages: int
    average_confidence: float
    frame_results: List[PageOCR]
    json_path: str
