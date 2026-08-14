"""LangGraph Interaction Orchestrator — the central state machine that coordinates
the student simulator, teaching evaluator, misconception generator, and Bloom tracker
into a coherent, explainable interaction pipeline.

State Graph:
  START → generate_student_message → [wait for faculty] → evaluate_teaching →
  update_bloom → check_misconceptions → decide_next_action → generate_student_message
  (loop until session ends)
"""

from __future__ import annotations
import json
from typing import TypedDict, Annotated, Optional
from loguru import logger

from langgraph.graph import StateGraph, END

from services.ollama_service import OllamaService
from agents.student_simulator import StudentSimulator
from agents.teaching_evaluator import TeachingEvaluator
from models.schemas import (
    InteractionRequest,
    InteractionResponse,
    TeachingEvaluation,
    NewMisconception,
    MisconceptionCorrection,
    ConversationMessage,
    ActiveMisconception,
)


class InteractionState(TypedDict):
    """State that flows through the LangGraph interaction pipeline."""
    # Input from .NET backend
    session_id: str
    faculty_message: str
    persona_type: str
    subject: str
    department: str
    turn_number: int
    max_turns: int
    current_bloom_level: str
    current_difficulty: str
    conversation_history: list[dict]
    active_misconceptions: list[dict]
    faculty_context_json: Optional[str]

    # Generated during pipeline
    evaluation: Optional[dict]
    new_bloom_level: Optional[str]
    bloom_should_change: bool
    bloom_transition_reason: Optional[str]
    current_topic: str
    student_message: str
    new_misconception: Optional[dict]
    misconception_correction: Optional[dict]
    understanding_estimate: float
    should_end_session: bool
    end_session_reason: Optional[str]


class InteractionOrchestrator:
    """LangGraph-based orchestrator for the teaching interaction pipeline."""

    def __init__(self, ollama: OllamaService):
        self.ollama = ollama
        self.student = StudentSimulator(ollama)
        self.evaluator = TeachingEvaluator(ollama)
        self._graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        graph = StateGraph(InteractionState)

        # Add nodes
        graph.add_node("evaluate_teaching", self._evaluate_teaching_node)
        graph.add_node("classify_bloom", self._classify_bloom_node)
        graph.add_node("check_misconceptions", self._check_misconceptions_node)
        graph.add_node("generate_student_response", self._generate_student_node)
        graph.add_node("check_session_end", self._check_session_end_node)

        # Define edges (sequential pipeline)
        graph.set_entry_point("evaluate_teaching")
        graph.add_edge("evaluate_teaching", "classify_bloom")
        graph.add_edge("classify_bloom", "check_misconceptions")
        graph.add_edge("check_misconceptions", "generate_student_response")
        graph.add_edge("generate_student_response", "check_session_end")
        graph.add_edge("check_session_end", END)

        return graph.compile()

    async def process_turn(self, request: InteractionRequest) -> InteractionResponse:
        """Process a single interaction turn through the full pipeline.

        This is the main entry point called by the FastAPI endpoint.
        """
        # Build initial state from request
        initial_state: InteractionState = {
            "session_id": request.session_id,
            "faculty_message": request.faculty_message,
            "persona_type": request.persona_type,
            "subject": request.subject,
            "department": request.department,
            "turn_number": request.turn_number,
            "max_turns": request.max_turns,
            "current_bloom_level": request.current_bloom_level,
            "current_difficulty": request.current_difficulty,
            "conversation_history": [m.model_dump() for m in request.conversation_history],
            "active_misconceptions": [m.model_dump() for m in request.active_misconceptions],
            "faculty_context_json": request.faculty_context_json,
            # Pipeline outputs (initialized)
            "evaluation": None,
            "new_bloom_level": None,
            "bloom_should_change": False,
            "bloom_transition_reason": None,
            "current_topic": request.subject,
            "student_message": "",
            "new_misconception": None,
            "misconception_correction": None,
            "understanding_estimate": 0.3,
            "should_end_session": False,
            "end_session_reason": None,
        }

        logger.info(f"[ORCHESTRATOR] Processing turn {request.turn_number} for session {request.session_id}")

        # Execute the graph
        final_state = await self._graph.ainvoke(initial_state)

        # Convert state to response
        return self._build_response(final_state)

    async def generate_opening(
        self, persona_type: str, subject: str, department: str
    ) -> str:
        """Generate the opening student message to start a session."""
        return await self.student.generate_opening_message(
            persona_type, subject, department
        )

    # ─── Graph Nodes ────────────────────────────────────────────────────

    async def _evaluate_teaching_node(self, state: InteractionState) -> dict:
        """Node 1: Evaluate the faculty's teaching quality for this turn."""
        history = [ConversationMessage(**m) for m in state["conversation_history"]]

        evaluation = await self.evaluator.evaluate_turn(
            student_message=self._get_last_student_message(history),
            faculty_response=state["faculty_message"],
            conversation_history=history,
            current_bloom=state["current_bloom_level"],
        )

        # Calculate understanding estimate
        prev_estimate = state.get("understanding_estimate", 0.3)
        understanding = self.evaluator.calculate_understanding_estimate(
            evaluation, prev_estimate
        )

        return {
            "evaluation": evaluation.model_dump(),
            "understanding_estimate": understanding,
        }

    async def _classify_bloom_node(self, state: InteractionState) -> dict:
        """Node 2: Classify the Bloom level of the faculty's explanation."""
        bloom_level, should_change, reason = await self.evaluator.classify_bloom_level(
            faculty_response=state["faculty_message"],
            current_bloom=state["current_bloom_level"],
            topic=state["current_topic"],
        )

        return {
            "new_bloom_level": bloom_level if should_change else None,
            "bloom_should_change": should_change,
            "bloom_transition_reason": reason if should_change else None,
        }

    async def _check_misconceptions_node(self, state: InteractionState) -> dict:
        """Node 3: Check if any active misconceptions were corrected by this response."""
        active = state.get("active_misconceptions", [])
        correction = None

        for m in active:
            if m.get("status") == "Presented":
                result = await self.evaluator.evaluate_misconception_correction(
                    misconception_text=m["misconception_text"],
                    faculty_response=state["faculty_message"],
                )
                if result:
                    correction = result.model_dump()
                    break

        return {"misconception_correction": correction}

    async def _generate_student_node(self, state: InteractionState) -> dict:
        """Node 4: Generate the AI student's response."""
        history = [ConversationMessage(**m) for m in state["conversation_history"]]

        # Decide whether to inject a misconception
        active_count = len(state.get("active_misconceptions", []))
        should_inject = self.student.should_inject_misconception(
            persona_type=state["persona_type"],
            turn_number=state["turn_number"],
            total_misconceptions=active_count,
        )

        misconception_to_inject = None
        if should_inject:
            misconception_to_inject = self.student.select_misconception(state["subject"])

        # Generate student response
        current_bloom = state.get("new_bloom_level") or state["current_bloom_level"]
        student_msg, new_misconception = await self.student.generate_response(
            persona_type=state["persona_type"],
            subject=state["subject"],
            department=state["department"],
            faculty_message=state["faculty_message"],
            conversation_history=history,
            current_bloom=current_bloom,
            understanding_estimate=state.get("understanding_estimate", 0.3),
            inject_misconception=should_inject and misconception_to_inject is not None,
            misconception_to_inject=misconception_to_inject,
        )

        result = {"student_message": student_msg}
        if new_misconception:
            result["new_misconception"] = new_misconception.model_dump()

        return result

    async def _check_session_end_node(self, state: InteractionState) -> dict:
        """Node 5: Determine if the session should end."""
        should_end = False
        reason = None

        # Check turn limit
        if state["turn_number"] >= state["max_turns"]:
            should_end = True
            reason = "Maximum turn limit reached"

        # Check if understanding is very high (student is satisfied)
        elif state.get("understanding_estimate", 0) > 0.92 and state["turn_number"] > 8:
            should_end = True
            reason = "Student has achieved high understanding"

        return {
            "should_end_session": should_end,
            "end_session_reason": reason,
        }

    # ─── Helpers ────────────────────────────────────────────────────────

    def _get_last_student_message(self, history: list[ConversationMessage]) -> str:
        """Get the most recent student message from history."""
        for msg in reversed(history):
            if msg.role == "Student":
                return msg.content
        return ""

    def _build_response(self, state: InteractionState) -> InteractionResponse:
        """Convert final graph state into an API response."""
        evaluation = None
        if state.get("evaluation"):
            evaluation = TeachingEvaluation(**state["evaluation"])

        new_misconception = None
        if state.get("new_misconception"):
            new_misconception = NewMisconception(**state["new_misconception"])

        correction = None
        if state.get("misconception_correction"):
            correction = MisconceptionCorrection(**state["misconception_correction"])

        return InteractionResponse(
            student_message=state.get("student_message", ""),
            current_bloom_level=state.get("current_bloom_level", "Remember"),
            new_bloom_level=state.get("new_bloom_level"),
            bloom_transition_reason=state.get("bloom_transition_reason"),
            current_topic=state.get("current_topic", ""),
            evaluation=evaluation,
            new_misconception=new_misconception,
            misconception_correction=correction,
            understanding_estimate=state.get("understanding_estimate", 0.3),
            should_end_session=state.get("should_end_session", False),
            end_session_reason=state.get("end_session_reason"),
        )
