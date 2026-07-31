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
