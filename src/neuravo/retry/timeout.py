"""Timeout management and enforcement.

Provides timeout handling for various operation types with clear
error messages and recovery information.
"""

import asyncio
from dataclasses import dataclass
from typing import Awaitable, TypeVar

from neuravo.core.exceptions import TimeoutError as NeuravoTimeoutError

T = TypeVar("T")


@dataclass
class TimeoutConfig:
    """Timeout configuration.

    Attributes:
        request_timeout: Per-request timeout in seconds
        stream_timeout: Streaming operation timeout in seconds
        connect_timeout: Connection establishment timeout in seconds
    """

    request_timeout: float = 30.0
    stream_timeout: float = 300.0
    connect_timeout: float = 10.0


class TimeoutManager:
    """Manages timeout enforcement for operations.

    Provides utilities for executing operations with configurable timeouts
    and handling timeout errors gracefully.
    """

    def __init__(self, config: TimeoutConfig):
        """Initialize timeout manager.

        Args:
            config: Timeout configuration
        """
        self.config = config

    async def execute_with_timeout(
        self,
        coro: Awaitable[T],
        timeout_type: str = "request",
    ) -> T:
        """Execute coroutine with timeout.

        Args:
            coro: Coroutine to execute
            timeout_type: Type of timeout (request, stream, connect)

        Returns:
            Coroutine result

        Raises:
            NeuravoTimeoutError: If operation times out
        """
        timeout = self._get_timeout(timeout_type)
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise NeuravoTimeoutError(
                f"Operation timed out after {timeout}s ({timeout_type})",
                timeout_seconds=timeout,
            ) from exc

    def _get_timeout(self, timeout_type: str) -> float:
        """Get timeout for operation type.

        Args:
            timeout_type: Type of timeout

        Returns:
            Timeout in seconds
        """
        return {
            "request": self.config.request_timeout,
            "stream": self.config.stream_timeout,
            "connect": self.config.connect_timeout,
        }.get(timeout_type, self.config.request_timeout)
