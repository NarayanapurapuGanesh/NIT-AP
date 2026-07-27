"""
End-to-End Enterprise AI Recruitment Decision Pipeline.
Orchestrates Coordinator Agent, 9 Specialist Agents, Institutional RAG Engine, Ollama Adapter,
Anti-Hallucination Guardrails, Evidence Provenance, Decision Confidence, and Telemetry Monitoring.
"""

import time
from app.recruitment_agent.adapters.recruitment_ollama import RecruitmentOllamaAdapter
from app.recruitment_agent.confidence.decision_confidence import DecisionConfidenceEngine
from app.recruitment_agent.evidence.decision_evidence import DecisionEvidenceEngine
from app.recruitment_agent.guardrails.decision_guardrails import DecisionGuardrailsEngine
from app.recruitment_agent.json.decision_json_validator import DecisionJSONValidator
from app.recruitment_agent.monitoring.decision_monitoring import DecisionMonitoringEngine
from app.recruitment_agent.orchestrator.coordinator import CoordinatorAgent
from app.recruitment_agent.prompt_engine.decision_prompts import DecisionPromptEngine
from app.recruitment_agent.rag.recruitment_rag import InstitutionalRecruitmentRAG
from app.recruitment_agent.schemas.decision_models import (
    DecisionRequest,
    InterviewFocusArea,
    RecruitmentDecisionReport,
    RiskAssessment,
)
from core.logging import get_logger

logger = get_logger("recruitment_decision_pipeline")


class RecruitmentDecisionPipeline:
    """Enterprise AI Recruitment Decision Pipeline Engine."""

    def __init__(self) -> None:
        self.coordinator = CoordinatorAgent()
        self.prompt_engine = DecisionPromptEngine()
        self.rag_engine = InstitutionalRecruitmentRAG()
        self.ollama_adapter = RecruitmentOllamaAdapter()
        self.json_validator = DecisionJSONValidator()
        self.guardrails_engine = DecisionGuardrailsEngine()
        self.evidence_engine = DecisionEvidenceEngine()
        self.confidence_engine = DecisionConfidenceEngine()
        self.monitoring_engine = DecisionMonitoringEngine()

    async def evaluate_candidate_decision(
        self, request: DecisionRequest
    ) -> RecruitmentDecisionReport:
        """Executes full multi-agent AI recruitment decision pipeline."""
        start_time = time.perf_counter()
        match = request.match_report

        # Step 1: Specialist Multi-Agent Evaluation & Consensus
        raw_recommendation, specialist_opinions = self.coordinator.orchestrate_agents(match)

        # Step 2: Enforce Strict Guardrails
        final_recommendation = self.guardrails_engine.enforce_guardrails(raw_recommendation, match)

        # Step 3: RAG Guidelines Retrieval
        rag_policies = self.rag_engine.retrieve_guidelines(request.department_name or "Computer Science")

        # Step 4: Prompt Construction & LLM Reasoning
        prompt = self.prompt_engine.build_decision_prompt(match, rag_policies)
        raw_json = await self.ollama_adapter.generate_decision(prompt, request.preferred_model)
        parsed_json = self.json_validator.validate_or_repair(raw_json)

        # Step 5: Evidence & Confidence Engine
        evidence_lines = self.evidence_engine.build_evidence_lines(match)
        overall_confidence = self.confidence_engine.compute_decision_confidence(match)

        # Step 6: Telemetry Monitoring
        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        self.monitoring_engine.log_decision_metrics(match.candidate_name, final_recommendation, processing_time_ms)

        risk_level = "High" if len(match.critical_gaps) > 0 else "Low"
        risk_obj = RiskAssessment(
            risk_level=risk_level,
            risk_factors=match.critical_gaps or ["No critical risks identified."],
            mitigation_strategies=["Verify credentials during in-person panel interview."] if match.critical_gaps else [],
        )

        interview_topics = parsed_json.get("interview_topics", ["Core Research Vision", "Teaching Pedagogy"])
        interview_focus = [
            InterviewFocusArea(category="Technical & Research", focus_topics=interview_topics)
        ]

        report = RecruitmentDecisionReport(
            document_uuid=match.document_uuid,
            job_uuid=match.job_uuid,
            candidate_name=match.candidate_name,
            position_title=match.position_title,
            recommendation=final_recommendation,
            overall_confidence=overall_confidence,
            summary=parsed_json.get("summary", "Candidate meets requirements for hiring consideration."),
            strengths=match.strengths,
            weaknesses=match.weaknesses,
            risks=risk_obj,
            interview_focus=interview_focus,
            specialist_opinions=specialist_opinions,
            evidence=evidence_lines,
            processing_time_ms=processing_time_ms,
        )

        logger.info(
            "Recruitment decision pipeline complete",
            candidate=match.candidate_name,
            recommendation=final_recommendation,
            confidence=overall_confidence,
            duration_ms=processing_time_ms,
        )

        return report
