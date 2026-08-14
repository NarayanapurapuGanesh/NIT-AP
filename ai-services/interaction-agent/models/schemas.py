"""Pydantic models for the Interaction Agent session state and API contracts."""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class BloomLevel(str, Enum):
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


class DifficultyLevel(str, Enum):
    FOUNDATIONAL = "Foundational"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class PersonaType(str, Enum):
    BEGINNER = "Beginner"
    AVERAGE = "Average"
    EXCELLENT = "Excellent"
    CONFUSED = "Confused"
    CURIOUS = "Curious"
    PRACTICAL_LEARNER = "PracticalLearner"
    RESEARCH_STUDENT = "ResearchStudent"
    INDUSTRY_STUDENT = "IndustryStudent"
    EXAM_ORIENTED = "ExamOriented"
    SLOW_LEARNER = "SlowLearner"
    ADVANCED_LEARNER = "AdvancedLearner"


class MisconceptionStatus(str, Enum):
    PRESENTED = "Presented"
    IDENTIFIED = "Identified"
    CORRECTED = "Corrected"
    MISSED = "Missed"
    PARTIALLY_CORRECTED = "PartiallyCorrected"


class ConversationMessage(BaseModel):
    role: str
    content: str
    turn_number: int


class ActiveMisconception(BaseModel):
    misconception_text: str
    correct_concept: str
    status: str


class InteractionRequest(BaseModel):
    """Request from .NET backend to generate AI student response."""
    session_id: str
    faculty_message: str
    persona_type: str
    subject: str
    department: str
    turn_number: int
    max_turns: int
    current_bloom_level: str
    current_difficulty: str
    conversation_history: list[ConversationMessage] = Field(default_factory=list)
    active_misconceptions: list[ActiveMisconception] = Field(default_factory=list)
    faculty_context_json: Optional[str] = None


class TeachingEvaluation(BaseModel):
    """AI evaluation of the faculty's teaching quality for a single turn."""
    concept_clarity: float = Field(ge=0, le=1)
    technical_accuracy: float = Field(ge=0, le=1)
    logical_flow: float = Field(ge=0, le=1)
    explanation_simplicity: float = Field(ge=0, le=1)
    depth: float = Field(ge=0, le=1)
    example_quality: float = Field(ge=0, le=1)
    analogy_usage: float = Field(ge=0, le=1)
    real_world_relevance: float = Field(ge=0, le=1)
    question_handling: float = Field(ge=0, le=1)
    doubt_clarification: float = Field(ge=0, le=1)
    adaptive_teaching: float = Field(ge=0, le=1)
    grammar: float = Field(ge=0, le=1)
    fluency: float = Field(ge=0, le=1)
    vocabulary: float = Field(ge=0, le=1)
    professionalism: float = Field(ge=0, le=1)
    critical_thinking_encouragement: float = Field(ge=0, le=1)
    evidence_justification: str = ""
    confidence: float = Field(ge=0, le=1, default=0.5)


class NewMisconception(BaseModel):
    """A new misconception for the AI student to present."""
    misconception_text: str
    correct_concept: str
    subject_category: str


class MisconceptionCorrection(BaseModel):
    """AI assessment of how faculty corrected a misconception."""
    misconception_text: str
    correction_text: str
    correction_quality: float = Field(ge=0, le=1)
    fully_corrected: bool


class InteractionResponse(BaseModel):
    """Response from the AI service back to the .NET backend."""
    student_message: str
    current_bloom_level: str
    new_bloom_level: Optional[str] = None
    bloom_transition_reason: Optional[str] = None
    current_topic: str = ""
    evaluation: Optional[TeachingEvaluation] = None
    new_misconception: Optional[NewMisconception] = None
    misconception_correction: Optional[MisconceptionCorrection] = None
    understanding_estimate: float = Field(ge=0, le=1, default=0.3)
    should_end_session: bool = False
    end_session_reason: Optional[str] = None


class FinalEvaluationRequest(BaseModel):
    """Request for a final comprehensive evaluation of the entire session."""
    session_id: str
    conversation_history: list[ConversationMessage]
    faculty_context_json: Optional[str] = None


class SessionReport(BaseModel):
    """Full session evaluation report."""
    session_id: str
    overall_teaching_effectiveness: float = Field(ge=0, le=1)
    scores: dict[str, float] = Field(default_factory=dict)
    bloom_distribution: dict[str, int] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, default=0.5)
    total_turns: int = 0
    duration: str = ""
    persona_used: str = ""
    subject: str = ""
