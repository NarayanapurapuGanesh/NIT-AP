import logging
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        self.client = OllamaClient()

    async def ensure_model(self, model_name: str) -> bool:
        """Check if model exists, if not try to pull it."""
        logger.info(f"Ensuring model {model_name} is available.")
        # In a full implementation, we'd query /api/tags to see if it exists first
        # For simplicity, we just trigger a pull (Ollama is idempotent for pulls)
        return await self.client.pull_model(model_name)
