import httpx
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def generate(self, model: str, prompt: str) -> dict:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=120.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
                raise

    async def pull_model(self, model: str):
        url = f"{self.base_url}/api/pull"
        payload = {"name": model}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=300.0)
                response.raise_for_status()
                logger.info(f"Successfully pulled model {model}")
                return True
            except Exception as e:
                logger.error(f"Failed to pull model {model}: {e}")
                return False
