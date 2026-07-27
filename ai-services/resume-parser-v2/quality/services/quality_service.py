"""
Quality Service Registry.
Singleton access to all Quality, Performance, Benchmarking, Security, and Certification engines.
"""

from typing import Optional
from quality.accessibility.accessibility_validator import AccessibilityValidationEngine
from quality.benchmark.ai_benchmark_framework import AIBenchmarkFrameworkEngine
from quality.benchmark.performance_benchmarker import PerformanceBenchmarkerEngine
from quality.certification.certification_engine import ProductionCertificationEngine
from quality.chaos.chaos_engine import ChaosEngineeringEngine
from quality.load.load_test_engine import LoadTestEngine
from quality.security.security_validator import SecurityValidationEngine
from quality.stress.stress_soak_engine import StressSoakEngine
from core.logging import get_logger

logger = get_logger("quality_service")


class QualityServiceRegistry:
    """Central Quality Service Registry Singleton."""

    _instance: Optional["QualityServiceRegistry"] = None

    def __init__(self) -> None:
        self.benchmarker = PerformanceBenchmarkerEngine()
        self.load_test_engine = LoadTestEngine()
        self.stress_soak_engine = StressSoakEngine()
        self.chaos_engine = ChaosEngineeringEngine()
        self.ai_benchmark_engine = AIBenchmarkFrameworkEngine()
        self.security_validator = SecurityValidationEngine()
        self.accessibility_validator = AccessibilityValidationEngine()
        self.certification_engine = ProductionCertificationEngine()

    @classmethod
    def get_instance(cls) -> "QualityServiceRegistry":
        if cls._instance is None:
            cls._instance = QualityServiceRegistry()
        return cls._instance
