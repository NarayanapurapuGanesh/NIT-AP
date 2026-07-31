"""
Generates metadata and smart names for extracted visuals.
"""

import os
from typing import Dict, Any

def generate_smart_name(job_id: str, timestamp_sec: float, topic: str = "", visual_type: str = "", raw_text: str = "") -> str:
    """
    Generates a unique deterministic image name like {jobId}_{timestamp}.jpg
    This avoids filename collisions and enables idempotent persistence.
    """
    # Provide one decimal precision to avoid floating point anomalies (e.g. 14.5.jpg)
    return f"{job_id}_{timestamp_sec:.1f}.jpg"

def rename_image(old_path: str, new_filename: str) -> str:
    """
    Renames the image file to its smart name.
    """
    directory = os.path.dirname(old_path)
    new_path = os.path.join(directory, new_filename)
    
    try:
        os.rename(old_path, new_path)
        return new_path
    except Exception:
        return old_path
