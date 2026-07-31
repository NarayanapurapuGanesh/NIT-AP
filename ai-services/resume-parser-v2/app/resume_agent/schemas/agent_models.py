"""
Canonical Pydantic v2 Models for Enterprise Resume Intelligence Agent.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.resume_intelligence.schemas.intelligence_report import CandidateIntelligenceReport


class AgentAnalysisRequest(BaseModel):
    intelligence_report: CandidateIntelligenceReport
    job_description: Optional[str] = Field(default=None, description="Target Faculty Job Description text")
    department_name: Optional[str] = Field(default="Computer Science & Engineering", description="Academic Department")
    preferred_model: str = Field(default="qwen2.5", description="Ollama model name (llama3.2, qwen2.5, gemma, phi)")
    
    # Optional parameters
    temperature: float = 0.1
    max_tokens: int = 1500
    
class AgentReasoningStep(BaseModel):
    """Reasoning process log"""
    step: str
    description: str
    confidence: float


class EvidenceCitation(BaseModel):
    citation_id: str
    source_field: str
    extracted_value: str
    confidence: float = 1.0


class ReasoningHighlights(BaseModel):
    professional_summary: str
    research_highlights: List[str] = Field(default_factory=list)
    teaching_profile: List[str] = Field(default_factory=list)
    academic_strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    interview_preparation_notes: List[str] = Field(default_factory=list)


class TokenMetrics(BaseModel):
    """LLM execution metrics"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    model_name: str = "qwen2.5"


class AIResumeIntelligenceReport(BaseModel):
    agent_report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_uuid: str
    candidate_name: str
    reasoning: ReasoningHighlights
    citations: List[EvidenceCitation] = Field(default_factory=list)
    overall_agent_confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    token_metrics: TokenMetrics = Field(default_factory=TokenMetrics)
    deterministic_score_summary: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
