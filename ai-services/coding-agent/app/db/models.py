"""
FacultyIQ Coding Intelligence Agent — SQLAlchemy ORM Models.

Normalized schema for sessions, questions, submissions, scores, and evidence.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean,
    DateTime, ForeignKey, JSON, Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ─── Questions ────────────────────────────────────────────────────────────────

class QuestionORM(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=_uuid)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(64), nullable=False, index=True)
    difficulty = Column(String(16), nullable=False, index=True)
    bloom_level = Column(String(32), nullable=False)
    tags = Column(JSON, default=list)
    constraints = Column(Text, default="")
    expected_time_complexity = Column(String(32), default="")
    expected_space_complexity = Column(String(32), default="")
    starter_code = Column(JSON, default=dict)       # {language: code}
    solution_code = Column(JSON, default=dict)       # {language: code}
    hints = Column(JSON, default=list)
    is_debugging = Column(Boolean, default=False)
    buggy_code = Column(JSON, default=dict)          # {language: code} for debug questions
    bug_description = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)

    test_cases = relationship("TestCaseORM", back_populates="question", cascade="all, delete-orphan")


class TestCaseORM(Base):
    __tablename__ = "test_cases"

    id = Column(String, primary_key=True, default=_uuid)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False, index=True)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False)
    is_stress = Column(Boolean, default=False)
    is_edge_case = Column(Boolean, default=False)
    description = Column(String(256), default="")
    time_limit_ms = Column(Integer, default=5000)

    question = relationship("QuestionORM", back_populates="test_cases")


# ─── Sessions ─────────────────────────────────────────────────────────────────

class SessionORM(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=_uuid)
    candidate_name = Column(String(128), default="")
    candidate_email = Column(String(128), default="")
    department = Column(String(64), default="")
    programming_language = Column(String(32), default="python")
    difficulty = Column(String(16), default="medium")
    status = Column(String(16), default="active", index=True)  # active | completed | expired
    total_score = Column(Float, default=0.0)
    questions_answered = Column(Integer, default=0)
    max_questions = Column(Integer, default=10)
    started_at = Column(DateTime, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)
    evidence_json = Column(JSON, nullable=True)

    submissions = relationship("SubmissionORM", back_populates="session", cascade="all, delete-orphan")


# ─── Submissions ──────────────────────────────────────────────────────────────

class SubmissionORM(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    language = Column(String(32), nullable=False)
    source_code = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=_utcnow)

    # Compilation results
    compiled_ok = Column(Boolean, nullable=True)
    compilation_error = Column(Text, default="")
    compilation_time_ms = Column(Float, default=0.0)

    # Execution results
    execution_time_ms = Column(Float, default=0.0)
    memory_used_kb = Column(Float, default=0.0)
    stdout = Column(Text, default="")
    stderr = Column(Text, default="")
    exit_code = Column(Integer, nullable=True)

    # Test results
    public_tests_passed = Column(Integer, default=0)
    public_tests_total = Column(Integer, default=0)
    hidden_tests_passed = Column(Integer, default=0)
    hidden_tests_total = Column(Integer, default=0)
    test_results_json = Column(JSON, nullable=True)

    # Analysis scores
    correctness_score = Column(Float, default=0.0)
    complexity_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    explanation_score = Column(Float, default=0.0)
    viva_score = Column(Float, default=0.0)
    debugging_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)

    # Analysis details
    estimated_time_complexity = Column(String(32), default="")
    estimated_space_complexity = Column(String(32), default="")
    complexity_confidence = Column(Float, default=0.0)
    static_analysis_json = Column(JSON, nullable=True)
    explanation_text = Column(Text, default="")
    explanation_eval_json = Column(JSON, nullable=True)
    viva_json = Column(JSON, nullable=True)

    session = relationship("SessionORM", back_populates="submissions")


# ─── Audit Log ────────────────────────────────────────────────────────────────

class AuditLogORM(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, nullable=True, index=True)
    event_type = Column(String(64), nullable=False)
    event_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=_utcnow)
