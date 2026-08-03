"""
FacultyIQ Coding Intelligence Agent — Adaptive Question Generator.

Selects the next question based on candidate performance, difficulty
progression, category coverage, and Bloom taxonomy escalation.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.logging import get_module_logger
from app.models.question import QuestionDTO, QuestionFilter
from app.services.question_bank import QuestionBankService

log = get_module_logger("pipeline")

# Difficulty progression ladder
DIFFICULTY_LADDER = ["easy", "medium", "hard", "expert"]

# Bloom level escalation
BLOOM_LADDER = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

# Category rotation order for balanced coverage
CATEGORY_ROTATION = [
    "arrays", "strings", "linked_list", "stack", "queue",
    "trees", "bst", "heap", "hashmap", "graphs",
    "dfs", "bfs", "dynamic_programming", "greedy",
    "trie", "backtracking", "bit_manipulation",
]


class AdaptiveQuestionGenerator:
    """Generates progressively harder questions based on candidate performance."""

    def __init__(self, question_bank: Optional[QuestionBankService] = None):
        self.question_bank = question_bank or QuestionBankService()

    def next_question(
        self,
        db: Session,
        answered_ids: List[str],
        answered_categories: List[str],
        current_score: float,
        questions_answered: int,
        preferred_difficulty: str = "medium",
        preferred_language: str = "python",
    ) -> Optional[QuestionDTO]:
        """
        Selects the next adaptive question.

        Strategy:
        1. Determine target difficulty based on performance
        2. Pick a category the candidate hasn't been tested on yet
        3. Apply Bloom level escalation
        4. Fall back to random if specific filtering yields nothing
        """
        # 1. Determine target difficulty
        target_difficulty = self._compute_difficulty(
            current_score, questions_answered, preferred_difficulty
        )

        # 2. Pick next category (rotate through untested categories)
        target_category = self._pick_category(answered_categories)

        # 3. Determine Bloom level
        target_bloom = self._compute_bloom_level(questions_answered)

        log.info(
            "Adaptive selection: difficulty={}, category={}, bloom={}",
            target_difficulty, target_category, target_bloom,
        )

        # 4. Try to find a matching question
        filters = QuestionFilter(
            category=target_category,
            difficulty=target_difficulty,
            bloom_level=target_bloom,
            exclude_ids=answered_ids,
            is_debugging=False,
        )

        question = self.question_bank.get_random_question(db, filters)

        # Relax filters progressively if no match
        if not question:
            filters.bloom_level = None
            question = self.question_bank.get_random_question(db, filters)

        if not question:
            filters.category = None
            question = self.question_bank.get_random_question(db, filters)

        if not question:
            filters.difficulty = None
            question = self.question_bank.get_random_question(db, filters)

        if question:
            log.info(
                "Selected question: {} [{}] ({})",
                question.title, question.difficulty, question.category,
            )
        else:
            log.warning("No more questions available for this session.")

        return question

    def _compute_difficulty(
        self, score: float, answered: int, default: str
    ) -> str:
        """Fixed difficulty progression: 2 easy, 2 medium, 1 hard."""
        if answered < 2:
            return "easy"
        elif answered < 4:
            return "medium"
        else:
            return "hard"

    def _pick_category(self, answered_categories: List[str]) -> Optional[str]:
        """Picks the next untested category from the rotation."""
        for cat in CATEGORY_ROTATION:
            if cat not in answered_categories:
                return cat
        # All categories covered — allow any
        return None

    def _compute_bloom_level(self, questions_answered: int) -> Optional[str]:
        """Escalates Bloom level as the session progresses."""
        if questions_answered < 2:
            return "Apply"
        elif questions_answered < 4:
            return "Analyze"
        elif questions_answered < 7:
            return "Evaluate"
        else:
            return "Create"
