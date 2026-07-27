"""
AI Provider Adapters.
Provider abstraction layer for Ollama, OpenAI, Azure OpenAI, Anthropic, Google Gemini, and Custom AI Providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.integration.schemas.integration_models import AIAdapterConfig, AIProviderType
from core.logging import get_logger

logger = get_logger("ai_adapters")


class BaseAIProviderAdapter(ABC):
    """Abstract Base Class for AI Provider Adapters."""

    def __init__(self, config: AIAdapterConfig) -> None:
        self.config = config

    @abstractmethod
    def generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        pass


class OllamaAdapter(BaseAIProviderAdapter):
    def generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        logger.info("Ollama AI adapter executing completion", model=self.config.model_name)
        return f"[Ollama response from {self.config.model_name}]: Processing prompt analysis."


class OpenAIAdapter(BaseAIProviderAdapter):
    def generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        logger.info("OpenAI AI adapter executing completion", model=self.config.model_name)
        return f"[OpenAI response from {self.config.model_name}]: Processing prompt analysis."


class AnthropicAdapter(BaseAIProviderAdapter):
    def generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        logger.info("Anthropic AI adapter executing completion", model=self.config.model_name)
        return f"[Anthropic response from {self.config.model_name}]: Processing prompt analysis."


class GeminiAdapter(BaseAIProviderAdapter):
    def generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        logger.info("Google Gemini AI adapter executing completion", model=self.config.model_name)
        return f"[Google Gemini response from {self.config.model_name}]: Processing prompt analysis."


class AIAdapterFactory:
    """Factory for creating AI Provider Adapters."""

    @staticmethod
    def create_adapter(config: AIAdapterConfig) -> BaseAIProviderAdapter:
        if config.provider_type == AIProviderType.OLLAMA:
            return OllamaAdapter(config)
        elif config.provider_type == AIProviderType.OPENAI or config.provider_type == AIProviderType.AZURE_OPENAI:
            return OpenAIAdapter(config)
        elif config.provider_type == AIProviderType.ANTHROPIC:
            return AnthropicAdapter(config)
        elif config.provider_type == AIProviderType.GOOGLE_GEMINI:
            return GeminiAdapter(config)
        else:
            return OllamaAdapter(config)
