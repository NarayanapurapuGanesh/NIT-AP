"""Session Manager — authoritative session store and state machine.

The Python service owns session state. Sessions are stored in-memory with
optional SQLite persistence for crash recovery. Each session is protected
by an asyncio lock for concurrency control.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from loguru import logger

from config.settings import settings
from config.scoring_config import scoring_config
from models.session_state import (
    InteractionSession,
    SessionStatus,
    Turn,
    SpeakerRole,
    BloomLevel,
    DifficultyLevel,
    TurnAnalysis,
    TurnEvidence,
    EvidencePacket,
    MisconceptionState,
    BloomProgressEntry,
    SessionSummary,
    SessionReport,
    TeachingScores,
    AnalyticsSnapshot,
)


class SessionManager:
    """Manages interaction session lifecycle, state transitions, and persistence."""

    def __init__(self):
        self._sessions: dict[str, InteractionSession] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._db_path = Path(__file__).parent.parent / "data" / "sessions.db"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ─── Database ────────────────────────────────────────────────

    def _init_db(self):
        """Initialize SQLite database for session persistence."""
        try:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()
            logger.info(f"[SESSION_MGR] SQLite DB initialized at {self._db_path}")
        except Exception as e:
            logger.warning(f"[SESSION_MGR] SQLite init failed (non-fatal): {e}")

    def _persist(self, session: InteractionSession):
        """Persist session state to SQLite."""
        try:
            conn = sqlite3.connect(str(self._db_path))
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "INSERT OR REPLACE INTO sessions (session_id, state_json, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (session.session_id, session.model_dump_json(), session.created_at, now),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"[SESSION_MGR] Persist failed (non-fatal): {e}")

    def _load_from_db(self, session_id: str) -> Optional[InteractionSession]:
        """Load a session from SQLite."""
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.execute(
                "SELECT state_json FROM sessions WHERE session_id = ?", (session_id,)
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return InteractionSession.model_validate_json(row[0])
        except Exception as e:
            logger.warning(f"[SESSION_MGR] Load from DB failed: {e}")
        return None

    # ─── Lock Management ─────────────────────────────────────────

    def _get_lock(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()
        return self._locks[session_id]

    # ─── Session Lifecycle ───────────────────────────────────────

    async def create_session(
        self,
        candidate_id: str,
        subject: str,
        department: str,
        persona_type: str = "Beginner",
        max_turns: int = 12,
    ) -> InteractionSession:
        """Create a new interaction session."""
        session = InteractionSession(
            candidate_id=candidate_id,
            subject=subject,
            department=department,
            persona_type=persona_type,
            max_turns=max_turns,
            current_topic=subject,
            status=SessionStatus.INITIALIZING,
        )
        self._sessions[session.session_id] = session
        self._persist(session)
        logger.info(
            f"[SESSION_MGR] Created session {session.session_id[:8]} "
            f"for {subject} ({persona_type})"
        )
        return session

    async def activate_session(
        self, session_id: str, opening_message: str
    ) -> InteractionSession:
        """Transition session from INITIALIZING to ACTIVE with the opening student message."""
        async with self._get_lock(session_id):
            session = self._get_session(session_id)
            if session.status != SessionStatus.INITIALIZING:
                raise ValueError(
                    f"Cannot activate session in {session.status} state"
                )

            session.status = SessionStatus.ACTIVE
            session.started_at = datetime.now(timezone.utc).isoformat()
            session.last_activity_at = session.started_at
            session.current_turn = 1

            # Add the opening student message as turn 1
            turn = Turn(
                turn_number=1,
                speaker=SpeakerRole.STUDENT,
                message=opening_message,
                bloom_level=session.current_bloom_level,
                difficulty=session.current_difficulty,
                concept=session.subject,
            )
            session.conversation.append(turn)
            self._persist(session)

            logger.info(
                f"[SESSION_MGR] Session {session_id[:8]} activated"
            )
            return session

    async def add_faculty_response(
        self, session_id: str, message: str
    ) -> Turn:
        """Record the faculty's response and return the turn object."""
        async with self._get_lock(session_id):
            session = self._get_session(session_id)
            if session.status != SessionStatus.ACTIVE:
                raise ValueError(
                    f"Cannot add response in {session.status} state"
                )

            # Idempotency: check if we already processed this turn
            expected_turn = session.current_turn + 1
            if expected_turn <= session.last_processed_turn:
                logger.warning(
                    f"[SESSION_MGR] Duplicate turn {expected_turn} for session {session_id[:8]}"
                )
                # Return the already-processed turn
                for t in session.conversation:
                    if t.turn_number == expected_turn and t.speaker == SpeakerRole.FACULTY:
                        return t
                raise ValueError("Inconsistent turn state")

            session.current_turn = expected_turn
            session.last_activity_at = datetime.now(timezone.utc).isoformat()

            turn = Turn(
                turn_number=session.current_turn,
                speaker=SpeakerRole.FACULTY,
                message=message,
                bloom_level=session.current_bloom_level,
                difficulty=session.current_difficulty,
                concept=session.current_topic or session.subject,
            )
            session.conversation.append(turn)
            self._persist(session)
            return turn

    async def add_student_response(
        self,
        session_id: str,
        message: str,
        analysis: Optional[TurnAnalysis] = None,
        new_bloom: Optional[str] = None,
        bloom_reason: Optional[str] = None,
        misconception: Optional[MisconceptionState] = None,
        understanding_estimate: float = 0.3,
        should_end: bool = False,
        end_reason: Optional[str] = None,
    ) -> InteractionSession:
        """Add the AI student response and update session state."""
        async with self._get_lock(session_id):
            session = self._get_session(session_id)

            session.current_turn += 1
            session.last_activity_at = datetime.now(timezone.utc).isoformat()
            session.understanding_estimate = understanding_estimate

            # Record analysis if provided
            if analysis:
                session.turn_analyses.append(analysis)

                # Generate evidence from analysis
                if analysis.conceptual_clarity >= scoring_config.STRENGTH_THRESHOLD:
                    session.evidence_packets.append(EvidencePacket(
                        turn_number=session.current_turn - 1,
                        type="STRENGTH",
                        score=analysis.conceptual_clarity,
                        justification=analysis.evidence_justification or "Clear concept explanation",
                        confidence=analysis.confidence,
                        bloom_level=session.current_bloom_level,
                    ))
                if analysis.doubt_resolution <= scoring_config.WEAKNESS_THRESHOLD:
                    session.evidence_packets.append(EvidencePacket(
                        turn_number=session.current_turn - 1,
                        type="WEAKNESS",
                        score=analysis.doubt_resolution,
                        justification=analysis.evidence_justification or "Did not adequately address student doubt",
                        confidence=analysis.confidence,
                        bloom_level=session.current_bloom_level,
                    ))

            # Handle Bloom level change
            if new_bloom and new_bloom in [b.value for b in BloomLevel]:
                old_bloom = session.current_bloom_level
                new_bloom_enum = BloomLevel(new_bloom)
                session.bloom_progress.append(BloomProgressEntry(
                    turn_number=session.current_turn,
                    from_level=old_bloom,
                    to_level=new_bloom_enum,
                    topic=session.current_topic or session.subject,
                    reason=bloom_reason or "",
                ))
                session.current_bloom_level = new_bloom_enum

                # Adjust difficulty with Bloom
                if new_bloom_enum in (BloomLevel.REMEMBER, BloomLevel.UNDERSTAND):
                    session.current_difficulty = DifficultyLevel.FOUNDATIONAL
                elif new_bloom_enum == BloomLevel.APPLY:
                    session.current_difficulty = DifficultyLevel.INTERMEDIATE
                elif new_bloom_enum == BloomLevel.ANALYZE:
                    session.current_difficulty = DifficultyLevel.ADVANCED
                else:
                    session.current_difficulty = DifficultyLevel.EXPERT

            # Handle misconception
            if misconception:
                session.misconceptions.append(misconception)

            # Add student turn
            turn = Turn(
                turn_number=session.current_turn,
                speaker=SpeakerRole.STUDENT,
                message=message,
                bloom_level=session.current_bloom_level,
                difficulty=session.current_difficulty,
                concept=session.current_topic or session.subject,
                understanding_estimate=understanding_estimate,
            )
            session.conversation.append(turn)
            session.last_processed_turn = session.current_turn

            # Check session end conditions
            if should_end or session.current_turn >= session.max_turns * 2:
                session.status = SessionStatus.COMPLETING

            self._persist(session)
            return session

    async def pause_session(self, session_id: str) -> InteractionSession:
        """Pause the session."""
        async with self._get_lock(session_id):
            session = self._get_session(session_id)
            if session.status != SessionStatus.ACTIVE:
                raise ValueError(f"Cannot pause session in {session.status} state")
            session.status = SessionStatus.PAUSED
            session.paused_at = datetime.now(timezone.utc).isoformat()
            self._persist(session)
            return session

    async def resume_session(self, session_id: str) -> InteractionSession:
        """Resume a paused session."""
        async with self._get_lock(session_id):
            session = self._get_session(session_id)
            if session.status != SessionStatus.PAUSED:
                raise ValueError(f"Cannot resume session in {session.status} state")
            session.status = SessionStatus.ACTIVE
            session.paused_at = None
            session.last_activity_at = datetime.now(timezone.utc).isoformat()
            self._persist(session)
            return session

    async def complete_session(self, session_id: str) -> InteractionSession:
        """Mark session as completed."""
        async with self._get_lock(session_id):
            session = self._get_session(session_id)
            if session.status not in (SessionStatus.ACTIVE, SessionStatus.PAUSED, SessionStatus.COMPLETING):
                raise ValueError(f"Cannot complete session in {session.status} state")
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc).isoformat()
            self._persist(session)
            return session

    async def set_report(
        self, session_id: str, report: SessionReport
    ) -> InteractionSession:
        """Attach the final evaluation report to the session."""
        async with self._get_lock(session_id):
            session = self._get_session(session_id)
            session.report = report
            session.status = SessionStatus.EVALUATED
            self._persist(session)
            return session

    async def set_error(self, session_id: str, error: str) -> InteractionSession:
        """Mark session as errored."""
        async with self._get_lock(session_id):
            session = self._get_session(session_id)
            session.status = SessionStatus.ERROR
            session.error_message = error
            self._persist(session)
            return session

    # ─── Queries ─────────────────────────────────────────────────

    def get_session(self, session_id: str) -> Optional[InteractionSession]:
        """Get a session by ID (checks memory, then DB)."""
        session = self._sessions.get(session_id)
        if not session:
            session = self._load_from_db(session_id)
            if session:
                self._sessions[session_id] = session
        return session

    def _get_session(self, session_id: str) -> InteractionSession:
        """Get session or raise ValueError."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session

    def get_analytics(self, session_id: str) -> AnalyticsSnapshot:
        """Get live analytics for the frontend."""
        session = self._get_session(session_id)
        return session.get_analytics()

    def build_report(self, session_id: str) -> SessionReport:
        """Build a final evaluation report from collected evidence and turn analyses."""
        session = self._get_session(session_id)

        # Average each dimension across all turn analyses
        analyses = session.turn_analyses
        n = max(1, len(analyses))

        avg_accuracy = sum(a.technical_accuracy for a in analyses) / n
        avg_clarity = sum(a.conceptual_clarity for a in analyses) / n
        avg_resolution = sum(a.doubt_resolution for a in analyses) / n
        avg_adaptive = sum(a.adaptive_teaching for a in analyses) / n
        avg_structure = sum(a.structure for a in analyses) / n
        avg_example = sum(a.example_quality for a in analyses) / n
        avg_misconception = sum(a.misconception_handling for a in analyses) / n

        # Bloom depth: proportion of higher-order levels covered
        bloom_counts = {}
        for t in session.conversation:
            level = t.bloom_level.value if isinstance(t.bloom_level, BloomLevel) else str(t.bloom_level)
            bloom_counts[level] = bloom_counts.get(level, 0) + 1

        total_bloom = max(1, sum(bloom_counts.values()))
        higher_order = sum(
            bloom_counts.get(l, 0)
            for l in ["Apply", "Analyze", "Evaluate", "Create"]
        )
        bloom_depth = higher_order / total_bloom

        # Bloom profile (percentage per level)
        bloom_profile = {
            level: round(count / total_bloom, 3)
            for level, count in bloom_counts.items()
        }

        scores = TeachingScores(
            technical_accuracy=round(avg_accuracy, 3),
            concept_clarity=round(avg_clarity, 3),
            doubt_resolution=round(avg_resolution, 3),
            pedagogical_adaptability=round(avg_adaptive, 3),
            explanation_structure=round(avg_structure, 3),
            example_quality=round(avg_example, 3),
            bloom_depth=round(bloom_depth, 3),
            misconception_handling=round(avg_misconception, 3),
        )

        overall = scoring_config.calculate_overall_score(
            technical_accuracy=avg_accuracy,
            concept_clarity=avg_clarity,
            doubt_resolution=avg_resolution,
            pedagogical_adaptability=avg_adaptive,
            explanation_structure=avg_structure,
            example_quality=avg_example,
            bloom_depth=bloom_depth,
            misconception_handling=avg_misconception,
        )

        # Separate strengths and weaknesses from evidence
        strengths = [
            e.justification for e in session.evidence_packets if e.type == "STRENGTH"
        ]
        weaknesses = [
            e.justification for e in session.evidence_packets if e.type == "WEAKNESS"
        ]

        # Calculate duration
        duration = ""
        if session.started_at and session.completed_at:
            try:
                start = datetime.fromisoformat(session.started_at)
                end = datetime.fromisoformat(session.completed_at)
                delta = end - start
                mins = int(delta.total_seconds() // 60)
                secs = int(delta.total_seconds() % 60)
                duration = f"{mins:02d}:{secs:02d}"
            except Exception:
                duration = "N/A"

        # Average confidence
        avg_confidence = (
            sum(a.confidence for a in analyses) / n if analyses else 0.5
        )

        return SessionReport(
            session_id=session.session_id,
            overall_score=overall,
            recommendation=scoring_config.get_recommendation(overall),
            scores=scores,
            bloom_profile=bloom_profile,
            strengths=strengths[:10],
            weaknesses=weaknesses[:10],
            evidence=session.evidence_packets,
            improvement_areas=[],  # Will be filled by AI evaluation
            confidence=round(avg_confidence, 3),
            total_turns=session.current_turn,
            duration=duration,
            persona_used=session.persona_type,
            subject=session.subject,
            department=session.department,
        )
