"""Session state models for the Interaction Agent.

These are the authoritative in-memory state objects that track the full
lifecycle of a teaching interaction session. They are NOT database ORM models —
persistence is handled by the SessionManager via JSON serialization.
"""

from __future__ import annotations
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETING = "COMPLETING"
    COMPLETED = "COMPLETED"
    EVALUATED = "EVALUATED"
    ERROR = "ERROR"
    TIMED_OUT = "TIMED_OUT"


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


class SpeakerRole(str, Enum):
    STUDENT = "Student"
    FACULTY = "Faculty"
    SYSTEM = "System"


# ─── Turn ────────────────────────────────────────────────────────


class TurnEvidence(BaseModel):
    """A piece of evidence extracted from a turn."""
    type: str  # STRENGTH, WEAKNESS, OBSERVATION
    claim: str
    score: float = 0.0
    confidence: float = 0.5


class TurnAnalysis(BaseModel):
    """Structured analysis of a faculty response turn."""
    technical_accuracy: float = 0.5
    conceptual_clarity: float = 0.5
    structure: float = 0.5
    example_quality: float = 0.3
    student_alignment: float = 0.5
    misconception_handling: float = 0.5
    depth: float = 0.5
    pedagogical_quality: float = 0.5
    doubt_resolution: float = 0.5
    adaptive_teaching: float = 0.5
    evidence_justification: str = ""
    confidence: float = 0.5


class Turn(BaseModel):
    """A single conversation turn."""
    turn_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    turn_number: int
    speaker: SpeakerRole
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    response_latency_ms: Optional[float] = None
    concept: str = ""
    bloom_level: BloomLevel = BloomLevel.REMEMBER
    difficulty: DifficultyLevel = DifficultyLevel.FOUNDATIONAL
    analysis: Optional[TurnAnalysis] = None
    evidence: list[TurnEvidence] = Field(default_factory=list)
    understanding_estimate: Optional[float] = None


# ─── Misconception ──────────────────────────────────────────────


class MisconceptionState(BaseModel):
    """Tracks a misconception through its lifecycle."""
    misconception_text: str
    correct_concept: str
    subject_category: str
    presented_at_turn: int
    status: str = "Presented"  # Presented, Corrected, Missed, PartiallyCorrected
    corrected_at_turn: Optional[int] = None
    correction_quality: Optional[float] = None


# ─── Bloom Progress ─────────────────────────────────────────────


class BloomProgressEntry(BaseModel):
    """Records a Bloom level transition."""
    turn_number: int
    from_level: BloomLevel
    to_level: BloomLevel
    topic: str
    reason: str = ""


# ─── Session Summary (for context management) ───────────────────


class SessionSummary(BaseModel):
    """Compact session summary for LLM context window management."""
    concepts_covered: list[str] = Field(default_factory=list)
    student_misconceptions: list[str] = Field(default_factory=list)
    faculty_strengths: list[str] = Field(default_factory=list)
    faculty_weaknesses: list[str] = Field(default_factory=list)
    current_understanding: float = 0.3
    key_events: list[str] = Field(default_factory=list)


# ─── Evidence Packet ─────────────────────────────────────────────


class EvidencePacket(BaseModel):
    """Evidence supporting an evaluation claim."""
    turn_number: int
    type: str  # teaching_quality, misconception_handling, bloom_progression
    score: float
    justification: str
    confidence: float = 0.5
    bloom_level: BloomLevel = BloomLevel.REMEMBER


# ─── Analytics Snapshot ──────────────────────────────────────────


class AnalyticsSnapshot(BaseModel):
    """Real-time analytics for the frontend dashboard."""
    teaching_score: float = 0.0
    communication_score: float = 0.0
    engagement_score: float = 0.0
    student_satisfaction: float = 0.0
    learning_gain: float = 0.0
    current_bloom_level: str = "Remember"
    turn_number: int = 0
    max_turns: int = 12
    current_topic: str = ""
    bloom_distribution: dict[str, int] = Field(default_factory=dict)
    total_misconceptions: int = 0
    corrected_misconceptions: int = 0
    missed_misconceptions: int = 0
    total_evidence_packets: int = 0
    understanding_estimate: float = 0.1
    concepts_explored: int = 0


# ─── Session Report ──────────────────────────────────────────────


class TeachingScores(BaseModel):
    """Detailed score breakdown for the final report."""
    technical_accuracy: float = 0.5
    concept_clarity: float = 0.5
    doubt_resolution: float = 0.5
    pedagogical_adaptability: float = 0.5
    explanation_structure: float = 0.5
    example_quality: float = 0.3
    bloom_depth: float = 0.3
    misconception_handling: float = 0.5


class SessionReport(BaseModel):
    """Full teaching evaluation report."""
    session_id: str
    overall_score: float = 0.0
    recommendation: str = "PENDING"  # STRONG, GOOD, AVERAGE, NEEDS_IMPROVEMENT
    scores: TeachingScores = Field(default_factory=TeachingScores)
    bloom_profile: dict[str, float] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    evidence: list[EvidencePacket] = Field(default_factory=list)
    improvement_areas: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    total_turns: int = 0
    duration: str = ""
    persona_used: str = ""
    subject: str = ""
    department: str = ""


# ─── Session (Root Aggregate) ────────────────────────────────────


class InteractionSession(BaseModel):
    """Root aggregate for the teaching interaction session.
    This is the authoritative session state owned by the Python service.
    """
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str = ""
    subject: str = ""
    department: str = ""
    persona_type: str = "Beginner"
    status: SessionStatus = SessionStatus.CREATED
    mode: str = "assessment"  # assessment | practice

    # Progress
    current_turn: int = 0
    max_turns: int = 12
    current_bloom_level: BloomLevel = BloomLevel.REMEMBER
    current_difficulty: DifficultyLevel = DifficultyLevel.FOUNDATIONAL
    current_topic: str = ""
    understanding_estimate: float = 0.1

    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    paused_at: Optional[str] = None
    completed_at: Optional[str] = None
    last_activity_at: Optional[str] = None

    # Conversation
    conversation: list[Turn] = Field(default_factory=list)

    # Tracking
    misconceptions: list[MisconceptionState] = Field(default_factory=list)
    bloom_progress: list[BloomProgressEntry] = Field(default_factory=list)
    evidence_packets: list[EvidencePacket] = Field(default_factory=list)
    concepts_covered: list[str] = Field(default_factory=list)

    # Running score accumulators (updated each turn)
    turn_analyses: list[TurnAnalysis] = Field(default_factory=list)

    # Summary (for context window management)
    session_summary: SessionSummary = Field(default_factory=SessionSummary)

    # Idempotency
    last_processed_turn: int = 0

    # Final Report
    report: Optional[SessionReport] = None

    # Error
    error_message: Optional[str] = None

    def get_analytics(self) -> AnalyticsSnapshot:
        """Build a live analytics snapshot from current session state."""
        bloom_dist: dict[str, int] = {}
        for turn in self.conversation:
            level = turn.bloom_level.value if isinstance(turn.bloom_level, BloomLevel) else str(turn.bloom_level)
            bloom_dist[level] = bloom_dist.get(level, 0) + 1

        # Calculate running averages from turn analyses
        if self.turn_analyses:
            n = len(self.turn_analyses)
            teaching = sum(a.conceptual_clarity for a in self.turn_analyses) / n
            communication = sum(a.structure for a in self.turn_analyses) / n
            engagement = sum(a.student_alignment for a in self.turn_analyses) / n
            satisfaction = sum(a.doubt_resolution for a in self.turn_analyses) / n
        else:
            teaching = communication = engagement = satisfaction = 0.0

        corrected = sum(1 for m in self.misconceptions if m.status == "Corrected")
        missed = sum(1 for m in self.misconceptions if m.status == "Missed")

        return AnalyticsSnapshot(
            teaching_score=round(teaching, 3),
            communication_score=round(communication, 3),
            engagement_score=round(engagement, 3),
            student_satisfaction=round(satisfaction, 3),
            learning_gain=round(self.understanding_estimate, 3),
            current_bloom_level=self.current_bloom_level.value if isinstance(self.current_bloom_level, BloomLevel) else str(self.current_bloom_level),
            turn_number=self.current_turn,
            max_turns=self.max_turns,
            current_topic=self.current_topic or self.subject,
            bloom_distribution=bloom_dist,
            total_misconceptions=len(self.misconceptions),
            corrected_misconceptions=corrected,
            missed_misconceptions=missed,
            total_evidence_packets=len(self.evidence_packets),
            understanding_estimate=round(self.understanding_estimate, 3),
            concepts_explored=len(self.concepts_covered),
        )
