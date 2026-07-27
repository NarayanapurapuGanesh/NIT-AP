"""
Local LLM Connector Base Interface for Ollama / Future Inference Runtimes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ILLMProvider(ABC):
    """Abstract interface for offline LLM prompts and inference generation."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def generate_completion(
        self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.1
    ) -> str:
        """Generates completion text from target LLM backend."""
        pass

    @abstractmethod
    async def generate_structured(
        self, prompt: str, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates JSON payload validated against target schema."""
        pass
