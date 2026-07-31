"""
Exports visual gallery and metadata to ZIP.
"""

import zipfile
import os
import json

def export_to_zip(visuals_data: list, output_path: str) -> str:
    """
    Generates a ZIP containing all extracted images and metadata JSON.
    """
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        metadata_list = []
        
        for visual in visuals_data:
            image_path = visual.get("image_path")
            if os.path.exists(image_path):
                filename = os.path.basename(image_path)
                zipf.write(image_path, arcname=f"images/{filename}")
                
            metadata_list.append({
                "timestamp_sec": visual.get("timestamp_sec"),
                "timestamp_str": visual.get("timestamp_str"),
                "filename": filename if os.path.exists(image_path) else None,
                "topic": visual.get("topic"),
                "diagram_type": visual.get("diagram_type"),
                "ocr": visual.get("ocr"),
                "linked_transcript_id": visual.get("linked_transcript_id")
            })
            
        # Write metadata JSON
        zipf.writestr("metadata.json", json.dumps(metadata_list, indent=2))
        
    return output_path
