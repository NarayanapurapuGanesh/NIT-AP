"""
Evidence Linking Engine.
Links visual frames to spoken transcript segments based on timestamps.
"""

from typing import List, Dict, Any, Optional

def link_visual_to_transcript(
    visual_timestamp_sec: float, 
    transcript_segments: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Finds the transcript segment that was spoken at the time the visual was shown.
    Returns the segment ID (or text if no ID).
    
    transcript_segments is expected to be a list of dicts like:
    {"id": "seg_1", "start": 10.5, "end": 15.2, "text": "..."}
    """
    
    # We look for the segment whose time range overlaps or is closest to the visual timestamp.
    # Usually a slide/diagram is shown right before or while they are talking about it.
    
    closest_segment = None
    min_distance = float('inf')
    
    for segment in transcript_segments:
        start = segment.get("start", 0)
        end = segment.get("end", 0)
        
        # If the visual timestamp falls inside the segment
        if start <= visual_timestamp_sec <= end:
            return str(segment.get("id", segment.get("text", "")))
            
        # Otherwise, calculate distance
        distance = min(abs(visual_timestamp_sec - start), abs(visual_timestamp_sec - end))
        if distance < min_distance:
            min_distance = distance
            closest_segment = segment
            
    # Link if it's within 15 seconds
    if min_distance <= 15.0 and closest_segment:
        return str(closest_segment.get("id", closest_segment.get("text", "")))
        
    return None
