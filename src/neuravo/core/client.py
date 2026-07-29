"""Base client interface for Neuravo SDK.

Defines the abstract base class that all clients must implement,
providing a unified interface across different providers.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List

from neuravo.core.config import Config
from neuravo.core.types import ChatResponse, HealthStatus, Message


class BaseClient(ABC):
    """Abstract base class for all Neuravo clients.

    Defines the contract that all provider-specific clients must implement,
    ensuring a consistent interface regardless of the underlying provider.

    Attributes:
        config: Configuration for this client instance
    """

    def __init__(self, config: Config) -> None:
        """Initialize client with configuration.

        Args:
            config: Configuration object specifying provider and settings
        """
        self.config = config

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the client connection.

        This method establishes the connection to the provider and validates
        credentials. It must be called before using the client.

        Raises:
            ProviderError: If initialization fails (e.g., bad credentials)
            ConfigError: If configuration is invalid for this provider
        """
        pass

    @abstractmethod
    async def chat(self, prompt: str) -> ChatResponse:
        """Send a chat prompt and get a response.

        Args:
            prompt: User input message

        Returns:
            ChatResponse containing the model's response

        Raises:
            ValidationError: If prompt is empty or invalid
            ProviderError: If the provider call fails
            TimeoutError: If the request exceeds timeout
        """
        pass

    @abstractmethod
    async def stream(self, prompt: str) -> AsyncIterator[ChatResponse]:
        """Stream a chat response progressively.

        Args:
            prompt: User input message

        Yields:
            ChatResponse chunks as they arrive from the provider

        Raises:
            ValidationError: If prompt is empty or invalid
            ProviderError: If the provider call fails
            StreamingError: If streaming fails mid-transfer
        """
        # A `yield` (even unreachable) is required so mypy infers this as an
        # async generator function rather than a plain coroutine - without
        # it, every real override's AsyncIterator return type mismatches.
        if False:  # noqa: SIM105
            yield  # type: ignore[unreachable]

    @abstractmethod
    async def get_chat_history(self) -> List[Message]:
        """Get the conversation history.

        Returns:
            List of messages in chronological order
        """
        pass

    @abstractmethod
    async def clear_history(self) -> None:
        """Clear the conversation history."""
        pass

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """Check if the provider is healthy.

        Returns:
            HealthStatus indicating provider health

        Raises:
            ProviderError: If health check fails
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the client connection and cleanup resources.

        This method should be called when done with the client to release
        any open connections or resources.
        """
        pass
