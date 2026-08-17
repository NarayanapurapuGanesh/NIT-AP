"""FacultyIQ Interaction Agent — FastAPI Service

Production-grade teaching interaction engine. The Python service is the
authoritative session owner — it manages session state, drives AI inference,
evaluates teaching quality, and persists results.

Architecture:
  Frontend (Next.js) → This Service → Ollama (local LLM)
                                    → Session Manager (SQLite)

Endpoints:
  POST /api/interaction/sessions                    — Create & start a session
  GET  /api/interaction/sessions/{id}               — Get session state (recovery)
  POST /api/interaction/sessions/{id}/respond       — Faculty sends a message
  POST /api/interaction/sessions/{id}/pause         — Pause session
  POST /api/interaction/sessions/{id}/resume        — Resume session
  POST /api/interaction/sessions/{id}/end           — End session & get report
  GET  /api/interaction/sessions/{id}/report        — Get final report
  GET  /api/interaction/sessions/{id}/analytics     — Get live analytics
  GET  /api/interaction/health                      — Dependency health check
  POST /api/interaction/opening                     — Generate opening message (legacy .NET compat)
  POST /api/interaction/respond                     — Process turn (legacy .NET compat)
  POST /api/interaction/evaluate                    — Final evaluation (legacy .NET compat)
"""

import time
import asyncio
import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field
from typing import Optional

from config.settings import settings
from services.ollama_service import OllamaService
from services.session_manager import SessionManager
from graphs.interaction_graph import InteractionOrchestrator
from models.session_state import (
    SessionStatus,
    TurnAnalysis,
    MisconceptionState,
    AnalyticsSnapshot,
)
from models.schemas import (
    InteractionRequest,
    InteractionResponse,
    FinalEvaluationRequest,
    SessionReport as LegacySessionReport,
    ConversationMessage,
    TeachingEvaluation,
)


# ─── Lifespan ────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FacultyIQ Interaction Agent...")
    logger.info(f"Student Model: {settings.STUDENT_MODEL}")
    logger.info(f"Evaluator Model: {settings.EVALUATOR_MODEL}")
    logger.info(f"Ollama URL: {settings.OLLAMA_BASE_URL}")

    is_available = await ollama.is_available()
    if is_available:
        logger.info("Ollama connection verified ✓")
    else:
        logger.warning("Ollama is not available — the service will start but inference will fail")

    yield
    logger.info("Shutting down Interaction Agent.")


app = FastAPI(
    title="FacultyIQ Interaction Agent",
    description="AI-powered Teaching Interaction Evaluation Engine",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ollama = OllamaService()
orchestrator = InteractionOrchestrator(ollama)
session_mgr = SessionManager()


# ═══════════════════════════════════════════════════════════════════
#  Request / Response Models
# ═══════════════════════════════════════════════════════════════════


class CreateSessionRequest(BaseModel):
    candidate_id: str = ""
    subject: str
    department: str
    persona_type: str = "Beginner"
    max_turns: int = Field(default=12, ge=4, le=30)


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str
    persona_type: str
    subject: str
    department: str
    opening_message: str
    current_bloom_level: str
    max_turns: int


class FacultyRespondRequest(BaseModel):
    message: str


class FacultyRespondResponse(BaseModel):
    student_message: str
    turn_number: int
    current_bloom_level: str
    session_complete: bool
    analytics: AnalyticsSnapshot


class SessionStateResponse(BaseModel):
    session_id: str
    status: str
    subject: str
    department: str
    persona_type: str
    current_turn: int
    max_turns: int
    current_bloom_level: str
    understanding_estimate: float
    conversation: list[dict]
    analytics: AnalyticsSnapshot


class HealthResponse(BaseModel):
    status: str
    ollama: str
    student_model: str
    evaluator_model: str
    student_model_available: bool
    evaluator_model_available: bool


class OpeningRequest(BaseModel):
    persona_type: str
    subject: str
    department: str


class OpeningResponse(BaseModel):
    student_message: str


# ═══════════════════════════════════════════════════════════════════
#  Health Check
# ═══════════════════════════════════════════════════════════════════


@app.get("/api/interaction/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive dependency health check."""
    ollama_ok = await ollama.is_available()

    # Check specific models
    student_model_ok = False
    evaluator_model_ok = False
    if ollama_ok:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                if resp.status_code == 200:
                    models = [m["name"] for m in resp.json().get("models", [])]
                    student_model_ok = settings.STUDENT_MODEL in models
                    evaluator_model_ok = settings.EVALUATOR_MODEL in models
        except Exception:
            pass

    overall = "healthy" if (ollama_ok and student_model_ok) else "degraded"
    if not ollama_ok:
        overall = "unhealthy"

    return HealthResponse(
        status=overall,
        ollama="available" if ollama_ok else "unavailable",
        student_model=settings.STUDENT_MODEL,
        evaluator_model=settings.EVALUATOR_MODEL,
        student_model_available=student_model_ok,
        evaluator_model_available=evaluator_model_ok,
    )


# ═══════════════════════════════════════════════════════════════════
#  Session Lifecycle Endpoints
# ═══════════════════════════════════════════════════════════════════


@app.post("/api/interaction/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create and start a new teaching interaction session.

    1. Validates dependencies (Ollama + model).
    2. Creates session state.
    3. Generates opening student question via LLM.
    4. Returns the session with the first student message.
    """
    start_time = time.time()

    # Pre-flight: Check Ollama
    ollama_ok = await ollama.is_available()
    if not ollama_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "AI Student unavailable",
                "message": "Ollama is not responding. Check that Ollama is running and the configured model is available.",
                "retry": True,
            },
        )

    try:
        # Create session
        session = await session_mgr.create_session(
            candidate_id=request.candidate_id,
            subject=request.subject,
            department=request.department,
            persona_type=request.persona_type,
            max_turns=request.max_turns,
        )

        # Generate opening student message
        try:
            opening_message = await asyncio.wait_for(
                orchestrator.generate_opening(
                    persona_type=request.persona_type,
                    subject=request.subject,
                    department=request.department,
                ),
                timeout=settings.OLLAMA_TIMEOUT,
            )
        except asyncio.TimeoutError:
            opening_message = (
                f"Hi, I'm trying to understand {request.subject} but I'm finding "
                f"some concepts really confusing. Can you help me with the basics?"
            )
            logger.warning("[SESSION] Opening message timed out, using fallback")
        except Exception as e:
            logger.warning(f"[SESSION] Opening generation failed, using fallback: {e}")
            opening_message = (
                f"Hello! I've been studying {request.subject} and there are "
                f"some things I don't quite understand. Could you explain the "
                f"fundamental concepts to me?"
            )

        # Activate session with the opening message
        session = await session_mgr.activate_session(
            session.session_id, opening_message
        )

        elapsed = time.time() - start_time
        logger.info(
            f"[SESSION] Session {session.session_id[:8]} started in {elapsed:.2f}s"
        )

        return CreateSessionResponse(
            session_id=session.session_id,
            status=session.status.value,
            persona_type=session.persona_type,
            subject=session.subject,
            department=session.department,
            opening_message=opening_message,
            current_bloom_level=session.current_bloom_level.value,
            max_turns=session.max_turns,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SESSION] Create failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to create session", "message": str(e)},
        )


@app.get("/api/interaction/sessions/{session_id}", response_model=SessionStateResponse)
async def get_session(session_id: str):
    """Get full session state for recovery after page refresh."""
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionStateResponse(
        session_id=session.session_id,
        status=session.status.value,
        subject=session.subject,
        department=session.department,
        persona_type=session.persona_type,
        current_turn=session.current_turn,
        max_turns=session.max_turns,
        current_bloom_level=session.current_bloom_level.value,
        understanding_estimate=session.understanding_estimate,
        conversation=[
            {
                "turn_number": t.turn_number,
                "speaker": t.speaker.value,
                "message": t.message,
                "bloom_level": t.bloom_level.value if hasattr(t.bloom_level, 'value') else str(t.bloom_level),
                "timestamp": t.timestamp,
            }
            for t in session.conversation
        ],
        analytics=session.get_analytics(),
    )


@app.post(
    "/api/interaction/sessions/{session_id}/respond",
    response_model=FacultyRespondResponse,
)
async def faculty_respond(session_id: str, request: FacultyRespondRequest):
    """Process the faculty's response through the full evaluation pipeline.

    1. Records faculty message.
    2. Evaluates teaching quality (Qwen 2.5).
    3. Classifies Bloom level.
    4. Checks misconception handling.
    5. Generates adaptive student response (Llama 3.2).
    6. Returns the student's next message + analytics.
    """
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == SessionStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Session is paused")
    if session.status not in (SessionStatus.ACTIVE, SessionStatus.COMPLETING):
        raise HTTPException(
            status_code=400,
            detail=f"Session is in {session.status.value} state",
        )

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    start_time = time.time()

    try:
        # Record the faculty message
        faculty_turn = await session_mgr.add_faculty_response(
            session_id, request.message.strip()
        )

        # Build the AI request from session state
        conversation_msgs = [
            ConversationMessage(
                role=t.speaker.value,
                content=t.message,
                turn_number=t.turn_number,
            )
            for t in session.conversation
        ]

        active_misconceptions = [
            {"misconception_text": m.misconception_text, "correct_concept": m.correct_concept, "status": m.status}
            for m in session.misconceptions
            if m.status in ("Presented", "Identified")
        ]

        ai_request = InteractionRequest(
            session_id=session_id,
            faculty_message=request.message.strip(),
            persona_type=session.persona_type,
            subject=session.subject,
            department=session.department,
            turn_number=session.current_turn,
            max_turns=session.max_turns,
            current_bloom_level=session.current_bloom_level.value,
            current_difficulty=session.current_difficulty.value,
            conversation_history=conversation_msgs,
            active_misconceptions=[
                __import__("models.schemas", fromlist=["ActiveMisconception"]).ActiveMisconception(**m)
                for m in active_misconceptions
            ],
            faculty_context_json=None,
        )

        # Run through the LangGraph pipeline
        try:
            ai_response = await asyncio.wait_for(
                orchestrator.process_turn(ai_request),
                timeout=settings.OLLAMA_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.warning(f"[SESSION] AI pipeline timed out for session {session_id[:8]}")
            ai_response = InteractionResponse(
                student_message="I see what you mean. Can you explain that in a different way? Maybe with a simpler example?",
                current_bloom_level=session.current_bloom_level.value,
                understanding_estimate=session.understanding_estimate,
            )
        except Exception as e:
            logger.error(f"[SESSION] AI pipeline failed: {e}")
            ai_response = InteractionResponse(
                student_message="Hmm, I'm still thinking about what you said. Can you elaborate a bit more?",
                current_bloom_level=session.current_bloom_level.value,
                understanding_estimate=session.understanding_estimate,
            )

        # Extract analysis from evaluation
        analysis = None
        if ai_response.evaluation:
            ev = ai_response.evaluation
            analysis = TurnAnalysis(
                technical_accuracy=ev.technical_accuracy,
                conceptual_clarity=ev.concept_clarity,
                structure=ev.logical_flow,
                example_quality=ev.example_quality,
                student_alignment=ev.question_handling,
                misconception_handling=ev.doubt_clarification,
                depth=ev.depth,
                pedagogical_quality=ev.adaptive_teaching,
                doubt_resolution=ev.doubt_clarification,
                adaptive_teaching=ev.adaptive_teaching,
                evidence_justification=ev.evidence_justification,
                confidence=ev.confidence,
            )

        # Build misconception state if any
        misconception = None
        if ai_response.new_misconception:
            m = ai_response.new_misconception
            misconception = MisconceptionState(
                misconception_text=m.misconception_text,
                correct_concept=m.correct_concept,
                subject_category=m.subject_category,
                presented_at_turn=session.current_turn,
            )

        # Update session state with the student response
        session = await session_mgr.add_student_response(
            session_id=session_id,
            message=ai_response.student_message,
            analysis=analysis,
            new_bloom=ai_response.new_bloom_level,
            bloom_reason=ai_response.bloom_transition_reason,
            misconception=misconception,
            understanding_estimate=ai_response.understanding_estimate,
            should_end=ai_response.should_end_session,
            end_reason=ai_response.end_session_reason,
        )

        # Handle misconception corrections
        if ai_response.misconception_correction:
            mc = ai_response.misconception_correction
            for m in session.misconceptions:
                if m.misconception_text == mc.misconception_text and m.status == "Presented":
                    if mc.fully_corrected:
                        m.status = "Corrected"
                    else:
                        m.status = "PartiallyCorrected"
                    m.corrected_at_turn = session.current_turn
                    m.correction_quality = mc.correction_quality
                    break

        session_complete = session.status in (
            SessionStatus.COMPLETING, SessionStatus.COMPLETED
        )

        elapsed = time.time() - start_time
        logger.info(
            f"[SESSION] Turn processed in {elapsed:.2f}s | "
            f"Session {session_id[:8]} | Turn {session.current_turn} | "
            f"Bloom: {session.current_bloom_level.value} | "
            f"Understanding: {session.understanding_estimate:.2f}"
        )

        return FacultyRespondResponse(
            student_message=ai_response.student_message,
            turn_number=session.current_turn,
            current_bloom_level=session.current_bloom_level.value,
            session_complete=session_complete,
            analytics=session.get_analytics(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SESSION] Respond failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process response", "message": str(e)},
        )


@app.post("/api/interaction/sessions/{session_id}/pause")
async def pause_session(session_id: str):
    """Pause the session."""
    try:
        session = await session_mgr.pause_session(session_id)
        return {"status": "paused", "session_id": session.session_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/interaction/sessions/{session_id}/resume")
async def resume_session(session_id: str):
    """Resume a paused session."""
    try:
        session = await session_mgr.resume_session(session_id)
        return {"status": "active", "session_id": session.session_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/interaction/sessions/{session_id}/end")
async def end_session(session_id: str):
    """End the session, generate final evaluation, return report."""
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Complete the session
        session = await session_mgr.complete_session(session_id)

        # Build local report from evidence
        report = session_mgr.build_report(session_id)

        # Try AI-powered final evaluation for richer insights
        try:
            history = [
                ConversationMessage(
                    role=t.speaker.value,
                    content=t.message,
                    turn_number=t.turn_number,
                )
                for t in session.conversation
            ]

            ai_eval = await asyncio.wait_for(
                orchestrator.evaluator.generate_final_evaluation(
                    conversation_history=history,
                    faculty_context=None,
                ),
                timeout=60,
            )

            # Merge AI insights into the report
            if ai_eval:
                if ai_eval.get("strengths"):
                    report.strengths = ai_eval["strengths"][:8]
                if ai_eval.get("weaknesses"):
                    report.weaknesses = ai_eval["weaknesses"][:8]
                if ai_eval.get("recommendations"):
                    report.improvement_areas = ai_eval["recommendations"][:6]
                if ai_eval.get("confidence"):
                    report.confidence = max(report.confidence, ai_eval["confidence"])
        except Exception as e:
            logger.warning(f"[SESSION] AI final evaluation failed (using local): {e}")

        # Persist the report
        await session_mgr.set_report(session_id, report)

        return report.model_dump()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SESSION] End session failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to end session", "message": str(e)},
        )


@app.get("/api/interaction/sessions/{session_id}/report")
async def get_report(session_id: str):
    """Get the final evaluation report."""
    session = session_mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.report:
        raise HTTPException(status_code=400, detail="Session has not been evaluated yet")
    return session.report.model_dump()


@app.get("/api/interaction/sessions/{session_id}/analytics")
async def get_analytics(session_id: str):
    """Get live analytics snapshot."""
    try:
        return session_mgr.get_analytics(session_id).model_dump()
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")


# ═══════════════════════════════════════════════════════════════════
#  Legacy .NET Compatibility Endpoints
# ═══════════════════════════════════════════════════════════════════


@app.post("/api/interaction/opening", response_model=OpeningResponse)
async def generate_opening(request: OpeningRequest):
    """Generate the opening student message (legacy .NET backend compat)."""
    try:
        message = await orchestrator.generate_opening(
            persona_type=request.persona_type,
            subject=request.subject,
            department=request.department,
        )
        return OpeningResponse(student_message=message)
    except Exception as e:
        logger.error(f"Opening generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate opening message: {str(e)}",
        )


@app.post("/api/interaction/respond", response_model=InteractionResponse)
async def process_faculty_message(request: InteractionRequest):
    """Process a faculty message (legacy .NET backend compat)."""
    try:
        response = await orchestrator.process_turn(request)
        return response
    except Exception as e:
        logger.error(f"Turn processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process faculty message: {str(e)}",
        )


@app.post("/api/interaction/evaluate", response_model=LegacySessionReport)
async def generate_final_evaluation(request: FinalEvaluationRequest):
    """Generate final evaluation (legacy .NET backend compat)."""
    try:
        history = request.conversation_history
        eval_result = await orchestrator.evaluator.generate_final_evaluation(
            conversation_history=history,
            faculty_context=request.faculty_context_json,
        )
        return LegacySessionReport(
            session_id=request.session_id,
            overall_teaching_effectiveness=eval_result.get("overall_teaching_effectiveness", 0.5),
            scores=eval_result.get("scores", {}),
            bloom_distribution=eval_result.get("bloom_distribution", {}),
            strengths=eval_result.get("strengths", []),
            weaknesses=eval_result.get("weaknesses", []),
            evidence=eval_result.get("evidence", []),
            recommendations=eval_result.get("recommendations", []),
            confidence=eval_result.get("confidence", 0.5),
            total_turns=len(history),
        )
    except Exception as e:
        logger.error(f"Final evaluation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate final evaluation: {str(e)}",
        )


@app.get("/api/health")
async def legacy_health_check():
    """Legacy health check."""
    ollama_ok = await ollama.is_available()
    return {
        "status": "healthy" if ollama_ok else "degraded",
        "ollama_available": ollama_ok,
        "student_model": settings.STUDENT_MODEL,
        "evaluator_model": settings.EVALUATOR_MODEL,
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
    )
