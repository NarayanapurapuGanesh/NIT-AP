from pathlib import Path
from typing import Union


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensures directory exists, creating parent directories if needed."""
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p
