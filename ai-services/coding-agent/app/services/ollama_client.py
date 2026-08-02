"""
FacultyIQ Coding Intelligence Agent — AI Orchestrator Client.

HTTP client for the centralized AI Orchestrator (Port 8010) that proxies
requests to Ollama models. Used for code explanation evaluation, viva
question generation, and complexity analysis.
"""

import time
from typing import Dict, Any, Optional

import httpx
from app.config.settings import settings
from app.core.logging import get_module_logger
from app.core.exceptions import OllamaError

log = get_module_logger("pipeline")


class OllamaClient:
    """Client for the FacultyIQ AI Orchestrator service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        agent_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = base_url or settings.ollama.orchestrator_url
        self.agent_name = agent_name or settings.ollama.agent_name
        self.timeout = timeout or settings.ollama.timeout_seconds

    async def generate(
        self,
        prompt: str,
        system: str = "",
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sends a generation request to the AI Orchestrator."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "agent_name": agent_name or self.agent_name,
            "prompt": prompt,
            "system": system,
        }

        log.info(
            "AI Orchestrator request for agent '{}'",
            payload["agent_name"],
        )
        start = time.time()

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

            elapsed = time.time() - start
            log.info("Inference completed in {:.2f}s", elapsed)
            return data

        except httpx.ConnectError:
            log.warning(
                "AI Orchestrator unavailable at {} — using fallback mode",
                self.base_url,
            )
            return self._fallback_response(prompt)

        except Exception as exc:
            log.error("AI Orchestrator call failed: {}", exc)
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Deterministic fallback when AI Orchestrator is unavailable."""
        return {
            "response": "AI evaluation unavailable. Deterministic scoring applied.",
            "model_used": "fallback-deterministic",
            "inference_time_seconds": 0.0,
            "tokens_generated": 0,
        }
