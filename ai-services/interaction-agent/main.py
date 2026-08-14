"""FacultyIQ Interaction Agent — FastAPI Service
Provides the AI-powered teaching interaction pipeline.

Endpoints:
  POST /api/interaction/respond     — Process a faculty message and return student response
  POST /api/interaction/opening     — Generate the opening student message
  POST /api/interaction/evaluate    — Generate final comprehensive evaluation
  GET  /api/health                  — Health check
"""

import uvicorn
from fastapi import FastAPI, HTTPException, status
from loguru import logger

from config.settings import settings
from services.ollama_service import OllamaService
from graphs.interaction_graph import InteractionOrchestrator
from models.schemas import (
    InteractionRequest,
    InteractionResponse,
    FinalEvaluationRequest,
    SessionReport,
    ConversationMessage,
)
from pydantic import BaseModel


app = FastAPI(
    title="FacultyIQ Interaction Agent",
    description="AI-powered Teaching Interaction Evaluation Engine",
    version="1.0.0",
)

# Initialize services
ollama = OllamaService()
orchestrator = InteractionOrchestrator(ollama)


class OpeningRequest(BaseModel):
    persona_type: str
    subject: str
    department: str


class OpeningResponse(BaseModel):
    student_message: str


@app.on_event("startup")
async def startup_event():
    logger.info("Starting FacultyIQ Interaction Agent...")
    logger.info(f"Student Model: {settings.STUDENT_MODEL}")
    logger.info(f"Evaluator Model: {settings.EVALUATOR_MODEL}")
    logger.info(f"Ollama URL: {settings.OLLAMA_BASE_URL}")

    is_available = await ollama.is_available()
    if is_available:
        logger.info("Ollama connection verified ✓")
    else:
        logger.warning("Ollama is not available — the service will start but inference will fail")


@app.post("/api/interaction/opening", response_model=OpeningResponse)
async def generate_opening(request: OpeningRequest):
    """Generate the opening student message to start an interaction session."""
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
    """Process a faculty message through the full evaluation pipeline.

    Evaluates teaching quality, classifies Bloom level, checks misconceptions,
    and generates the next student response.
    """
    try:
        response = await orchestrator.process_turn(request)
        logger.info(
            f"[SESSION {request.session_id}] Turn {request.turn_number} processed | "
            f"Bloom: {response.current_bloom_level} | "
            f"Understanding: {response.understanding_estimate:.2f}"
        )
        return response
    except Exception as e:
        logger.error(f"Turn processing failed for session {request.session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process faculty message: {str(e)}",
        )


@app.post("/api/interaction/evaluate", response_model=SessionReport)
async def generate_final_evaluation(request: FinalEvaluationRequest):
    """Generate a comprehensive final evaluation of the entire teaching session."""
    try:
        history = request.conversation_history
        evaluator = orchestrator.evaluator

        eval_result = await evaluator.generate_final_evaluation(
            conversation_history=history,
            faculty_context=request.faculty_context_json,
        )

        return SessionReport(
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
        logger.error(f"Final evaluation failed for session {request.session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate final evaluation: {str(e)}",
        )


@app.get("/api/health")
async def health_check():
    """Service health check including Ollama connectivity."""
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
