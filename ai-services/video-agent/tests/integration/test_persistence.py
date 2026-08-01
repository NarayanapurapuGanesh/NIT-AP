import pytest
import os
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, VideoVisual, VisualOCR, VisualMetadata, VisualTopics, VisualTimeline
from app.db.repositories.visual_repository import VisualRepository

from sqlalchemy.pool import StaticPool

# Use an in-memory SQLite database for fast integration tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

def test_idempotent_visual_upsert(db_session):
    """Test that upserting the same visual twice updates instead of raising IntegrityError."""
    repo = VisualRepository(db_session)
    
    video_id = "test_video_123"
    filename = "test_video_123_10.0.jpg"
    
    visual_data = {"thumbnail_filename": "thumb.jpg", "timestamp_str": "00:10", "timestamp_sec": 10.0, "width": 1920, "height": 1080}
    ocr_data = {"raw_text": "Initial text", "keywords": "test", "confidence": 0.9}
    meta_data = {"visual_type": "Slide", "contains_handwriting": False, "contains_diagram": False, "contains_flowchart": False, "contains_code": False, "contains_equation": False, "contains_table": False, "rank_score": 0.5, "detection_confidence": 0.9}
    topic_data = {"primary_topic": "Testing"}
    timeline_data = {"video_id": video_id, "timeline_event_name": "Test Event", "transcript_segment_id": None}

    # First Insert
    visual1 = repo.upsert_visual(video_id, filename, visual_data, ocr_data, meta_data, topic_data, timeline_data)
    
    assert visual1 is not None
    assert visual1.id is not None
    assert visual1.ocr.raw_text == "Initial text"
    
    # Second Insert (Upsert) - simulate re-running the pipeline
    ocr_data["raw_text"] = "Updated text"
    meta_data["visual_type"] = "Whiteboard"
    
    visual2 = repo.upsert_visual(video_id, filename, visual_data, ocr_data, meta_data, topic_data, timeline_data)
    
    # Assertions
    assert visual2.id == visual1.id  # Same record
    assert visual2.ocr.raw_text == "Updated text"
    assert visual2.metadata_.visual_type == "Whiteboard"
    
    # Ensure no duplicates in DB
    count = db_session.query(VideoVisual).filter(VideoVisual.video_id == video_id, VideoVisual.filename == filename).count()
    assert count == 1
    
    ocr_count = db_session.query(VisualOCR).filter(VisualOCR.visual_id == visual1.id).count()
    assert ocr_count == 1

def test_concurrent_visual_upsert(db_session):
    """Test that concurrent processing of the same visual handles locks and upserts gracefully."""
    repo = VisualRepository(db_session)
    
    video_id = "test_video_456"
    filename = "test_video_456_20.0.jpg"
    
    visual_data = {"thumbnail_filename": "thumb.jpg", "timestamp_str": "00:20", "timestamp_sec": 20.0, "width": 1920, "height": 1080}
    ocr_data = {"raw_text": "Text", "keywords": "test", "confidence": 0.9}
    meta_data = {"visual_type": "Slide", "contains_handwriting": False, "contains_diagram": False, "contains_flowchart": False, "contains_code": False, "contains_equation": False, "contains_table": False, "rank_score": 0.5, "detection_confidence": 0.9}
    topic_data = {"primary_topic": "Testing"}
    timeline_data = {"video_id": video_id, "timeline_event_name": "Test Event", "transcript_segment_id": None}

    def run_upsert():
        repo.upsert_visual(video_id, filename, visual_data, ocr_data, meta_data, topic_data, timeline_data)

    threads = []
    for _ in range(5):
        t = threading.Thread(target=run_upsert)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()

    # Ensure only 1 record exists despite 5 threads trying to insert simultaneously
    count = db_session.query(VideoVisual).filter(VideoVisual.video_id == video_id, VideoVisual.filename == filename).count()
    assert count == 1
