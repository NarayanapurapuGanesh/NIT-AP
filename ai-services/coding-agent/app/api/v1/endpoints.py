"""
FacultyIQ Coding Intelligence Agent — REST API Endpoints.

Complete FastAPI router for the Coding Assessment Agent.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.logging import get_module_logger
from app.db.session import get_db
from app.db.models import SessionORM, SubmissionORM, AuditLogORM
from app.models.question import QuestionDTO, QuestionFilter, QuestionListResponse
from app.services.question_bank import QuestionBankService
from app.services.adaptive_generator import AdaptiveQuestionGenerator
from app.services.compilation_engine import CompilationEngine
from app.services.test_runner import TestRunner
from app.services.complexity_analyzer import ComplexityAnalyzer
from app.services.static_analyzer import StaticAnalyzer
from app.services.explanation_evaluator import ExplanationEvaluator
from app.services.viva_engine import VivaEngine
from app.services.evidence_builder import EvidenceBuilder

log = get_module_logger("api")

router = APIRouter(prefix="/coding", tags=["Coding Agent"])

# ─── Service instances ────────────────────────────────────────────────────────
question_bank = QuestionBankService()
adaptive_gen = AdaptiveQuestionGenerator(question_bank)
compilation_engine = CompilationEngine()
test_runner = TestRunner(compilation_engine)
complexity_analyzer = ComplexityAnalyzer()
static_analyzer = StaticAnalyzer()
explanation_evaluator = ExplanationEvaluator()
viva_engine = VivaEngine()
evidence_builder = EvidenceBuilder()


# ─── Request / Response Schemas ───────────────────────────────────────────────

class StartSessionRequest(BaseModel):
    candidate_name: str = ""
    candidate_email: str = ""
    department: str = ""
    programming_language: str = "python"
    difficulty: str = "medium"
    max_questions: int = 10


class SessionResponse(BaseModel):
    session_id: str
    status: str
    candidate_name: str
    programming_language: str
    difficulty: str
    questions_answered: int
    max_questions: int
    total_score: float
    started_at: str


class NextQuestionRequest(BaseModel):
    session_id: str


class SubmitCodeRequest(BaseModel):
    session_id: str
    question_id: str
    source_code: str
    language: str = "python"


class RunCodeRequest(BaseModel):
    source_code: str
    language: str = "python"
    stdin: str = ""


class RunCodeResponse(BaseModel):
    status: str
    stdout: str
    stderr: str
    execution_time_ms: float
    exit_code: int


class SubmitExplanationRequest(BaseModel):
    submission_id: str
    explanation: str


class GenerateVivaRequest(BaseModel):
    submission_id: str
    count: int = 3


class AnswerVivaRequest(BaseModel):
    submission_id: str
    question: str
    answer: str


class SubmissionResultResponse(BaseModel):
    submission_id: str
    status: str
    correctness_score: float
    complexity_score: float
    quality_score: float
    overall_score: float
    test_results: dict
    complexity_analysis: dict
    static_analysis: dict


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/session/start", response_model=SessionResponse)
def start_session(req: StartSessionRequest, db: Session = Depends(get_db)):
    """Start a new coding assessment session."""
    session = SessionORM(
        id=str(uuid.uuid4()),
        candidate_name=req.candidate_name,
        candidate_email=req.candidate_email,
        department=req.department,
        programming_language=req.programming_language,
        difficulty=req.difficulty,
        max_questions=req.max_questions,
        status="active",
    )
    db.add(session)
    db.add(AuditLogORM(
        session_id=session.id,
        event_type="session_started",
        event_data={"candidate": req.candidate_name, "language": req.programming_language},
    ))
    db.commit()

    log.info("Session started: {} for {}", session.id[:8], req.candidate_name or "anonymous")

    return SessionResponse(
        session_id=session.id,
        status=session.status,
        candidate_name=session.candidate_name,
        programming_language=session.programming_language,
        difficulty=session.difficulty,
        questions_answered=0,
        max_questions=session.max_questions,
        total_score=0.0,
        started_at=session.started_at.isoformat(),
    )


@router.get("/session/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get session status."""
    session = db.query(SessionORM).filter(SessionORM.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        session_id=session.id,
        status=session.status,
        candidate_name=session.candidate_name,
        programming_language=session.programming_language,
        difficulty=session.difficulty,
        questions_answered=session.questions_answered,
        max_questions=session.max_questions,
        total_score=session.total_score,
        started_at=session.started_at.isoformat(),
    )


@router.post("/question/next")
def next_question(req: NextQuestionRequest, db: Session = Depends(get_db)):
    """Get the next adaptive question for the session."""
    session = db.query(SessionORM).filter(SessionORM.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is no longer active")
    if session.questions_answered >= session.max_questions:
        raise HTTPException(status_code=400, detail="Maximum questions reached")

    # Get already-answered question IDs
    submissions = db.query(SubmissionORM).filter(
        SubmissionORM.session_id == session.id
    ).all()
    answered_ids = [s.question_id for s in submissions]
    answered_categories = []
    for s in submissions:
        from app.db.models import QuestionORM
        q = db.query(QuestionORM).filter(QuestionORM.id == s.question_id).first()
        if q:
            answered_categories.append(q.category)

    question = adaptive_gen.next_question(
        db=db,
        answered_ids=answered_ids,
        answered_categories=answered_categories,
        current_score=session.total_score,
        questions_answered=session.questions_answered,
        preferred_difficulty=session.difficulty,
        preferred_language=session.programming_language,
    )

    if not question:
        raise HTTPException(status_code=404, detail="No more questions available")

    db.add(AuditLogORM(
        session_id=session.id,
        event_type="question_served",
        event_data={"question_id": question.id, "title": question.title},
    ))
    db.commit()

    return question


@router.post("/submit")
def submit_code(req: SubmitCodeRequest, db: Session = Depends(get_db)):
    """Submit code for full evaluation (compile, test, analyze)."""
    session = db.query(SessionORM).filter(SessionORM.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is no longer active")

    question = question_bank.get_question(db, req.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Get ALL test cases (including hidden)
    all_test_cases = question_bank.get_test_cases(db, req.question_id, include_hidden=True)

    # Run tests
    test_summary = test_runner.run_all(req.source_code, req.language, all_test_cases)

    # Complexity analysis
    complexity_result = complexity_analyzer.analyze(
        req.source_code, req.language,
        question.expected_time_complexity,
        question.expected_space_complexity,
    )

    # Static analysis
    static_result = static_analyzer.analyze(req.source_code, req.language)

    # Compute scores
    correctness_score = test_summary.pass_rate
    complexity_score = complexity_result.confidence * 100
    if complexity_result.matches_expected:
        complexity_score = min(complexity_score + 30, 100)
    quality_score = static_result.maintainability_score

    overall = evidence_builder.compute_overall_score(
        correctness_score=correctness_score,
        complexity_score=complexity_score,
        quality_score=quality_score,
    )

    # Save submission
    submission = SubmissionORM(
        id=str(uuid.uuid4()),
        session_id=session.id,
        question_id=req.question_id,
        language=req.language,
        source_code=req.source_code,
        compiled_ok=True,
        public_tests_passed=test_summary.public_passed,
        public_tests_total=len(test_summary.public_results),
        hidden_tests_passed=test_summary.hidden_passed,
        hidden_tests_total=len(test_summary.hidden_results),
        test_results_json=test_summary.to_dict(),
        correctness_score=correctness_score,
        complexity_score=complexity_score,
        quality_score=quality_score,
        overall_score=overall,
        estimated_time_complexity=complexity_result.estimated_time,
        estimated_space_complexity=complexity_result.estimated_space,
        complexity_confidence=complexity_result.confidence,
        static_analysis_json=static_result.to_dict(),
    )

    # Check for compilation errors
    if test_summary.results and test_summary.results[0].verdict == "compilation_error":
        submission.compiled_ok = False
        submission.compilation_error = test_summary.results[0].error

    db.add(submission)

    # Update session
    session.questions_answered += 1
    scores = [s.overall_score for s in session.submissions] + [overall]
    session.total_score = sum(scores) / len(scores) if scores else 0

    if session.questions_answered >= session.max_questions:
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)

    db.add(AuditLogORM(
        session_id=session.id,
        event_type="code_submitted",
        event_data={
            "submission_id": submission.id,
            "question_id": req.question_id,
            "overall_score": overall,
        },
    ))
    db.commit()

    log.info(
        "Submission {} — score: {:.1f} (tests: {}/{}, complexity: {:.0f}, quality: {:.0f})",
        submission.id[:8], overall,
        test_summary.passed, test_summary.total,
        complexity_score, quality_score,
    )

    return {
        "submission_id": submission.id,
        "session_status": session.status,
        "overall_score": overall,
        "correctness_score": round(correctness_score, 1),
        "complexity_score": round(complexity_score, 1),
        "quality_score": round(quality_score, 1),
        "test_results": test_summary.to_dict(),
        "complexity_analysis": complexity_result.to_dict(),
        "static_analysis": static_result.to_dict(),
    }


@router.post("/run", response_model=RunCodeResponse)
def run_code(req: RunCodeRequest):
    """Run code against custom input (no scoring, for candidate testing)."""
    result = compilation_engine.compile_and_run(
        source_code=req.source_code,
        language=req.language,
        stdin=req.stdin,
    )

    return RunCodeResponse(
        status=result.status.value,
        stdout=result.stdout,
        stderr=result.stderr,
        execution_time_ms=result.execution_time_ms,
        exit_code=result.exit_code,
    )


@router.get("/result/{submission_id}")
def get_result(submission_id: str, db: Session = Depends(get_db)):
    """Get detailed result for a submission."""
    sub = db.query(SubmissionORM).filter(SubmissionORM.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    return {
        "submission_id": sub.id,
        "question_id": sub.question_id,
        "language": sub.language,
        "compiled_ok": sub.compiled_ok,
        "compilation_error": sub.compilation_error,
        "correctness_score": sub.correctness_score,
        "complexity_score": sub.complexity_score,
        "quality_score": sub.quality_score,
        "explanation_score": sub.explanation_score,
        "viva_score": sub.viva_score,
        "overall_score": sub.overall_score,
        "test_results": sub.test_results_json,
        "static_analysis": sub.static_analysis_json,
        "estimated_time_complexity": sub.estimated_time_complexity,
        "estimated_space_complexity": sub.estimated_space_complexity,
    }


@router.post("/explanation")
async def submit_explanation(req: SubmitExplanationRequest, db: Session = Depends(get_db)):
    """Submit a code explanation for AI evaluation."""
    sub = db.query(SubmissionORM).filter(SubmissionORM.id == req.submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    from app.db.models import QuestionORM
    question = db.query(QuestionORM).filter(QuestionORM.id == sub.question_id).first()
    title = question.title if question else ""

    score = await explanation_evaluator.evaluate(
        source_code=sub.source_code,
        explanation=req.explanation,
        question_title=title,
        language=sub.language,
    )

    # Update submission
    sub.explanation_text = req.explanation
    sub.explanation_score = score.overall_score
    sub.explanation_eval_json = score.to_dict()

    # Recompute overall
    sub.overall_score = evidence_builder.compute_overall_score(
        correctness_score=sub.correctness_score,
        complexity_score=sub.complexity_score,
        quality_score=sub.quality_score,
        explanation_score=sub.explanation_score,
        viva_score=sub.viva_score,
    )

    db.commit()

    return {"explanation_score": score.to_dict(), "updated_overall": sub.overall_score}


@router.post("/viva/generate")
async def generate_viva(req: GenerateVivaRequest, db: Session = Depends(get_db)):
    """Generate viva follow-up questions for a submission."""
    sub = db.query(SubmissionORM).filter(SubmissionORM.id == req.submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    from app.db.models import QuestionORM
    question = db.query(QuestionORM).filter(QuestionORM.id == sub.question_id).first()

    questions = await viva_engine.generate_questions(
        source_code=sub.source_code,
        question_title=question.title if question else "",
        category=question.category if question else "general",
        difficulty=question.difficulty if question else "medium",
        language=sub.language,
        count=req.count,
    )

    return {"questions": [q.to_dict() for q in questions]}


@router.post("/viva/answer")
async def answer_viva(req: AnswerVivaRequest, db: Session = Depends(get_db)):
    """Submit a viva answer for evaluation."""
    sub = db.query(SubmissionORM).filter(SubmissionORM.id == req.submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    score = await viva_engine.evaluate_answer(
        question=req.question,
        answer=req.answer,
        source_code=sub.source_code,
    )

    # Update viva score (average of all viva answers)
    existing_viva = sub.viva_json or []
    existing_viva.append({
        "question": req.question,
        "answer": req.answer,
        "score": score.score,
        "feedback": score.feedback,
    })
    sub.viva_json = existing_viva

    viva_scores = [v["score"] for v in existing_viva]
    sub.viva_score = sum(viva_scores) / len(viva_scores)

    sub.overall_score = evidence_builder.compute_overall_score(
        correctness_score=sub.correctness_score,
        complexity_score=sub.complexity_score,
        quality_score=sub.quality_score,
        explanation_score=sub.explanation_score,
        viva_score=sub.viva_score,
    )

    db.commit()

    return {"viva_score": score.to_dict(), "updated_overall": sub.overall_score}


@router.get("/report/{session_id}")
def get_report(session_id: str, db: Session = Depends(get_db)):
    """Get the full evidence report for a session."""
    session = db.query(SessionORM).filter(SessionORM.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = {
        "id": session.id,
        "candidate_name": session.candidate_name,
        "candidate_email": session.candidate_email,
        "department": session.department,
        "programming_language": session.programming_language,
        "difficulty": session.difficulty,
        "status": session.status,
        "started_at": session.started_at.isoformat(),
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
    }

    submissions = db.query(SubmissionORM).filter(
        SubmissionORM.session_id == session_id
    ).all()

    submission_evidences = []
    for sub in submissions:
        from app.db.models import QuestionORM
        q = db.query(QuestionORM).filter(QuestionORM.id == sub.question_id).first()
        q_data = {"id": q.id, "title": q.title, "category": q.category,
                  "difficulty": q.difficulty, "bloom_level": q.bloom_level} if q else {}

        evidence = evidence_builder.build_submission_evidence(
            question_data=q_data,
            submission_data={"language": sub.language, "source_code": sub.source_code,
                             "submitted_at": sub.submitted_at.isoformat()},
            test_results=sub.test_results_json or {},
            complexity_data={
                "estimated_time_complexity": sub.estimated_time_complexity,
                "estimated_space_complexity": sub.estimated_space_complexity,
                "confidence": sub.complexity_confidence,
            },
            static_analysis_data=sub.static_analysis_json or {},
            explanation_data=sub.explanation_eval_json,
            viva_data=sub.viva_json,
        )
        submission_evidences.append(evidence)

    report = evidence_builder.build_session_evidence(session_data, submission_evidences)

    # Cache in session
    session.evidence_json = report
    db.commit()

    return report


@router.get("/questions")
def list_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    bloom_level: Optional[str] = None,
    is_debugging: Optional[bool] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List/filter the question bank."""
    filters = QuestionFilter(
        category=category,
        difficulty=difficulty,
        bloom_level=bloom_level,
        is_debugging=is_debugging,
    )
    questions = question_bank.list_questions(db, filters, limit)
    return QuestionListResponse(questions=questions, total=len(questions))


@router.post("/debug/start")
def start_debug(session_id: str, db: Session = Depends(get_db)):
    """Start a debugging challenge."""
    session = db.query(SessionORM).filter(SessionORM.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    filters = QuestionFilter(is_debugging=True)
    question = question_bank.get_random_question(db, filters)
    if not question:
        raise HTTPException(status_code=404, detail="No debugging questions available")

    return question


@router.post("/debug/submit")
def submit_debug(req: SubmitCodeRequest, db: Session = Depends(get_db)):
    """Submit a debugging fix. Same as regular submit but tagged as debug."""
    result = submit_code(req, db)
    return result
