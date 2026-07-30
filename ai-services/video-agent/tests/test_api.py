"""Tests for Module 14: FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_200(self):
        """Health endpoint returns 200 with service info."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_health_contains_service_name(self):
        """Health endpoint includes service name."""
        response = client.get("/health")
        data = response.json()
        assert "Evidence Extraction" in data["service"]


class TestUploadEndpoint:
    """Tests for the /video/upload endpoint."""

    def test_upload_no_file(self):
        """Upload without file returns 422."""
        response = client.post("/video/upload")
        assert response.status_code == 422

    def test_upload_empty_filename(self):
        """Upload with empty content returns error."""
        response = client.post(
            "/video/upload",
            files={"file": ("", b"", "video/mp4")},
        )
        assert response.status_code in (400, 422)


class TestStatusEndpoint:
    """Tests for the /video/status/{jobId} endpoint."""

    def test_status_nonexistent_job(self):
        """Status for unknown job returns 404."""
        response = client.get("/video/status/nonexistent-job-id")
        assert response.status_code == 404

    def test_report_nonexistent_job(self):
        """Report for unknown job returns 404."""
        response = client.get("/video/report/nonexistent-job-id")
        assert response.status_code == 404


class TestSlideImageEndpoint:
    """Tests for the /video/slides/{jobId}/images/{slideId} endpoint."""

    def test_slide_image_not_found(self):
        """Slide image for nonexistent job returns 404."""
        response = client.get("/video/slides/fake-job/images/slide_001")
        assert response.status_code == 404
