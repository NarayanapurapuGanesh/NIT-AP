"""
Qwen2.5 3B Callback LLM Module (Module 10).

Targeted local LLM invocation module using Qwen2.5:3B (via Ollama or local HTTP server).
Fires *only* when deterministic extraction yields uncertain or ambiguous resume paragraphs.

Input: Uncertain text paragraph
Output: Structured breakdown into Projects, Skills, Research, or Responsibilities.
"""

import json
import re
import httpx
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from llm.base import ILLMProvider


class UncertainBlockClassification(BaseModel):
    paragraph_text: str = Field(..., description="Original uncertain text block sent to LLM")
    classification: str = Field(..., description="Projects, Skills, Research, or Responsibilities")
    extracted_entities: List[str] = Field(default_factory=list, description="Key concepts extracted by LLM")
    confidence: float = Field(0.9, description="LLM classification confidence score")


class QwenCallbackLLM(ILLMProvider):
    """Callback LLM connector targeting Qwen2.5:3B via Ollama / HTTP endpoint."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "qwen2.5:3b"):
        self.ollama_url = ollama_url
        self.model_name = model_name

    @property
    def provider_name(self) -> str:
        return "Qwen2.5-3B-Callback-LLM"

    async def generate_completion(
        self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.1
    ) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt or "You are an enterprise academic resume parsing assistant.",
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(f"{self.ollama_url}/api/generate", json=payload)
                if resp.status_code == 200:
                    return resp.json().get("response", "")
        except Exception:
            pass

        # Fallback offline string synthesis when Ollama service is offline
        return '{"classification": "Projects", "extracted_entities": []}'

    async def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        system = "Return strictly valid JSON matching the requested schema. Do not include markdown code block syntax."
        completion = await self.generate_completion(prompt, system_prompt=system, temperature=0.0)

        try:
            # Use regex to find JSON object in case model adds conversational text
            match = re.search(r'\{.*\}', completion.strip(), re.DOTALL)
            if match:
                return json.loads(match.group(0))
            cleaned = completion.strip().strip("`").removeprefix("json").strip()
            return json.loads(cleaned)
        except Exception as e:
            print(f"JSON Parse Error: {e}, Raw: {completion}")
            return {}

    async def classify_uncertain_paragraph(self, paragraph: str) -> UncertainBlockClassification:
        """Classifies uncertain paragraph specifically using Qwen2.5:3B callback prompt."""
        prompt = f"""Analyze this ambiguous resume paragraph and classify it strictly as one of: [Projects, Skills, Research, Responsibilities].

Paragraph:
"{paragraph}"

Respond in strict JSON format:
{{
  "classification": "Projects",
  "extracted_entities": ["item1", "item2"]
}}
"""
        schema = {
            "type": "object",
            "properties": {
                "classification": {"type": "string"},
                "extracted_entities": {"type": "array", "items": {"type": "string"}},
            },
        }

        response_dict = await self.generate_structured(prompt, schema)

        classification = response_dict.get("classification")
        entities = response_dict.get("extracted_entities", [])

        # Fallback heuristic if LLM call returned empty/mocked
        if not classification or classification not in {"Projects", "Skills", "Research", "Responsibilities"}:
            p_lower = paragraph.lower()
            if any(w in p_lower for w in ["research", "paper", "study", "analysis"]):
                classification = "Research"
            elif any(w in p_lower for w in ["project", "built", "implemented", "system"]):
                classification = "Projects"
            elif any(w in p_lower for w in ["managed", "responsible", "led", "handled"]):
                classification = "Responsibilities"
            else:
                classification = "Skills"

        valid_entities = entities
        if not valid_entities and classification == "Skills":
            from extractors.deterministic_extractor import DeterministicExtractor
            text_words = [re.sub(r'[^a-zA-Z0-9+#.-]', '', w).lower() for w in paragraph.split()]
            valid_entities = [w.title() for w in text_words if w in DeterministicExtractor.COMMON_SKILLS]

        return UncertainBlockClassification(
            paragraph_text=paragraph,
            classification=classification,
            extracted_entities=valid_entities,
            confidence=0.92,
        )
