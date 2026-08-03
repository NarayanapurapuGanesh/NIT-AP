import os
import time
import subprocess
import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status
from loguru import logger

from services.model_service import AIModelService

app = FastAPI(title="FacultyIQ AI Orchestrator", description="Centralized AI Model Management Service")

# Path to the config file at root workspace
CONFIG_PATH = os.environ.get("AI_MODELS_CONFIG", "../../config/ai-models.yaml")
model_service = AIModelService(CONFIG_PATH)

class GenerateRequest(BaseModel):
    agent_name: str
    prompt: str
    system: Optional[str] = ""

class GenerateResponse(BaseModel):
    response: str
    model_used: str
    inference_time_seconds: float
    tokens_generated: Optional[int] = None

def _log_gpu_stats():
    """Logs GPU usage if nvidia-smi is available."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(', ')
            if len(parts) >= 3:
                logger.info(f"GPU Used: {parts[0]}%")
                logger.info(f"VRAM Used: {parts[1]}MB / {parts[2]}MB")
    except Exception as e:
        logger.warning(f"Could not fetch GPU stats (is nvidia-smi installed?): {e}")

@app.on_event("startup")
async def startup_event():
    try:
        model_service.loadConfiguration()
        model_service.validate_all_startup_models()
    except Exception as e:
        logger.error(f"Failed to initialize AI Orchestrator: {e}")
        # Normally we might raise here, but let's allow it to start up so errors are visible via API if we want

@app.post("/api/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    model = model_service.getModel(req.agent_name)
    
    # Just in case, validate it still exists (optional but safe)
    # final_model = model_service.validateModelExists(model)
    final_model = model
    
    url = "http://localhost:11434/api/generate"
    payload: Dict[str, Any] = {
        "model": final_model,
        "prompt": req.prompt,
        "stream": False
    }
    if req.system:
        payload["system"] = req.system
        
    _log_gpu_stats()
    
    logger.info(f"[{req.agent_name.upper()} AGENT] Generation requested for model '{final_model}'.")
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
        inference_time = time.time() - start_time
        logger.info(f"[{req.agent_name.upper()} AGENT] Inference Time: {inference_time:.2f}s")
        
        return GenerateResponse(
            response=data.get("response", ""),
            model_used=final_model,
            inference_time_seconds=inference_time,
            tokens_generated=data.get("eval_count")
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama API returned an error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Ollama error: {e.response.text}")
    except Exception as e:
        logger.error(f"Ollama generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to connect to Ollama: {str(e)}")

@app.post("/api/reload")
async def reload_config():
    model_service.reloadConfiguration()
    return {"status": "success", "message": "Configuration reloaded."}

class DossierPayload(BaseModel):
    candidate_name: str
    session_id: str
    report: Dict[str, Any]

@app.post("/api/dossier/coding")
async def receive_coding_dossier(payload: DossierPayload):
    """Receive the final evidence report from the Coding Agent."""
    logger.info(f"[DOSSIER] Received coding report for candidate {payload.candidate_name} (Session: {payload.session_id})")
    
    # In a full implementation, this would save to a shared database or trigger the Decision Agent.
    # For now, we will save it to a local JSON file for the Decision Agent to pick up later.
    try:
        import json
        import os
        
        # Ensure the dossiers directory exists
        dossier_dir = os.path.join(os.path.dirname(__file__), "dossiers")
        os.makedirs(dossier_dir, exist_ok=True)
        
        file_path = os.path.join(dossier_dir, f"{payload.session_id}_coding.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload.dict(), f, indent=4)
            
        logger.info(f"[DOSSIER] Saved coding report to {file_path}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"[DOSSIER] Failed to save coding report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class DecisionResponse(BaseModel):
    session_id: str
    decision_report: str
    model_used: str

@app.post("/api/dossier/evaluate/{session_id}", response_model=DecisionResponse)
async def evaluate_candidate(session_id: str):
    """Evaluate candidate across all available dossiers (Coding, Video, Resume)."""
    import json
    import glob
    import os
    
    dossier_dir = os.path.join(os.path.dirname(__file__), "dossiers")
    if not os.path.exists(dossier_dir):
        raise HTTPException(status_code=404, detail="No dossiers found.")
        
    pattern = os.path.join(dossier_dir, f"{session_id}_*.json")
    files = glob.glob(pattern)
    
    # Filter out decision file itself if it exists
    files = [f for f in files if not f.endswith("_decision.json")]
    
    if not files:
        raise HTTPException(status_code=404, detail=f"No dossiers found for session {session_id}")
        
    compiled_evidence = {}
    for f_path in files:
        with open(f_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # The filename is something like sessionID_coding.json
            name_part = os.path.basename(f_path).replace(f"{session_id}_", "").replace(".json", "")
            compiled_evidence[name_part] = data
            
    # Prepare the prompt for the decision agent
    system_prompt = (
        "You are the Final Decision Agent for FacultyIQ. You evaluate candidate evidence across multiple modalities "
        "including coding assessments, video analysis, and resume parsing. Provide a final 'Hire' or 'No Hire' recommendation, "
        "along with a detailed summary of strengths, weaknesses, and reasoning based strictly on the provided JSON data."
    )
    user_prompt = f"Candidate Evidence (JSON format):\n\n{json.dumps(compiled_evidence, indent=2)}\n\nPlease provide your final recommendation."
    
    # Fetch the correct model for decision
    model = model_service.getModel("decision")
    
    # Generate the response
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False
    }
    
    logger.info(f"[DECISION AGENT] Generating final evaluation for session {session_id} using {model}...")
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
        decision_text = data.get("response", "")
        
        # Save the final decision
        decision_path = os.path.join(dossier_dir, f"{session_id}_decision.json")
        final_doc = {
            "session_id": session_id,
            "decision": decision_text,
            "evidence_used": list(compiled_evidence.keys()),
            "model": model
        }
        with open(decision_path, "w", encoding="utf-8") as f:
            json.dump(final_doc, f, indent=4)
            
        return DecisionResponse(
            session_id=session_id,
            decision_report=decision_text,
            model_used=model
        )
    except Exception as e:
        logger.error(f"[DECISION AGENT] Failed to generate decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))
