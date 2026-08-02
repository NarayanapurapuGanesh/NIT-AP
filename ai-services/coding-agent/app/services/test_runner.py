"""
FacultyIQ Coding Intelligence Agent — Test Runner.

Executes all test case categories against submitted code and produces
per-test pass/fail reports with timing information.
"""

from typing import List

from app.core.logging import get_module_logger
from app.models.sandbox import ExecutionResult, ExecutionStatus
from app.services.compilation_engine import CompilationEngine
from app.models.question import TestCaseDTO

log = get_module_logger("test_runner")


class TestVerdict:
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT = "time_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"


class TestCaseResult:
    def __init__(
        self,
        test_case: TestCaseDTO,
        verdict: str,
        actual_output: str = "",
        execution_time_ms: float = 0.0,
        error: str = "",
    ):
        self.test_case = test_case
        self.verdict = verdict
        self.actual_output = actual_output
        self.execution_time_ms = execution_time_ms
        self.error = error

    def to_dict(self) -> dict:
        return {
            "description": self.test_case.description,
            "input": self.test_case.input[:200],
            "expected_output": self.test_case.expected_output[:200],
            "actual_output": self.actual_output[:200],
            "verdict": self.verdict,
            "execution_time_ms": self.execution_time_ms,
            "is_hidden": self.test_case.is_hidden,
            "is_stress": self.test_case.is_stress,
            "is_edge_case": self.test_case.is_edge_case,
            "error": self.error[:200] if self.error else "",
        }


class TestRunSummary:
    def __init__(self, results: List[TestCaseResult]):
        self.results = results
        self.total = len(results)
        self.passed = sum(1 for r in results if r.verdict == TestVerdict.ACCEPTED)
        self.failed = self.total - self.passed
        self.pass_rate = (self.passed / self.total * 100) if self.total > 0 else 0

        # Split by category
        self.public_results = [r for r in results if not r.test_case.is_hidden]
        self.hidden_results = [r for r in results if r.test_case.is_hidden]
        self.stress_results = [r for r in results if r.test_case.is_stress]
        self.edge_results = [r for r in results if r.test_case.is_edge_case]

        self.public_passed = sum(1 for r in self.public_results if r.verdict == TestVerdict.ACCEPTED)
        self.hidden_passed = sum(1 for r in self.hidden_results if r.verdict == TestVerdict.ACCEPTED)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": round(self.pass_rate, 1),
            "public_passed": self.public_passed,
            "public_total": len(self.public_results),
            "hidden_passed": self.hidden_passed,
            "hidden_total": len(self.hidden_results),
            "results": [r.to_dict() for r in self.results],
        }


class TestRunner:
    """Runs all test cases against submitted code."""

    def __init__(self, engine: CompilationEngine | None = None):
        self.engine = engine or CompilationEngine()

    def run_all(
        self,
        source_code: str,
        language: str,
        test_cases: List[TestCaseDTO],
    ) -> TestRunSummary:
        """Executes all test cases and returns summary."""
        results = []

        for tc in test_cases:
            result = self._run_single(source_code, language, tc)
            results.append(result)

        summary = TestRunSummary(results)
        log.info(
            "Test run complete: {}/{} passed ({:.0f}%)",
            summary.passed, summary.total, summary.pass_rate,
        )
        return summary

    def run_public_only(
        self,
        source_code: str,
        language: str,
        test_cases: List[TestCaseDTO],
    ) -> TestRunSummary:
        """Runs only public (non-hidden) test cases."""
        public = [tc for tc in test_cases if not tc.is_hidden]
        return self.run_all(source_code, language, public)

    def _run_single(
        self, source_code: str, language: str, tc: TestCaseDTO
    ) -> TestCaseResult:
        """Executes a single test case."""
        timeout = max(tc.time_limit_ms // 1000, 5)

        exec_result: ExecutionResult = self.engine.compile_and_run(
            source_code=source_code,
            language=language,
            stdin=tc.input,
            timeout_seconds=timeout,
        )

        if exec_result.status == ExecutionStatus.COMPILATION_ERROR:
            return TestCaseResult(
                test_case=tc,
                verdict=TestVerdict.COMPILATION_ERROR,
                error=exec_result.compilation_error or exec_result.stderr,
                execution_time_ms=exec_result.execution_time_ms,
            )

        if exec_result.status == ExecutionStatus.TIMEOUT:
            return TestCaseResult(
                test_case=tc,
                verdict=TestVerdict.TIME_LIMIT,
                execution_time_ms=exec_result.execution_time_ms,
                error=exec_result.stderr,
            )

        if exec_result.status == ExecutionStatus.RUNTIME_ERROR:
            return TestCaseResult(
                test_case=tc,
                verdict=TestVerdict.RUNTIME_ERROR,
                actual_output=exec_result.stdout.strip(),
                error=exec_result.stderr,
                execution_time_ms=exec_result.execution_time_ms,
            )

        # Compare output
        actual = exec_result.stdout.strip()
        expected = tc.expected_output.strip()

        if self._compare_output(actual, expected):
            verdict = TestVerdict.ACCEPTED
        else:
            verdict = TestVerdict.WRONG_ANSWER

        return TestCaseResult(
            test_case=tc,
            verdict=verdict,
            actual_output=actual,
            execution_time_ms=exec_result.execution_time_ms,
        )

    def _compare_output(self, actual: str, expected: str) -> bool:
        """Flexible output comparison (ignores trailing whitespace per line)."""
        actual_lines = [line.strip() for line in actual.split("\n") if line.strip()]
        expected_lines = [line.strip() for line in expected.split("\n") if line.strip()]
        return actual_lines == expected_lines
