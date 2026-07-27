"""
Quality & Certification Pipeline Orchestrator.
Orchestrates performance benchmarking, security validation, chaos experiments, and production certification.
"""

from typing import Any, Dict, List
from quality.schemas.quality_models import BenchmarkResult, CertificationChecklist, ProductionReadinessReport
from quality.services.quality_service import QualityServiceRegistry
from core.logging import get_logger

logger = get_logger("quality_pipeline")


class QualityPipeline:
    """Enterprise Production Certification Pipeline Facade."""

    def __init__(self) -> None:
        self.registry = QualityServiceRegistry.get_instance()

    def get_readiness_status(self) -> Dict[str, Any]:
        checklist = self.registry.certification_engine.evaluate_certification_checklist()
        return {
            "status": checklist.overall_status.value,
            "score_percent": checklist.score_percent,
            "items_passed": sum(1 for i in checklist.items if i.status == "PASSED"),
            "total_items": len(checklist.items),
            "production_ready": checklist.score_percent == 100.0,
        }

    def run_benchmark_suite(self) -> Dict[str, Any]:
        perf = self.registry.benchmarker.run_all_benchmarks()
        ai = self.registry.ai_benchmark_engine.benchmark_all_agents()
        return {
            "performance_benchmarks": perf,
            "ai_agent_benchmarks": ai,
        }

    def generate_full_certification_report(self) -> ProductionReadinessReport:
        report = self.registry.certification_engine.generate_full_report()
        report.benchmarks = self.registry.benchmarker.run_all_benchmarks()
        report.load_tests = self.registry.load_test_engine.run_load_test_suite()
        report.chaos_experiments = self.registry.chaos_engine.run_all_experiments()
        report.ai_benchmarks = self.registry.ai_benchmark_engine.benchmark_all_agents()
        return report
