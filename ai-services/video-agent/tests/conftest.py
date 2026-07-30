"""
FacultyIQ Video Evidence Extraction Service — Test Configuration.

Shared fixtures and test helpers for the pytest suite.
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """Provides a temporary workspace directory for test outputs."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


@pytest.fixture
def sample_video_path(tmp_path: Path) -> Path:
    """Creates a minimal dummy file for validation testing."""
    video_file = tmp_path / "sample_video.mp4"
    video_file.write_bytes(b"\x00" * 1024)
    return video_file


@pytest.fixture
def sample_text() -> str:
    """Sample transcript text for summary/timeline tests."""
    return (
        "Welcome to today's lecture on computer science principles and algorithms. "
        "We will cover fundamental data structures including arrays, linked lists, "
        "and binary search trees. Python is an excellent language for implementing "
        "these data structures. The merge sort algorithm has O(n log n) time complexity. "
        "Machine learning requires understanding of linear algebra and statistics. "
        "Dynamic programming breaks complex problems into simpler subproblems."
    )
