"""
FacultyIQ Coding Intelligence Agent — File Utilities.
"""

import json
from pathlib import Path
from typing import Any


def ensure_directory(path: Path) -> Path:
    """Creates a directory (and parents) if it doesn't exist, returns the Path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, data: Any) -> None:
    """Writes data as formatted JSON to the given file path."""
    ensure_directory(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def read_json(path: Path) -> Any:
    """Reads and returns JSON data from a file path."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
