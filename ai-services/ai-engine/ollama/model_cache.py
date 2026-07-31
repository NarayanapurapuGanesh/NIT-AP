import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ModelCache:
    """
    In a real implementation, this would hold model references in VRAM.
    For Ollama, it handles its own VRAM, but for Whisper/OCR, we might
    keep the PyTorch/CTranslate2 models in memory based on Performance Mode.
    """
    def __init__(self, performance_mode: bool = False):
        self.performance_mode = performance_mode
        self.cache: Dict[str, Any] = {}
        
    def get_model(self, model_id: str):
        if not self.performance_mode:
            return None
        return self.cache.get(model_id)
        
    def set_model(self, model_id: str, model_obj: Any):
        if not self.performance_mode:
            logger.info(f"Performance mode off. Not caching {model_id}.")
            return
        self.cache[model_id] = model_obj
        logger.info(f"Model {model_id} cached in memory.")
        
    def clear(self):
        self.cache.clear()
        logger.info("Model cache cleared.")
