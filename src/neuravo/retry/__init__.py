"""Retry logic and backoff strategies.

Provides configurable retry behavior with exponential backoff and jitter
for resilient API interactions.
"""

import asyncio
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Retry configuration.

    Attributes:
        max_retries: Maximum retry attempts
        backoff_factor: Exponential backoff multiplier
        base_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds
        jitter: Whether to add random jitter
    """

    max_retries: int = 3
    backoff_factor: float = 2.0
    base_wait: float = 1.0
    max_wait: float = 60.0
    jitter: bool = True


class RetryStrategy(ABC):
    """Abstract retry strategy."""

    @abstractmethod
    async def execute(
        self,
        func: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with retry logic.

        Args:
            func: Callable to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Last exception if all retries exhausted
        """
        pass


class ExponentialBackoffRetry(RetryStrategy):
    """Exponential backoff retry strategy.

    Retries with exponentially increasing wait times between attempts.
    Optionally adds jitter to prevent thundering herd.
    """

    def __init__(self, config: RetryConfig):
        """Initialize retry strategy.

        Args:
            config: Retry configuration
        """
        self.config = config

    async def execute(
        self,
        func: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with exponential backoff retry.

        Args:
            func: Callable to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Last exception if all retries exhausted
        """
        last_error: Optional[Exception] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                # Try to execute the function
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_error = e

                # Check if this error is retryable
                if not self._is_retryable(e):
                    raise

                # Don't retry if we've exhausted attempts
                if attempt == self.config.max_retries:
                    raise

                # Calculate wait time and sleep
                wait_time = self._calculate_wait(attempt)
                await asyncio.sleep(wait_time)

        # Should not reach here, but safety fallback
        if last_error:
            raise last_error
        raise RuntimeError("Retry loop failed without exception")

    def _calculate_wait(self, attempt: int) -> float:
        """Calculate wait time for attempt.

        Implements exponential backoff with optional jitter.
        Formula: min(base_wait * (backoff_factor ^ attempt), max_wait)
        If jitter enabled, multiply result by random value between 0.5 and 1.0

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Wait time in seconds
        """
        # Calculate exponential backoff
        wait_time = self.config.base_wait * (self.config.backoff_factor ** attempt)

        # Cap at max wait
        wait_time = min(wait_time, self.config.max_wait)

        # Apply jitter if enabled
        if self.config.jitter:
            wait_time *= random.uniform(0.5, 1.0)

        return wait_time

    @staticmethod
    def _is_retryable(error: Exception) -> bool:
        """Determine if error is retryable.

        Classifies errors as retryable based on error type and message patterns.
        Retryable errors typically include:
        - Throttling/rate limiting
        - Service unavailability (temporary)
        - Timeout errors
        - Connection errors

        Args:
            error: Exception to check

        Returns:
            True if error is retryable, False if permanent

        Examples:
            Checking if error is retryable::

                try:
                    make_api_call()
                except Exception as e:
                    if ExponentialBackoffRetry._is_retryable(e):
                        print("Will retry")
                    else:
                        print("Permanent error")
        """
        # Get error type name and string representation
        error_name = type(error).__name__
        error_str = str(error).lower()

        # Retryable patterns
        retryable_patterns = [
            "throttling",
            "ratelimit",
            "rate_limit",
            "service unavailable",
            "serviceunavailable",
            "timeout",
            "connection reset",
            "connection refused",
            "temporarily unavailable",
            "too many requests",
            "backoff",
            "transient",
            "try again",
        ]

        # Check if error string contains retryable patterns
        for pattern in retryable_patterns:
            if pattern in error_str:
                return True

        # Retryable error types
        retryable_errors = [
            "TimeoutError",
            "ConnectionError",
            "BrokenPipeError",
            "ConnectionResetError",
            "ConnectionRefusedError",
            "ConnectionAbortedError",
        ]

        if error_name in retryable_errors:
            return True

        # Check for asyncio-specific errors
        if isinstance(error, asyncio.TimeoutError):
            return True

        return False
