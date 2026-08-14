"""Ollama HTTP client for local LLM inference.
Communicates with the Ollama API to generate responses from both the
student simulation model (Llama 3.2) and the teaching evaluator model (Qwen 2.5).
"""

import httpx
import time
from loguru import logger
from config.settings import settings


class OllamaService:
    """Async HTTP client for the Ollama local LLM API."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def generate(
        self,
        prompt: str,
        model: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> dict:
        """Generate a completion from the specified Ollama model.

        Args:
            prompt: The user prompt
            model: Model name (e.g., "llama3.2:3b", "qwen2.5:3b")
            system: System prompt for role-setting
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with 'response', 'eval_count', 'total_duration' keys
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        start_time = time.time()
        logger.info(f"[OLLAMA] Generating with model={model}, temp={temperature}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

            inference_time = time.time() - start_time
            logger.info(
                f"[OLLAMA] Model={model} | Inference={inference_time:.2f}s | "
                f"Tokens={data.get('eval_count', 'N/A')}"
            )

            return {
                "response": data.get("response", ""),
                "eval_count": data.get("eval_count", 0),
                "total_duration": data.get("total_duration", 0),
                "inference_time": inference_time,
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"[OLLAMA] HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"[OLLAMA] Inference failed: {e}")
            raise

    async def generate_student_response(self, prompt: str, system: str = "") -> str:
        """Generate a student simulation response using Llama 3.2."""
        result = await self.generate(
            prompt=prompt,
            model=settings.STUDENT_MODEL,
            system=system,
            temperature=settings.STUDENT_TEMPERATURE,
            max_tokens=settings.MAX_TOKENS_STUDENT,
        )
        return result["response"]

    async def generate_evaluation(self, prompt: str, system: str = "") -> str:
        """Generate a teaching evaluation using Qwen 2.5 (structured JSON output)."""
        result = await self.generate(
            prompt=prompt,
            model=settings.EVALUATOR_MODEL,
            system=system,
            temperature=settings.EVALUATOR_TEMPERATURE,
            max_tokens=settings.MAX_TOKENS_EVALUATOR,
        )
        return result["response"]

    async def is_available(self) -> bool:
        """Check if Ollama is running and reachable."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
