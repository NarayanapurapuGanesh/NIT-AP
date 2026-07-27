"""
End-to-End Enterprise Resume Intelligence Agent Pipeline.
Orchestrates Prompt Engine, Institutional RAG Engine, Local LLM Adapter, Pydantic JSON Validator,
Evidence Guardrails, Reasoning Confidence, and Performance Monitoring.
"""

import time
from app.resume_agent.adapters.ollama_adapter import OllamaAdapter
from app.resume_agent.confidence.agent_confidence import AgentConfidenceEngine
from app.resume_agent.evidence.evidence_engine import EvidenceEngine
from app.resume_agent.guardrails.guardrails_engine import GuardrailsEngine
from app.resume_agent.json.json_validator import JSONValidator
from app.resume_agent.monitoring.agent_monitoring import AgentMonitoringEngine
from app.resume_agent.prompts.prompt_engine import PromptEngine
from app.resume_agent.rag.policy_rag import InstitutionalKnowledgeRAG
from app.resume_agent.schemas.agent_models import AIResumeIntelligenceReport, AgentAnalysisRequest
from core.logging import get_logger

logger = get_logger("resume_agent_pipeline")


class ResumeAgentPipeline:
    """Enterprise Local AI Resume Intelligence Agent Pipeline."""

    def __init__(self) -> None:
        self.prompt_engine = PromptEngine()
        self.rag_engine = InstitutionalKnowledgeRAG()
        self.ollama_adapter = OllamaAdapter()
        self.json_validator = JSONValidator()
        self.guardrails_engine = GuardrailsEngine()
        self.evidence_engine = EvidenceEngine()
        self.confidence_engine = AgentConfidenceEngine()
        self.monitoring_engine = AgentMonitoringEngine()

    async def analyze_candidate(
        self, request: AgentAnalysisRequest
    ) -> AIResumeIntelligenceReport:
        """Executes full Local AI Resume Agent pipeline."""
        start_time = time.perf_counter()
        report = request.intelligence_report

        # Step 1: Retrieve RAG Policy Context
        policy_context = self.rag_engine.retrieve_context(request.department_name or "Computer Science")

        # Step 2: Build Prompt
        prompt_text = self.prompt_engine.build_agent_prompt(request, policy_context)

        # Step 3: Local LLM Generation via Ollama
        raw_json, token_metrics = await self.ollama_adapter.generate_reasoning(
            prompt=prompt_text,
            model_name=request.preferred_model,
            temperature=request.temperature,
        )

        # Step 4: JSON Schema Validation & Repair
        validated_reasoning = self.json_validator.validate_or_repair(raw_json)

        # Step 5: Enforce Guardrails against hallucinated claims
        guarded_reasoning = self.guardrails_engine.enforce_guardrails(validated_reasoning, report)

        # Step 6: Build Evidence Citations
        citations = self.evidence_engine.build_citations(report)

        # Step 7: Compute Reasoning Confidence
        overall_confidence = self.confidence_engine.compute_confidence(report)

        # Step 8: Telemetry Monitoring
        self.monitoring_engine.log_execution(report.document_uuid, token_metrics)

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        ai_report = AIResumeIntelligenceReport(
            document_uuid=report.document_uuid,
            candidate_name=report.candidate_name,
            reasoning=guarded_reasoning,
            citations=citations,
            overall_agent_confidence=overall_confidence,
            token_metrics=token_metrics,
            deterministic_score_summary={
                "resume_quality": report.scores.resume_quality_score,
                "research_strength": report.scores.research_strength_score,
                "teaching_strength": report.scores.teaching_strength_score,
            },
            processing_time_ms=processing_time_ms,
        )

        logger.info(
            "Resume Agent candidate analysis complete",
            candidate=report.candidate_name,
            model=token_metrics.model_name,
            confidence=overall_confidence,
            duration_ms=processing_time_ms,
        )

        return ai_report
