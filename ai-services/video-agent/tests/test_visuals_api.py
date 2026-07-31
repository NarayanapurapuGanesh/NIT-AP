import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil
import uuid
from unittest.mock import patch
from app.main import app
from app.config.settings import settings
from app.db.session import SessionLocal
from app.db.models import VideoVisual

client = TestClient(app)

@pytest.fixture
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def mock_job_dir():
    job_id = str(uuid.uuid4())
    job_dir = settings.base_dir / settings.storage.output_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    visuals_dir = job_dir / "visuals"
    visuals_dir.mkdir(parents=True, exist_ok=True)
    yield job_id, job_dir
    # Cleanup
    shutil.rmtree(job_dir, ignore_errors=True)

def test_missing_folder_404():
    job_id = str(uuid.uuid4())
    response = client.get(f"/video/{job_id}/visuals")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job directory not found"

def test_invalid_jobid_400():
    response = client.get("/video/invalid@@jobid/visuals")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Job ID format"

def test_empty_gallery(mock_job_dir):
    job_id, _ = mock_job_dir
    response = client.get(f"/video/{job_id}/visuals")
    assert response.status_code == 200
    assert response.json() == []

def test_gallery_auto_rebuild(mock_job_dir, test_db):
    job_id, job_dir = mock_job_dir
    
    # Create mock images on disk without adding them to DB
    visuals_dir = job_dir / "visuals"
    (visuals_dir / "image1.jpg").touch()
    (visuals_dir / "thumb_image1.jpg").touch()
    
    # Ensure DB is empty
    count = test_db.query(VideoVisual).filter(VideoVisual.video_id == job_id).count()
    assert count == 0
    
    response = client.get(f"/video/{job_id}/visuals")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "image1.jpg"
    assert data[0]["thumbnail_filename"] == "thumb_image1.jpg"
    
    # Ensure DB was populated
    count = test_db.query(VideoVisual).filter(VideoVisual.video_id == job_id).count()
    assert count == 1
    
    # Cleanup DB
    test_db.query(VideoVisual).filter(VideoVisual.video_id == job_id).delete()
    test_db.commit()
    
def test_debug_endpoint(mock_job_dir):
    job_id, job_dir = mock_job_dir
    visuals_dir = job_dir / "visuals"
    (visuals_dir / "test.jpg").touch()
    
    response = client.get(f"/video/{job_id}/visuals/debug")
    assert response.status_code == 200
    data = response.json()
    assert data["jobId"] == job_id
    assert data["folderExists"] is True
    assert data["imageCount"] == 1
    assert "test.jpg" in data["images"]

def test_server_error_500_returns_json(mock_job_dir):
    job_id, job_dir = mock_job_dir
    (job_dir / "visuals" / "test.jpg").touch()
    
    with patch("app.visual_extractor.gallery_service.rebuild_gallery_from_disk") as mock_rebuild:
        mock_rebuild.side_effect = Exception("Mocked catastrophic failure")
        response = client.get(f"/video/{job_id}/visuals")
        assert response.status_code == 500
        assert "Mocked catastrophic failure" in response.json()["detail"]
        assert "application/json" in response.headers.get("content-type", "")
