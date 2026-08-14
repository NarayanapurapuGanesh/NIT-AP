"""Teaching Quality Evaluator Agent — uses Qwen 2.5 for structured evaluation.
Evaluates each faculty response across 16 teaching dimensions and classifies
the Bloom's Taxonomy level of the explanation.
"""

import json
from loguru import logger

from services.ollama_service import OllamaService
from prompts.evaluator_prompts import (
    TEACHING_EVALUATOR_SYSTEM,
    get_evaluation_prompt,
    BLOOM_CLASSIFIER_SYSTEM,
    get_bloom_classification_prompt,
    FINAL_EVALUATION_SYSTEM,
)
from models.schemas import (
    TeachingEvaluation,
    MisconceptionCorrection,
    ConversationMessage,
)


class TeachingEvaluator:
    """Evaluates teaching quality using structured AI analysis (Qwen 2.5)."""

    def __init__(self, ollama: OllamaService):
        self.ollama = ollama

    async def evaluate_turn(
        self,
        student_message: str,
        faculty_response: str,
        conversation_history: list[ConversationMessage],
        current_bloom: str,
    ) -> TeachingEvaluation:
        """Evaluate a single faculty response for teaching quality.

        Returns:
            TeachingEvaluation with all 16 dimension scores and justification.
        """
        # Build recent context
        recent = conversation_history[-4:] if conversation_history else []
        context_lines = []
        for msg in recent:
            role = "Student" if msg.role == "Student" else "Teacher"
            context_lines.append(f"{role}: {msg.content[:200]}")
        context = "\n".join(context_lines) if context_lines else "Session just started."

        prompt = get_evaluation_prompt(
            student_message, faculty_response, context, current_bloom
        )

        try:
            raw_response = await self.ollama.generate_evaluation(
                prompt, TEACHING_EVALUATOR_SYSTEM
            )
            evaluation = self._parse_evaluation(raw_response)
            logger.info(
                f"[EVALUATOR] Turn evaluated: clarity={evaluation.concept_clarity:.2f}, "
                f"accuracy={evaluation.technical_accuracy:.2f}, "
                f"engagement={evaluation.doubt_clarification:.2f}"
            )
            return evaluation
        except Exception as e:
            logger.error(f"[EVALUATOR] Evaluation failed, using defaults: {e}")
            return TeachingEvaluation(
                concept_clarity=0.5, technical_accuracy=0.5,
                logical_flow=0.5, explanation_simplicity=0.5,
                depth=0.5, example_quality=0.3, analogy_usage=0.2,
                real_world_relevance=0.3, question_handling=0.5,
                doubt_clarification=0.5, adaptive_teaching=0.5,
                grammar=0.7, fluency=0.7, vocabulary=0.6,
                professionalism=0.7, critical_thinking_encouragement=0.3,
                evidence_justification="Evaluation used default scores due to processing error.",
                confidence=0.3,
            )

    async def classify_bloom_level(
        self, faculty_response: str, current_bloom: str, topic: str
    ) -> tuple[str, bool, str]:
        """Classify the Bloom level of a faculty explanation.

        Returns:
            Tuple of (bloom_level, should_change, reason)
        """
        prompt = get_bloom_classification_prompt(faculty_response, current_bloom, topic)

        try:
            raw = await self.ollama.generate_evaluation(prompt, BLOOM_CLASSIFIER_SYSTEM)
            data = self._extract_json(raw)

            bloom_level = data.get("bloom_level", current_bloom)
            should_change = data.get("should_change", False)
            reason = data.get("reason", "")

            valid_levels = {"Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"}
            if bloom_level not in valid_levels:
                bloom_level = current_bloom
                should_change = False

            return bloom_level, should_change, reason
        except Exception as e:
            logger.warning(f"[EVALUATOR] Bloom classification failed: {e}")
            return current_bloom, False, ""

    async def evaluate_misconception_correction(
        self,
        misconception_text: str,
        faculty_response: str,
    ) -> MisconceptionCorrection | None:
        """Evaluate whether and how well the faculty corrected a misconception."""
        prompt = f"""A student expressed this misconception: "{misconception_text}"

The teacher responded: "{faculty_response}"

Did the teacher:
1. Identify the misconception?
2. Correct it accurately?
3. Explain why the student's understanding was wrong?

Return ONLY valid JSON:
{{
  "identified": true/false,
  "correction_text": "summary of the correction",
  "correction_quality": 0.0-1.0,
  "fully_corrected": true/false
}}"""

        try:
            raw = await self.ollama.generate_evaluation(
                prompt,
                "You evaluate whether a teacher correctly identified and corrected a student misconception. Return ONLY valid JSON."
            )
            data = self._extract_json(raw)

            if not data.get("identified", False):
                return None

            return MisconceptionCorrection(
                misconception_text=misconception_text,
                correction_text=data.get("correction_text", ""),
                correction_quality=max(0.0, min(1.0, data.get("correction_quality", 0.5))),
                fully_corrected=data.get("fully_corrected", False),
            )
        except Exception as e:
            logger.warning(f"[EVALUATOR] Misconception correction eval failed: {e}")
            return None

    async def generate_final_evaluation(
        self,
        conversation_history: list[ConversationMessage],
        faculty_context: str | None,
    ) -> dict:
        """Generate a comprehensive final evaluation of the entire session."""
        history_text = "\n".join(
            f"{'Student' if m.role == 'Student' else 'Teacher'} (Turn {m.turn_number}): {m.content}"
            for m in conversation_history
        )

        context_note = ""
        if faculty_context:
            context_note = f"\nFACULTY CONTEXT (from resume/prior assessments):\n{faculty_context}\n"

        prompt = f"""COMPLETE TEACHING INTERACTION TRANSCRIPT:
{history_text}
{context_note}
Generate a comprehensive final evaluation. Return ONLY valid JSON."""

        try:
            raw = await self.ollama.generate_evaluation(prompt, FINAL_EVALUATION_SYSTEM)
            return self._extract_json(raw)
        except Exception as e:
            logger.error(f"[EVALUATOR] Final evaluation failed: {e}")
            return {
                "overall_teaching_effectiveness": 0.5,
                "scores": {
                    "teaching": 0.5, "communication": 0.5, "engagement": 0.5,
                    "student_satisfaction": 0.5, "learning_gain": 0.5, "bloom_coverage": 0.3,
                },
                "strengths": ["Unable to fully evaluate due to processing error"],
                "weaknesses": ["Evaluation incomplete"],
                "recommendations": ["Re-run evaluation"],
                "confidence": 0.2,
            }

    def calculate_understanding_estimate(
        self, evaluation: TeachingEvaluation, previous_estimate: float
    ) -> float:
        """Estimate how much the student's understanding improved based on teaching quality.

        Higher teaching quality → more understanding improvement.
        """
        teaching_impact = (
            evaluation.concept_clarity * 0.25
            + evaluation.doubt_clarification * 0.25
            + evaluation.example_quality * 0.15
            + evaluation.explanation_simplicity * 0.15
            + evaluation.adaptive_teaching * 0.10
            + evaluation.logical_flow * 0.10
        )

        # Gradual improvement with diminishing returns
        improvement = teaching_impact * 0.3 * (1.0 - previous_estimate)
        new_estimate = min(1.0, previous_estimate + improvement)

        return round(new_estimate, 3)

    def _parse_evaluation(self, raw: str) -> TeachingEvaluation:
        """Parse raw LLM output into a TeachingEvaluation model."""
        data = self._extract_json(raw)

        def clamp(v, default=0.5):
            try:
                return max(0.0, min(1.0, float(v)))
            except (ValueError, TypeError):
                return default

        return TeachingEvaluation(
            concept_clarity=clamp(data.get("concept_clarity")),
            technical_accuracy=clamp(data.get("technical_accuracy")),
            logical_flow=clamp(data.get("logical_flow")),
            explanation_simplicity=clamp(data.get("explanation_simplicity")),
            depth=clamp(data.get("depth")),
            example_quality=clamp(data.get("example_quality")),
            analogy_usage=clamp(data.get("analogy_usage")),
            real_world_relevance=clamp(data.get("real_world_relevance")),
            question_handling=clamp(data.get("question_handling")),
            doubt_clarification=clamp(data.get("doubt_clarification")),
            adaptive_teaching=clamp(data.get("adaptive_teaching")),
            grammar=clamp(data.get("grammar")),
            fluency=clamp(data.get("fluency")),
            vocabulary=clamp(data.get("vocabulary")),
            professionalism=clamp(data.get("professionalism")),
            critical_thinking_encouragement=clamp(data.get("critical_thinking_encouragement")),
            evidence_justification=data.get("evidence_justification", ""),
            confidence=clamp(data.get("confidence")),
        )

    def _extract_json(self, raw: str) -> dict:
        """Extract JSON from LLM output, handling markdown code blocks."""
        text = raw.strip()

        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                cleaned = part.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    continue

        # Try finding JSON object boundaries
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        logger.warning(f"[EVALUATOR] Could not parse JSON from: {text[:200]}...")
        return {}
