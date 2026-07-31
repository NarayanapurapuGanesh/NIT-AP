"""
Integration tests for the VisualRepository to ensure idempotent persistence
and correct handling of unique constraints.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.db.repositories.visual_repository import VisualRepository
from app.db.models import VideoVisual

@pytest.fixture
def db_session():
    # Use in-memory SQLite for testing repository logic without blowing up real db
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def repo(db_session):
    return VisualRepository(db_session)

def test_upsert_visual_new_record(repo: VisualRepository, db_session):
    video_id = "test_vid_001"
    filename = "test_vid_001_10.5.jpg"
    
    visual_data = {"thumbnail_filename": None, "timestamp_str": "00:10", "timestamp_sec": 10.5, "width": 1920, "height": 1080}
    ocr_data = {"raw_text": "hello", "keywords": "hello", "confidence": 0.9}
    meta_data = {"visual_type": "Slide"}
    topic_data = {"primary_topic": "General"}
    timeline_data = {"video_id": video_id, "timeline_event_name": "Test", "transcript_segment_id": None}
    
    visual = repo.upsert_visual(video_id, filename, visual_data, ocr_data, meta_data, topic_data, timeline_data)
    
    assert visual.id is not None
    assert visual.video_id == video_id
    assert visual.filename == filename
    assert visual.ocr.raw_text == "hello"

def test_upsert_visual_update_existing(repo: VisualRepository, db_session):
    video_id = "test_vid_002"
    filename = "test_vid_002_20.0.jpg"
    
    visual_data = {"thumbnail_filename": None, "timestamp_str": "00:20", "timestamp_sec": 20.0, "width": 1920, "height": 1080}
    ocr_data = {"raw_text": "initial", "keywords": "init", "confidence": 0.5}
    meta_data = {"visual_type": "Slide"}
    topic_data = {"primary_topic": "General"}
    timeline_data = {"video_id": video_id, "timeline_event_name": "Test", "transcript_segment_id": None}
    
    # First insert
    visual1 = repo.upsert_visual(video_id, filename, visual_data, ocr_data, meta_data, topic_data, timeline_data)
    initial_id = visual1.id
    
    # Now update
    ocr_data["raw_text"] = "updated"
    visual2 = repo.upsert_visual(video_id, filename, visual_data, ocr_data, meta_data, topic_data, timeline_data)
    
    assert visual2.id == initial_id
    assert visual2.ocr.raw_text == "updated"
    
    # Ensure no duplicates in DB
    count = db_session.query(VideoVisual).filter_by(video_id=video_id, filename=filename).count()
    assert count == 1
