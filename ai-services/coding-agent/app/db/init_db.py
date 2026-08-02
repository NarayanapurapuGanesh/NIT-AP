"""
FacultyIQ Coding Intelligence Agent — Database Initialization.

Creates tables and seeds question bank from JSON data files on first run.
"""

from pathlib import Path

from app.core.logging import get_module_logger
from app.db.session import engine, SessionLocal, Base
from app.db.models import QuestionORM, TestCaseORM
from app.utils.file_utils import read_json

log = get_module_logger("pipeline")


def init_database() -> None:
    """Creates all tables and seeds the question bank if empty."""
    Base.metadata.create_all(bind=engine)
    log.info("Database tables ensured.")

    db = SessionLocal()
    try:
        count = db.query(QuestionORM).count()
        if count == 0:
            log.info("Question bank is empty — seeding from JSON data files...")
            _seed_questions(db)
        else:
            log.info("Question bank already has {} questions.", count)
    finally:
        db.close()


def _seed_questions(db) -> None:
    """Loads all question JSON files and inserts them into the database."""
    data_dir = Path(__file__).resolve().parent.parent / "question_data"
    total = 0

    for json_file in sorted(data_dir.glob("*.json")):
        try:
            questions = read_json(json_file)
            if not isinstance(questions, list):
                continue

            for q_data in questions:
                q = QuestionORM(
                    id=q_data.get("id", None),
                    title=q_data["title"],
                    description=q_data["description"],
                    category=q_data["category"],
                    difficulty=q_data["difficulty"],
                    bloom_level=q_data.get("bloom_level", "Apply"),
                    tags=q_data.get("tags", []),
                    constraints=q_data.get("constraints", ""),
                    expected_time_complexity=q_data.get("expected_time_complexity", ""),
                    expected_space_complexity=q_data.get("expected_space_complexity", ""),
                    starter_code=q_data.get("starter_code", {}),
                    solution_code=q_data.get("solution_code", {}),
                    hints=q_data.get("hints", []),
                    is_debugging=q_data.get("is_debugging", False),
                    buggy_code=q_data.get("buggy_code", {}),
                    bug_description=q_data.get("bug_description", ""),
                )
                db.add(q)
                db.flush()

                for tc in q_data.get("test_cases", []):
                    db.add(TestCaseORM(
                        question_id=q.id,
                        input_data=tc["input"],
                        expected_output=tc["expected_output"],
                        is_hidden=tc.get("is_hidden", False),
                        is_stress=tc.get("is_stress", False),
                        is_edge_case=tc.get("is_edge_case", False),
                        description=tc.get("description", ""),
                        time_limit_ms=tc.get("time_limit_ms", 5000),
                    ))
                total += 1

            db.commit()
            log.info("Seeded {} questions from {}", len(questions), json_file.name)
        except Exception as exc:
            db.rollback()
            log.error("Failed to seed from {}: {}", json_file.name, exc)

    log.info("Question bank seeding complete. Total: {} questions.", total)
