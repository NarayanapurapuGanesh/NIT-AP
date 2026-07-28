from typing import List
from pydantic import BaseModel, Field


class TeachingAnalysisResult(BaseModel):
    pedagogy_score: float = 85.0
    structure_score: float = 88.0
    engagement_score: float = 82.0
    clarity_score: float = 87.0
    insights: List[str] = Field(default_factory=list)
    json_path: str
