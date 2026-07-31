"""
Builds the visual timeline.
"""

def generate_timeline_event_name(visual_type: str, topic: str, ocr_keywords: str) -> str:
    """
    Generates a concise timeline event name for the extracted visual.
    """
    if visual_type != "Slide" and visual_type != "Unknown":
        return f"{visual_type}"
    
    if topic != "General":
        return f"{topic} Discussion"
        
    keywords = ocr_keywords.split(",")
    if keywords and keywords[0]:
        return f"Topic: {keywords[0].capitalize()}"
        
    return "Visual Aid"
