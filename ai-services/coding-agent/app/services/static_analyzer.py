"""
FacultyIQ Coding Intelligence Agent — Static Code Analyzer.

Evaluates code quality: naming, readability, modularity, cyclomatic complexity,
dead code, magic numbers, comments, security issues, and language best practices.
"""

import re
from typing import List

from app.core.logging import get_module_logger

log = get_module_logger("static_analysis")


class CodeSmell:
    def __init__(self, category: str, message: str, severity: str = "info", line: int = 0):
        self.category = category
        self.message = message
        self.severity = severity  # info | warning | error
        self.line = line

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "message": self.message,
            "severity": self.severity,
            "line": self.line,
        }


class StaticAnalysisResult:
    def __init__(self):
        self.smells: List[CodeSmell] = []
        self.metrics: dict = {}
        self.maintainability_score: float = 100.0

    def add_smell(self, smell: CodeSmell):
        self.smells.append(smell)
        # Deduct from maintainability
        if smell.severity == "error":
            self.maintainability_score = max(0, self.maintainability_score - 10)
        elif smell.severity == "warning":
            self.maintainability_score = max(0, self.maintainability_score - 5)
        else:
            self.maintainability_score = max(0, self.maintainability_score - 2)

    def to_dict(self) -> dict:
        return {
            "maintainability_score": round(self.maintainability_score, 1),
            "total_issues": len(self.smells),
            "errors": sum(1 for s in self.smells if s.severity == "error"),
            "warnings": sum(1 for s in self.smells if s.severity == "warning"),
            "info": sum(1 for s in self.smells if s.severity == "info"),
            "metrics": self.metrics,
            "issues": [s.to_dict() for s in self.smells[:20]],  # Cap at 20
        }


class StaticAnalyzer:
    """Evaluates code quality and maintainability."""

    def analyze(self, source_code: str, language: str = "python") -> StaticAnalysisResult:
        """Runs all static analysis checks on the source code."""
        result = StaticAnalysisResult()
        lines = source_code.split("\n")

        # Basic metrics
        result.metrics = {
            "total_lines": len(lines),
            "code_lines": sum(1 for l in lines if l.strip() and not l.strip().startswith("#")),
            "blank_lines": sum(1 for l in lines if not l.strip()),
            "comment_lines": sum(1 for l in lines if l.strip().startswith("#")),
        }

        # Run checks
        self._check_naming(source_code, language, result)
        self._check_magic_numbers(source_code, language, result)
        self._check_long_lines(lines, result)
        self._check_long_functions(source_code, language, result)
        self._check_comments(lines, result)
        self._check_security(source_code, language, result)
        self._check_dead_code(source_code, language, result)
        self._check_cyclomatic_complexity(source_code, language, result)

        log.info(
            "Static analysis: score={:.0f}, issues={}",
            result.maintainability_score, len(result.smells),
        )

        return result

    def _check_naming(self, code: str, language: str, result: StaticAnalysisResult):
        """Checks naming conventions."""
        if language == "python":
            # Check for camelCase variable names (should be snake_case)
            camel_vars = re.findall(r'\b([a-z]+[A-Z][a-zA-Z]*)\s*=', code)
            for var in camel_vars[:3]:
                result.add_smell(CodeSmell(
                    "naming", f"Variable '{var}' uses camelCase; prefer snake_case in Python.",
                    "info",
                ))

            # Single-letter variable names (except common ones)
            single_letter = re.findall(r'\bfor\s+([a-z])\s+in\b', code)
            # This is acceptable for loop vars, skip

    def _check_magic_numbers(self, code: str, language: str, result: StaticAnalysisResult):
        """Detects magic numbers (numeric literals other than 0, 1, 2)."""
        for i, line in enumerate(code.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            # Find standalone numbers > 2
            numbers = re.findall(r'(?<![a-zA-Z_])\b(\d+)\b(?![a-zA-Z_])', stripped)
            for num in numbers:
                if int(num) > 2 and "range" not in stripped and "len" not in stripped:
                    result.add_smell(CodeSmell(
                        "magic_number",
                        f"Magic number {num} — consider using a named constant.",
                        "info", i,
                    ))
                    break  # One per line is enough

    def _check_long_lines(self, lines: List[str], result: StaticAnalysisResult):
        """Flags lines exceeding 120 characters."""
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > 120:
                result.add_smell(CodeSmell(
                    "readability",
                    f"Line {i} exceeds 120 characters ({len(line.rstrip())} chars).",
                    "info", i,
                ))

    def _check_long_functions(self, code: str, language: str, result: StaticAnalysisResult):
        """Flags functions exceeding 50 lines."""
        if language == "python":
            func_pattern = re.finditer(r'^(def\s+\w+)', code, re.MULTILINE)
            positions = [m.start() for m in func_pattern]
            for i, pos in enumerate(positions):
                end = positions[i + 1] if i + 1 < len(positions) else len(code)
                func_body = code[pos:end]
                line_count = len(func_body.strip().split("\n"))
                if line_count > 50:
                    func_name = re.match(r'def\s+(\w+)', func_body).group(1)
                    result.add_smell(CodeSmell(
                        "modularity",
                        f"Function '{func_name}' is {line_count} lines — consider refactoring.",
                        "warning",
                    ))

    def _check_comments(self, lines: List[str], result: StaticAnalysisResult):
        """Checks comment ratio."""
        total = len(lines)
        comments = sum(1 for l in lines if l.strip().startswith("#") or l.strip().startswith("//"))
        if total > 10 and comments == 0:
            result.add_smell(CodeSmell(
                "readability",
                "No comments found. Consider adding explanatory comments.",
                "info",
            ))

    def _check_security(self, code: str, language: str, result: StaticAnalysisResult):
        """Detects potential security issues."""
        dangerous_patterns = [
            (r'\beval\s*\(', "Use of eval() is a security risk."),
            (r'\bexec\s*\(', "Use of exec() is a security risk."),
            (r'\b__import__\s*\(', "Dynamic import via __import__() is risky."),
            (r'\bos\.system\s*\(', "Use of os.system() — prefer subprocess."),
            (r'\bsubprocess\.\w+\(.*shell\s*=\s*True', "subprocess with shell=True is risky."),
        ]
        for pattern, msg in dangerous_patterns:
            if re.search(pattern, code):
                result.add_smell(CodeSmell("security", msg, "error"))

    def _check_dead_code(self, code: str, language: str, result: StaticAnalysisResult):
        """Detects potential dead code patterns."""
        if language == "python":
            # Check for code after return
            lines = code.split("\n")
            in_function = False
            found_return = False
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("def "):
                    in_function = True
                    found_return = False
                elif in_function and stripped.startswith("return "):
                    found_return = True
                elif found_return and stripped and not stripped.startswith(("def ", "class ", "#", "@")):
                    indent = len(line) - len(line.lstrip())
                    if indent > 0:  # Still inside function
                        result.add_smell(CodeSmell(
                            "dead_code", f"Unreachable code after return (line {i}).",
                            "warning", i,
                        ))
                        found_return = False

    def _check_cyclomatic_complexity(self, code: str, language: str, result: StaticAnalysisResult):
        """Estimates cyclomatic complexity."""
        # Count decision points
        decision_keywords = ['if ', 'elif ', 'else:', 'for ', 'while ', 'except ',
                             'and ', 'or ', '? ']
        complexity = 1  # Base complexity
        for keyword in decision_keywords:
            complexity += code.count(keyword)

        result.metrics["cyclomatic_complexity"] = complexity

        if complexity > 15:
            result.add_smell(CodeSmell(
                "complexity",
                f"High cyclomatic complexity ({complexity}). Consider simplifying.",
                "warning",
            ))
