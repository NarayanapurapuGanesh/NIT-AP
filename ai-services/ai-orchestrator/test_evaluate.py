import sys
import os
import asyncio
from fastapi.testclient import TestClient

# Add current dir to sys.path so we can import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, evaluate_candidate
import json

client = TestClient(app)

def test_evaluate():
    session_id = "test_session_123"
    dossier_dir = os.path.join(os.path.dirname(__file__), "dossiers")
    os.makedirs(dossier_dir, exist_ok=True)
    
    # Create mock dossiers
    coding_data = {
        "candidate_name": "John Doe",
        "session_id": session_id,
        "report": {
            "overall_score": 85,
            "test_cases_passed": "18/20",
            "time_complexity": "O(N)",
            "summary": "Candidate solved problems efficiently but missed an edge case."
        }
    }
    
    video_data = {
        "candidate_name": "John Doe",
        "session_id": session_id,
        "report": {
            "presentation_score": 90,
            "confidence": "High",
            "summary": "Candidate spoke clearly and made good eye contact."
        }
    }
    
    with open(os.path.join(dossier_dir, f"{session_id}_coding.json"), "w") as f:
        json.dump(coding_data, f)
        
    with open(os.path.join(dossier_dir, f"{session_id}_video.json"), "w") as f:
        json.dump(video_data, f)
        
    print(f"Created mock dossiers for {session_id}")
    
    print(f"Calling endpoint /api/dossier/evaluate/{session_id}...")
    
    try:
        with TestClient(app) as client:
            response = client.post(f"/api/dossier/evaluate/{session_id}")
            
            print("Status Code:", response.status_code)
            if response.status_code == 200:
                print("Response:", json.dumps(response.json(), indent=2))
            else:
                print("Error Response:", response.text)
    except Exception as e:
        print("Failed to run endpoint:", e)
        
if __name__ == "__main__":
    test_evaluate()
