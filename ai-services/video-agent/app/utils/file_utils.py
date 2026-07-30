"""
FacultyIQ Video Evidence Extraction Service — File Utilities.

Common file-system helpers used across all modules.
"""

import json
from pathlib import Path
from typing import Any, Union


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensures directory exists, creating parent directories if needed."""
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(path: Union[str, Path], data: Any) -> Path:
    """Writes a Pydantic model or dict to a JSON file."""
    p = Path(path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        if hasattr(data, "model_dump_json"):
            f.write(data.model_dump_json(indent=2, by_alias=True))
        else:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return p


def write_text(path: Union[str, Path], content: str) -> Path:
    """Writes text content to a file."""
    p = Path(path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


def format_timestamp(seconds: float) -> str:
    """Converts seconds to HH:MM:SS format."""
    total = int(seconds)
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
