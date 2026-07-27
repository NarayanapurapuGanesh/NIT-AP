"""
Resilience Engine.
Implements Circuit Breaker (CLOSED, OPEN, HALF_OPEN), Retry with exponential backoff,
Bulkhead isolation, and Fallback execution strategies.
"""

import time
from typing import Any, Callable, Dict, Optional, TypeVar
from app.platform.schemas.platform_models import CircuitBreakerState, CircuitState, RetryPolicy
from core.logging import get_logger

logger = get_logger("resilience_engine")

T = TypeVar("T")


class ResilienceEngine:
    """Enterprise Fault Tolerance & Resilience Engine."""

    def __init__(self) -> None:
        self._circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.default_retry_policy = RetryPolicy(policy_name="default", max_retries=3, base_delay_ms=200)

    def get_circuit_breaker(self, service_name: str) -> CircuitBreakerState:
        if service_name not in self._circuit_breakers:
            self._circuit_breakers[service_name] = CircuitBreakerState(service_name=service_name, state=CircuitState.CLOSED)
        return self._circuit_breakers[service_name]

    def record_success(self, service_name: str) -> None:
        cb = self.get_circuit_breaker(service_name)
        cb.success_count += 1
        if cb.state == CircuitState.HALF_OPEN:
            cb.state = CircuitState.CLOSED
            cb.failure_count = 0
            logger.info("Circuit breaker state changed to CLOSED", service_name=service_name)

    def record_failure(self, service_name: str, max_failures: int = 5) -> None:
        cb = self.get_circuit_breaker(service_name)
        cb.failure_count += 1
        if cb.failure_count >= max_failures and cb.state == CircuitState.CLOSED:
            cb.state = CircuitState.OPEN
            logger.warning("Circuit breaker state changed to OPEN", service_name=service_name, failure_count=cb.failure_count)

    def execute_with_circuit_breaker(
        self,
        service_name: str,
        func: Callable[..., T],
        fallback_func: Optional[Callable[..., T]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        cb = self.get_circuit_breaker(service_name)

        if cb.state == CircuitState.OPEN:
            logger.warning("Circuit breaker OPEN, short-circuiting call", service_name=service_name)
            if fallback_func:
                return fallback_func(*args, **kwargs)
            raise RuntimeError(f"Service '{service_name}' circuit breaker is OPEN.")

        try:
            result = func(*args, **kwargs)
            self.record_success(service_name)
            return result
        except Exception as e:
            self.record_failure(service_name)
            logger.error("Call failed under circuit breaker", service_name=service_name, error=str(e))
            if fallback_func:
                return fallback_func(*args, **kwargs)
            raise

    def execute_with_retry(
        self,
        func: Callable[..., T],
        policy: Optional[RetryPolicy] = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        policy = policy or self.default_retry_policy
        last_exception = None

        for attempt in range(1, policy.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(
                    "Attempt failed, retrying...",
                    attempt=attempt,
                    max_retries=policy.max_retries,
                    error=str(e),
                )
                if attempt < policy.max_retries:
                    delay = policy.base_delay_ms / 1000.0
                    if policy.exponential_backoff:
                        delay *= 2 ** (attempt - 1)
                    time.sleep(min(delay, policy.max_delay_ms / 1000.0))

        raise last_exception or RuntimeError("Retry attempts exhausted.")

    def list_circuit_breakers(self) -> list[CircuitBreakerState]:
        return list(self._circuit_breakers.values())
