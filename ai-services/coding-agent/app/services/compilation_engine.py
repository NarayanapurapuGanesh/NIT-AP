"""
FacultyIQ Coding Intelligence Agent — Compilation Engine.

Orchestrates compile + execute for all supported languages,
capturing detailed metrics for each submission.
"""

from app.core.logging import get_module_logger
from app.models.sandbox import ExecutionRequest, ExecutionResult, ExecutionStatus
from app.sandbox.sandbox_manager import SandboxManager

log = get_module_logger("compilation")

# Standard I/O wrappers that convert function-style solutions into stdin/stdout programs
CODE_WRAPPERS = {
    "python": """
import sys

{user_code}

# --- Auto-generated I/O wrapper ---
if __name__ == "__main__":
    input_data = sys.stdin.read().strip()
    lines = input_data.split("\\n") if input_data else []
    # Pass all input lines to the first function found
    import inspect
    funcs = [obj for name, obj in list(locals().items()) if callable(obj) and not name.startswith('_') and name != 'sys']
    if funcs:
        func = funcs[-1]
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        if len(params) == 1:
            # Single param: try to parse as list of ints, else pass as string
            try:
                args = [list(map(int, lines[0].split()))]
            except (ValueError, IndexError):
                args = [input_data]
        elif len(params) == 2:
            try:
                args = [list(map(int, lines[0].split())), int(lines[1])]
            except (ValueError, IndexError):
                args = [lines[0] if lines else "", lines[1] if len(lines) > 1 else ""]
        else:
            args = lines[:len(params)]
        result = func(*args)
        if isinstance(result, list):
            print(" ".join(map(str, result)))
        elif isinstance(result, bool):
            print("true" if result else "false")
        elif result is not None:
            print(result)
""",
}


class CompilationEngine:
    """
    Language-aware compilation and execution engine.

    Wraps user code with I/O adapters and delegates execution
    to the SandboxManager.
    """

    def __init__(self, sandbox: SandboxManager | None = None):
        self.sandbox = sandbox or SandboxManager()

    def compile_and_run(
        self,
        source_code: str,
        language: str,
        stdin: str = "",
        timeout_seconds: int = 15,
        memory_limit_mb: int = 256,
        wrap_io: bool = True,
    ) -> ExecutionResult:
        """
        Compiles and executes code, returning detailed results.

        Args:
            source_code: The candidate's source code
            language:     Programming language
            stdin:        Input to feed to the program
            timeout_seconds: Maximum execution time
            memory_limit_mb: Maximum memory usage
            wrap_io:      Whether to wrap the code with I/O adapter
        """
        final_code = source_code

        # Apply I/O wrapper if available and requested
        if wrap_io and language in CODE_WRAPPERS:
            final_code = CODE_WRAPPERS[language].format(user_code=source_code)

        request = ExecutionRequest(
            source_code=final_code,
            language=language,
            stdin=stdin,
            timeout_seconds=timeout_seconds,
            memory_limit_mb=memory_limit_mb,
        )

        log.info(
            "Executing {} code ({} bytes, timeout={}s)",
            language, len(source_code), timeout_seconds,
        )

        result = self.sandbox.execute(request)

        log.info(
            "Execution result: status={}, time={:.1f}ms, exit={}",
            result.status.value, result.execution_time_ms, result.exit_code,
        )

        return result

    def run_with_stdin(
        self, source_code: str, language: str, stdin: str
    ) -> ExecutionResult:
        """Convenience method to run code with specific stdin input."""
        return self.compile_and_run(
            source_code=source_code,
            language=language,
            stdin=stdin,
        )
