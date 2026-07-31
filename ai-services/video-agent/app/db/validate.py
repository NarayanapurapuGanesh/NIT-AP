"""
Startup validation module to ensure database schema matches ORM models.
"""

from sqlalchemy import inspect, func
from sqlalchemy.orm import Session
from loguru import logger
import sys
from app.db.session import Base, engine, SessionLocal
from app.db.models import VideoVisual

def check_for_duplicates(db: Session) -> bool:
    """Checks for existing duplicate records that violate unique constraints."""
    
    duplicates = db.query(
        VideoVisual.video_id, 
        VideoVisual.filename, 
        func.count('*').label('count')
    ).group_by(
        VideoVisual.video_id, 
        VideoVisual.filename
    ).having(func.count('*') > 1).all()
    
    if duplicates:
        logger.error("Found {} duplicate (video_id, filename) pairs in VideoVisual!", len(duplicates))
        for d in duplicates:
            logger.error(f"Duplicate found: video_id={d[0]}, filename={d[1]}, count={d[2]}")
        return False
    return True

def validate_schema() -> None:
    """
    Validates that the database schema matches the SQLAlchemy ORM models.
    Raises RuntimeError if tables or columns are missing, forcing a fail-fast on startup.
    """
    logger.info("Validating database schema against ORM models...")
    
    db = SessionLocal()
    try:
        if not check_for_duplicates(db):
            logger.error("Duplicate records found. Please resolve them before starting the service.")
            sys.exit(1)
    finally:
        db.close()

    inspector = inspect(engine)
    
    # Check if database has any tables to determine if it's completely uninitialized
    existing_tables = inspector.get_table_names()
    if not existing_tables:
        logger.warning("Database has no tables! A migration must be applied.")
        raise RuntimeError("Database schema is uninitialized. Run migrations using Alembic before starting the application.")

    missing_tables = []
    schema_errors = []

    for table_name, table in Base.metadata.tables.items():
        if not inspector.has_table(table_name):
            missing_tables.append(table_name)
            continue
            
        columns_in_db = {col['name'] for col in inspector.get_columns(table_name)}
        columns_in_model = {col.name for col in table.columns}
        
        missing_columns = columns_in_model - columns_in_db
        if missing_columns:
            schema_errors.append(f"Table '{table_name}' is missing columns: {', '.join(missing_columns)}")

    if missing_tables:
        raise RuntimeError(f"Database schema is out of sync. Missing tables: {', '.join(missing_tables)}. Please run Alembic migrations.")
        
    if schema_errors:
        error_msg = "; ".join(schema_errors)
        raise RuntimeError(f"Database schema mismatch detected: {error_msg}. Please run Alembic migrations.")
        
    logger.info("Database schema validation successful.")
