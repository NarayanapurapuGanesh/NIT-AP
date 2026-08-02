"""
FacultyIQ Coding Intelligence Agent — Complexity Analyzer.

Estimates time and space complexity through static analysis
(loop depth, recursion detection) and optional AI-assisted analysis.
"""

import re
from typing import Optional

from app.core.logging import get_module_logger
from app.services.ollama_client import OllamaClient

log = get_module_logger("complexity")


class ComplexityResult:
    def __init__(
        self,
        estimated_time: str = "O(?)",
        estimated_space: str = "O(?)",
        confidence: float = 0.0,
        analysis_details: str = "",
        matches_expected: bool = False,
    ):
        self.estimated_time = estimated_time
        self.estimated_space = estimated_space
        self.confidence = confidence
        self.analysis_details = analysis_details
        self.matches_expected = matches_expected

    def to_dict(self) -> dict:
        return {
            "estimated_time_complexity": self.estimated_time,
            "estimated_space_complexity": self.estimated_space,
            "confidence": round(self.confidence, 2),
            "analysis_details": self.analysis_details,
            "matches_expected": self.matches_expected,
        }


class ComplexityAnalyzer:
    """Estimates algorithmic complexity through static + AI analysis."""

    def __init__(self, ollama: OllamaClient | None = None):
        self.ollama = ollama or OllamaClient()

    def analyze(
        self,
        source_code: str,
        language: str = "python",
        expected_time: str = "",
        expected_space: str = "",
    ) -> ComplexityResult:
        """Analyzes code complexity using heuristic static analysis."""
        # Static analysis
        loop_depth = self._count_loop_depth(source_code, language)
        has_recursion = self._detect_recursion(source_code, language)
        has_sorting = self._detect_sorting(source_code, language)
        has_hashmap = self._detect_hashmap(source_code, language)

        # Estimate time complexity from heuristics
        time_est, time_conf = self._estimate_time(
            loop_depth, has_recursion, has_sorting, has_hashmap
        )
        space_est, space_conf = self._estimate_space(
            has_recursion, has_hashmap, source_code
        )

        confidence = (time_conf + space_conf) / 2

        # Check against expected
        matches = False
        if expected_time:
            matches = self._normalize_complexity(time_est) == self._normalize_complexity(expected_time)

        details = (
            f"Loop depth: {loop_depth}, "
            f"Recursion: {has_recursion}, "
            f"Sorting: {has_sorting}, "
            f"HashMap: {has_hashmap}"
        )

        log.info(
            "Complexity analysis: time={}, space={}, confidence={:.0f}%",
            time_est, space_est, confidence * 100,
        )

        return ComplexityResult(
            estimated_time=time_est,
            estimated_space=space_est,
            confidence=confidence,
            analysis_details=details,
            matches_expected=matches,
        )

    async def analyze_with_ai(
        self,
        source_code: str,
        language: str = "python",
        expected_time: str = "",
        expected_space: str = "",
    ) -> ComplexityResult:
        """Enhanced analysis using AI for complex cases."""
        # Start with static analysis
        static_result = self.analyze(source_code, language, expected_time, expected_space)

        # If confidence is low, consult AI
        if static_result.confidence < 0.5:
            try:
                prompt = (
                    f"Analyze the time and space complexity of this {language} code. "
                    f"Respond ONLY with two lines:\n"
                    f"TIME: O(...)\nSPACE: O(...)\n\n"
                    f"Code:\n```\n{source_code[:2000]}\n```"
                )
                ai_result = await self.ollama.generate(
                    prompt=prompt,
                    system="You are an algorithm complexity analysis expert. Be precise and concise.",
                )
                response = ai_result.get("response", "")
                time_match = re.search(r'TIME:\s*(O\([^)]+\))', response)
                space_match = re.search(r'SPACE:\s*(O\([^)]+\))', response)

                if time_match:
                    static_result.estimated_time = time_match.group(1)
                    static_result.confidence = min(static_result.confidence + 0.3, 1.0)
                if space_match:
                    static_result.estimated_space = space_match.group(1)

                if expected_time:
                    static_result.matches_expected = (
                        self._normalize_complexity(static_result.estimated_time)
                        == self._normalize_complexity(expected_time)
                    )

            except Exception as exc:
                log.warning("AI complexity analysis failed: {}", exc)

        return static_result

    def _count_loop_depth(self, code: str, language: str) -> int:
        """Counts maximum nesting depth of loops."""
        max_depth = 0
        current_depth = 0

        if language == "python":
            for line in code.split("\n"):
                stripped = line.strip()
                if stripped.startswith(("for ", "while ")):
                    indent = len(line) - len(line.lstrip())
                    depth = indent // 4 + 1
                    current_depth = depth
                    max_depth = max(max_depth, current_depth)
        else:
            for char in code:
                if char == '{':
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)
                elif char == '}':
                    current_depth = max(0, current_depth - 1)
            # Count for/while occurrences as approximation
            loop_count = len(re.findall(r'\b(for|while)\b', code))
            max_depth = min(max_depth, loop_count)

        return max_depth

    def _detect_recursion(self, code: str, language: str) -> bool:
        """Detects if code contains recursive function calls."""
        if language == "python":
            funcs = re.findall(r'def\s+(\w+)\s*\(', code)
            for func in funcs:
                pattern = rf'\b{func}\s*\('
                count = len(re.findall(pattern, code))
                if count >= 2:
                    return True
        else:
            funcs = re.findall(r'\b(\w+)\s*\([^)]*\)\s*\{', code)
            for func in funcs:
                pattern = rf'\b{func}\s*\('
                count = len(re.findall(pattern, code))
                if count >= 2:
                    return True
        return False

    def _detect_sorting(self, code: str, language: str) -> bool:
        """Detects usage of sorting functions."""
        patterns = [
            r'\.sort\(', r'sorted\(', r'Arrays\.sort',
            r'std::sort', r'Collections\.sort', r'\.Sort\(',
        ]
        return any(re.search(p, code) for p in patterns)

    def _detect_hashmap(self, code: str, language: str) -> bool:
        """Detects usage of hash maps / dictionaries."""
        patterns = [
            r'\bdict\b', r'\bset\b', r'\bdefaultdict\b', r'\bCounter\b',
            r'HashMap', r'HashSet', r'unordered_map', r'unordered_set',
            r'Map\(', r'Set\(', r'Dictionary',
        ]
        return any(re.search(p, code) for p in patterns)

    def _estimate_time(
        self, loop_depth: int, has_recursion: bool,
        has_sorting: bool, has_hashmap: bool,
    ) -> tuple[str, float]:
        """Estimates time complexity from heuristics."""
        if has_sorting:
            if loop_depth >= 2:
                return "O(n^2 log n)", 0.4
            return "O(n log n)", 0.7

        if loop_depth == 0:
            if has_recursion:
                return "O(2^n)", 0.3  # Uncertain for recursion
            return "O(n)", 0.6

        if loop_depth == 1:
            return "O(n)", 0.7
        elif loop_depth == 2:
            return "O(n^2)", 0.7
        elif loop_depth == 3:
            return "O(n^3)", 0.6
        else:
            return f"O(n^{loop_depth})", 0.4

    def _estimate_space(
        self, has_recursion: bool, has_hashmap: bool, code: str,
    ) -> tuple[str, float]:
        """Estimates space complexity from heuristics."""
        if has_hashmap or "dp" in code.lower():
            return "O(n)", 0.6
        if has_recursion:
            return "O(n)", 0.5  # Stack space
        if re.search(r'\[\s*\[', code):
            return "O(n^2)", 0.5  # 2D array
        return "O(1)", 0.5

    def _normalize_complexity(self, s: str) -> str:
        """Normalizes complexity strings for comparison."""
        return re.sub(r'\s+', '', s.lower().replace('*', ''))
