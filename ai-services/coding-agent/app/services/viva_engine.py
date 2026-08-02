"""
FacultyIQ Coding Intelligence Agent — DSA Viva Engine.

Generates contextual follow-up questions based on the candidate's
submitted code and evaluates viva answers using AI.
"""

import re
from typing import List, Optional

from app.core.logging import get_module_logger
from app.services.ollama_client import OllamaClient

log = get_module_logger("viva")


class VivaQuestion:
    def __init__(self, question: str, category: str = "general"):
        self.question = question
        self.category = category

    def to_dict(self) -> dict:
        return {"question": self.question, "category": self.category}


class VivaAnswerScore:
    def __init__(self, score: float = 0.0, feedback: str = ""):
        self.score = score
        self.feedback = feedback

    def to_dict(self) -> dict:
        return {"score": round(self.score, 1), "feedback": self.feedback}


class VivaEngine:
    """Generates and evaluates DSA viva questions."""

    def __init__(self, ollama: OllamaClient | None = None):
        self.ollama = ollama or OllamaClient()

    async def generate_questions(
        self,
        source_code: str,
        question_title: str,
        category: str,
        difficulty: str,
        language: str = "python",
        count: int = 3,
    ) -> List[VivaQuestion]:
        """Generates contextual follow-up viva questions."""
        try:
            return await self._ai_generate(
                source_code, question_title, category, difficulty, language, count
            )
        except Exception as exc:
            log.warning("AI viva generation failed: {}. Using templates.", exc)
            return self._template_questions(category, difficulty)

    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        source_code: str = "",
    ) -> VivaAnswerScore:
        """Evaluates a viva answer using AI."""
        if not answer or len(answer.strip()) < 5:
            return VivaAnswerScore(0.0, "Answer is too short.")

        try:
            return await self._ai_evaluate(question, answer, source_code)
        except Exception as exc:
            log.warning("AI viva evaluation failed: {}", exc)
            return self._deterministic_evaluate(answer)

    async def _ai_generate(
        self, code: str, title: str, category: str,
        difficulty: str, language: str, count: int,
    ) -> List[VivaQuestion]:
        """Uses AI to generate contextual viva questions."""
        prompt = f"""The candidate solved "{title}" ({category}, {difficulty}) in {language}.

Their code:
```
{code[:1200]}
```

Generate exactly {count} follow-up viva questions that test deeper understanding.
Examples of good questions:
- "Why did you choose this approach over X?"
- "What is the time complexity and why?"
- "How would this perform with 10 million inputs?"
- "Can you solve this using a different data structure?"

Respond with one question per line, numbered 1-{count}."""

        result = await self.ollama.generate(
            prompt=prompt,
            system="You are a DSA interview expert. Generate insightful technical questions.",
        )
        response = result.get("response", "")

        questions = []
        for line in response.split("\n"):
            line = line.strip()
            # Remove numbering like "1.", "1)", "1:"
            cleaned = re.sub(r'^\d+[\.\)\:]\s*', '', line).strip()
            if cleaned and len(cleaned) > 10 and "?" in cleaned:
                questions.append(VivaQuestion(cleaned, category))

        return questions[:count] if questions else self._template_questions(category, difficulty)

    async def _ai_evaluate(self, question: str, answer: str, code: str) -> VivaAnswerScore:
        """Uses AI to evaluate a viva answer."""
        prompt = f"""Evaluate this DSA viva answer.

Question: {question}
Answer: {answer[:500]}
{f'Code context: {code[:500]}' if code else ''}

Score 0-100 based on:
- Technical accuracy
- Depth of understanding
- Clarity of explanation

Respond in this EXACT format:
SCORE: <number>
FEEDBACK: <one sentence>"""

        result = await self.ollama.generate(
            prompt=prompt,
            system="You are a technical interviewer. Score precisely.",
        )
        response = result.get("response", "")

        score_match = re.search(r'SCORE:\s*(\d+)', response)
        feedback_match = re.search(r'FEEDBACK:\s*(.+)', response)

        score = min(float(score_match.group(1)), 100.0) if score_match else 50.0
        feedback = feedback_match.group(1).strip() if feedback_match else ""

        return VivaAnswerScore(score, feedback)

    def _deterministic_evaluate(self, answer: str) -> VivaAnswerScore:
        """Fallback evaluation based on answer length and keywords."""
        word_count = len(answer.split())
        has_technical = any(
            term in answer.lower()
            for term in ["complexity", "o(n)", "algorithm", "data structure",
                         "memory", "optimize", "efficient", "recursive"]
        )
        score = min(word_count * 2, 60)
        if has_technical:
            score = min(score + 20, 85)

        return VivaAnswerScore(
            score, "Evaluated deterministically (AI unavailable)."
        )

    def _template_questions(self, category: str, difficulty: str) -> List[VivaQuestion]:
        """Returns template viva questions based on category."""
        templates = {
            "arrays": [
                "What is the time complexity of your solution and why?",
                "Could you solve this with O(1) extra space?",
                "How would your solution handle an array with 10 million elements?",
            ],
            "dynamic_programming": [
                "Why did you choose dynamic programming over a greedy approach?",
                "Can you identify the overlapping subproblems in this solution?",
                "Could you optimize the space complexity of your DP table?",
            ],
            "graphs": [
                "Why did you choose BFS instead of DFS (or vice versa)?",
                "What is the time complexity in terms of vertices and edges?",
                "How would you handle disconnected components?",
            ],
        }

        default = [
            "Explain the time and space complexity of your solution.",
            "Can you think of an alternative approach?",
            "What edge cases did you consider?",
        ]

        questions = templates.get(category, default)
        return [VivaQuestion(q, category) for q in questions]
