"""
FacultyIQ Coding Intelligence Agent — Explanation Evaluator.

Evaluates candidate's textual explanation of their code solution using
AI (qwen2.5-coder:3b) via the AI Orchestrator.
"""

import re
from typing import Optional

from app.core.logging import get_module_logger
from app.services.ollama_client import OllamaClient

log = get_module_logger("explanation")


class ExplanationScore:
    def __init__(
        self,
        logic_score: float = 0.0,
        approach_score: float = 0.0,
        complexity_score: float = 0.0,
        tradeoff_score: float = 0.0,
        alternatives_score: float = 0.0,
        overall_score: float = 0.0,
        feedback: str = "",
    ):
        self.logic_score = logic_score
        self.approach_score = approach_score
        self.complexity_score = complexity_score
        self.tradeoff_score = tradeoff_score
        self.alternatives_score = alternatives_score
        self.overall_score = overall_score
        self.feedback = feedback

    def to_dict(self) -> dict:
        return {
            "logic_score": round(self.logic_score, 1),
            "approach_score": round(self.approach_score, 1),
            "complexity_score": round(self.complexity_score, 1),
            "tradeoff_score": round(self.tradeoff_score, 1),
            "alternatives_score": round(self.alternatives_score, 1),
            "overall_score": round(self.overall_score, 1),
            "feedback": self.feedback,
        }


class ExplanationEvaluator:
    """Evaluates candidate code explanations using AI."""

    def __init__(self, ollama: OllamaClient | None = None):
        self.ollama = ollama or OllamaClient()

    async def evaluate(
        self,
        source_code: str,
        explanation: str,
        question_title: str = "",
        language: str = "python",
    ) -> ExplanationScore:
        """Evaluates the explanation against the code."""
        if not explanation or len(explanation.strip()) < 10:
            return ExplanationScore(
                overall_score=0.0,
                feedback="Explanation is too short or empty.",
            )

        # Try AI evaluation
        try:
            return await self._ai_evaluate(source_code, explanation, question_title, language)
        except Exception as exc:
            log.warning("AI explanation evaluation failed: {}", exc)
            return self._deterministic_evaluate(source_code, explanation)

    async def _ai_evaluate(
        self, code: str, explanation: str, title: str, language: str,
    ) -> ExplanationScore:
        """Uses AI to evaluate the explanation."""
        prompt = f"""Evaluate this candidate's code explanation for the problem "{title}".

Code ({language}):
```
{code[:1500]}
```

Candidate's Explanation:
"{explanation[:1000]}"

Score each dimension 0-100:
1. LOGIC: Does the explanation correctly describe the logic?
2. APPROACH: Is the algorithmic approach clearly explained?
3. COMPLEXITY: Does the candidate correctly identify time/space complexity?
4. TRADEOFFS: Does the candidate discuss tradeoffs?
5. ALTERNATIVES: Does the candidate mention alternative approaches?

Respond in this EXACT format:
LOGIC: <score>
APPROACH: <score>
COMPLEXITY: <score>
TRADEOFFS: <score>
ALTERNATIVES: <score>
FEEDBACK: <one sentence feedback>"""

        result = await self.ollama.generate(
            prompt=prompt,
            system="You are a coding assessment evaluator. Score precisely 0-100.",
        )
        response = result.get("response", "")

        return self._parse_ai_response(response)

    def _parse_ai_response(self, response: str) -> ExplanationScore:
        """Parses the AI response into scores."""
        def extract(key: str) -> float:
            match = re.search(rf'{key}:\s*(\d+)', response)
            return min(float(match.group(1)), 100.0) if match else 50.0

        logic = extract("LOGIC")
        approach = extract("APPROACH")
        complexity = extract("COMPLEXITY")
        tradeoffs = extract("TRADEOFFS")
        alternatives = extract("ALTERNATIVES")

        overall = (logic * 0.3 + approach * 0.25 + complexity * 0.2 +
                   tradeoffs * 0.15 + alternatives * 0.1)

        feedback_match = re.search(r'FEEDBACK:\s*(.+)', response)
        feedback = feedback_match.group(1).strip() if feedback_match else ""

        return ExplanationScore(
            logic_score=logic,
            approach_score=approach,
            complexity_score=complexity,
            tradeoff_score=tradeoffs,
            alternatives_score=alternatives,
            overall_score=overall,
            feedback=feedback,
        )

    def _deterministic_evaluate(self, code: str, explanation: str) -> ExplanationScore:
        """Fallback deterministic evaluation when AI is unavailable."""
        word_count = len(explanation.split())
        mentions_complexity = any(
            term in explanation.lower()
            for term in ["o(n)", "o(1)", "o(log", "time complexity", "space complexity", "big-o"]
        )
        mentions_approach = any(
            term in explanation.lower()
            for term in ["approach", "algorithm", "strategy", "technique", "method"]
        )
        mentions_tradeoff = any(
            term in explanation.lower()
            for term in ["tradeoff", "trade-off", "versus", "alternatively", "instead"]
        )

        logic_score = min(word_count / 2, 70)
        approach_score = 60 if mentions_approach else 30
        complexity_score = 70 if mentions_complexity else 20
        tradeoff_score = 60 if mentions_tradeoff else 10
        alternatives_score = 20  # Hard to detect without AI

        overall = (logic_score * 0.3 + approach_score * 0.25 +
                   complexity_score * 0.2 + tradeoff_score * 0.15 +
                   alternatives_score * 0.1)

        return ExplanationScore(
            logic_score=logic_score,
            approach_score=approach_score,
            complexity_score=complexity_score,
            tradeoff_score=tradeoff_score,
            alternatives_score=alternatives_score,
            overall_score=overall,
            feedback="Evaluated using deterministic analysis (AI unavailable).",
        )
