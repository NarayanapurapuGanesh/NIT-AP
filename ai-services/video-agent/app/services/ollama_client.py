import httpx
import time
from loguru import logger
from typing import Dict, Any, Optional

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:8010"):
        self.base_url = base_url

    def chat(self, agent_name: str, prompt: str, system: str = "") -> Dict[str, Any]:
        """Sends a generation request to the AI Orchestrator."""
        url = f"{self.base_url}/api/generate"
        payload: Dict[str, Any] = {
            "agent_name": agent_name,
            "prompt": prompt,
            "system": system
        }
        
        logger.info(f"AI Orchestrator generation requested for agent '{agent_name}'.")
        start_time = time.time()
        
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
            inference_time = time.time() - start_time
            logger.info(f"Inference Time: {inference_time:.2f}s")
            
            return data
        except Exception as e:
            logger.error(f"AI Orchestrator generation failed: {e}")
            raise
