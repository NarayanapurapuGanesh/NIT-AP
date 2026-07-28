from typing import List
from pydantic import BaseModel, Field


class Segment(BaseModel):
    id: int
    start: float
    end: float
    text: str


class TranscriptionResult(BaseModel):
    full_text: str
    segments: List[Segment]
    json_path: str
    srt_path: str
    txt_path: str
