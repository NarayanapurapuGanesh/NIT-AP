"""
FacultyIQ Coding Intelligence Agent — Question Bank Service.

Loads, filters, and serves questions from the database.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.logging import get_module_logger
from app.db.models import QuestionORM, TestCaseORM
from app.models.question import QuestionDTO, TestCaseDTO, QuestionFilter

log = get_module_logger("question_bank")


class QuestionBankService:
    """Provides access to the curated DSA question repository."""

    def get_question(self, db: Session, question_id: str) -> Optional[QuestionDTO]:
        """Fetches a single question by ID."""
        q = db.query(QuestionORM).filter(QuestionORM.id == question_id).first()
        if not q:
            return None
        return self._to_dto(q, db)

    def list_questions(
        self, db: Session, filters: Optional[QuestionFilter] = None, limit: int = 50
    ) -> List[QuestionDTO]:
        """Lists questions with optional filtering."""
        query = db.query(QuestionORM)

        if filters:
            if filters.category:
                query = query.filter(QuestionORM.category == filters.category)
            if filters.difficulty:
                query = query.filter(QuestionORM.difficulty == filters.difficulty)
            if filters.bloom_level:
                query = query.filter(QuestionORM.bloom_level == filters.bloom_level)
            if filters.is_debugging is not None:
                query = query.filter(QuestionORM.is_debugging == filters.is_debugging)
            if filters.exclude_ids:
                query = query.filter(~QuestionORM.id.in_(filters.exclude_ids))

        questions = query.limit(limit).all()
        return [self._to_dto(q, db) for q in questions]

    def get_random_question(
        self, db: Session, filters: Optional[QuestionFilter] = None
    ) -> Optional[QuestionDTO]:
        """Returns a random question matching filters."""
        from sqlalchemy.sql.expression import func

        query = db.query(QuestionORM)

        if filters:
            if filters.category:
                query = query.filter(QuestionORM.category == filters.category)
            if filters.difficulty:
                query = query.filter(QuestionORM.difficulty == filters.difficulty)
            if filters.bloom_level:
                query = query.filter(QuestionORM.bloom_level == filters.bloom_level)
            if filters.is_debugging is not None:
                query = query.filter(QuestionORM.is_debugging == filters.is_debugging)
            if filters.exclude_ids:
                query = query.filter(~QuestionORM.id.in_(filters.exclude_ids))

        q = query.order_by(func.random()).first()
        if not q:
            return None
        return self._to_dto(q, db)

    def count_questions(self, db: Session, category: Optional[str] = None) -> int:
        """Returns the total number of questions, optionally filtered by category."""
        query = db.query(QuestionORM)
        if category:
            query = query.filter(QuestionORM.category == category)
        return query.count()

    def get_test_cases(
        self, db: Session, question_id: str, include_hidden: bool = False
    ) -> List[TestCaseDTO]:
        """Returns test cases for a question. Hidden tests only included when evaluating."""
        query = db.query(TestCaseORM).filter(TestCaseORM.question_id == question_id)
        if not include_hidden:
            query = query.filter(TestCaseORM.is_hidden == False)
        cases = query.all()
        return [
            TestCaseDTO(
                input=tc.input_data,
                expected_output=tc.expected_output,
                is_hidden=tc.is_hidden,
                is_stress=tc.is_stress,
                is_edge_case=tc.is_edge_case,
                description=tc.description,
                time_limit_ms=tc.time_limit_ms,
            )
            for tc in cases
        ]

    def _to_dto(self, q: QuestionORM, db: Session) -> QuestionDTO:
        """Converts ORM model to DTO, including only public test cases."""
        public_tests = self.get_test_cases(db, q.id, include_hidden=False)
        return QuestionDTO(
            id=q.id,
            title=q.title,
            description=q.description,
            category=q.category,
            difficulty=q.difficulty,
            bloom_level=q.bloom_level,
            tags=q.tags or [],
            constraints=q.constraints or "",
            expected_time_complexity=q.expected_time_complexity or "",
            expected_space_complexity=q.expected_space_complexity or "",
            starter_code=q.starter_code or {},
            hints=q.hints or [],
            public_test_cases=public_tests,
            is_debugging=q.is_debugging,
            buggy_code=q.buggy_code or {},
            bug_description="" if not q.is_debugging else (q.bug_description or ""),
        )
