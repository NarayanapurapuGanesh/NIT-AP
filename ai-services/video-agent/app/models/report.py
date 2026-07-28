from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationType(str, Enum):
    RECOMMEND = "Recommend"
    CONSIDER = "Consider"
    REJECT = "Reject"


class ScoreBreakdown(BaseModel):
    clarity_and_delivery: float = Field(..., description="Voice, speech rate, and acoustic delivery score (0-100)")
    visual_and_engagement: float = Field(..., description="Eye contact, posture, and gesture engagement score (0-100)")
    content_and_pedagogy: float = Field(..., description="Slide structure, OCR clarity, and teaching intelligence score (0-100)")
    overall_score: float = Field(..., description="Weighted overall composite evaluation score (0-100)")


class HiringRecommendation(BaseModel):
    recommendation: RecommendationType
    confidence_level: float
    summary: str


class EvaluationReport(BaseModel):
    job_id: str
    overall_score: float
    scores: ScoreBreakdown
    recommendation: HiringRecommendation
    strengths: List[str]
    weaknesses: List[str]
    html_report_path: str
    md_report_path: str
    json_report_path: str
