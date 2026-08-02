"""
FacultyIQ Coding Intelligence Agent — API Dependencies.
"""

from typing import Generator

from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """Dependency for providing a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
