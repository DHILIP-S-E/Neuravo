"""Abstract base provider interface for Neuravo SDK.

Defines the interface that all provider implementations must follow,
ensuring consistent behavior across different AI services.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from neuravo.core.config import Config
from neuravo.core.types import ChatResponse, HealthStatus, Message


class ModelInfo:
    """Information about an available model.

    Attributes:
        id: Model identifier
        provider: Provider that hosts this model
        name: Human-readable model name
        description: Model description
        capabilities: List of model capabilities
        max_tokens: Maximum context tokens supported
    """

    def __init__(
        self,
        id: str,
        provider: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        """Initialize ModelInfo."""
        self.id = id
        self.provider = provider
        self.name = name or id
        self.description = description or ""
        self.capabilities = capabilities or []
        self.max_tokens = max_tokens or 4096

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "provider": self.provider,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "max_tokens": self.max_tokens,
        }


class BaseProvider(ABC):
    """Abstract base class for provider implementations.

    All provider-specific implementations must inherit from this class
    and implement all abstract methods. Providers handle the actual
    communication with AI services.

    Examples:
        Implement a custom provider::

            class MyProvider(BaseProvider):
                async def initialize(self, config: Config) -> None:
                    # Setup provider
                    pass

                def validate_config(self, config: Config) -> bool:
                    # Validate config
                    return True

                def get_available_models(self) -> List[ModelInfo]:
                    # Return list of models
                    return []

                async def health_check(self) -> HealthStatus:
                    # Check provider health
                    pass
    """

    @abstractmethod
    async def initialize(self, config: Config) -> None:
        """Initialize provider with configuration.

        This method should establish connections and validate credentials.

        Args:
            config: Configuration object for this provider

        Raises:
            ProviderError: If initialization fails
            ConfigError: If configuration is invalid
        """
        pass

    @abstractmethod
    def validate_config(self, config: Config) -> bool:
        """Validate provider-specific configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ConfigError: If validation fails
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models for this provider.

        Returns:
            List of ModelInfo objects representing available models
        """
        pass

    @abstractmethod
    async def chat(self, messages: List[Message]) -> ChatResponse:
        """Send a chat request and return the complete response.

        Args:
            messages: Conversation so far, oldest first

        Returns:
            ChatResponse with the model's reply

        Raises:
            ProviderError: If the underlying API call fails
        """
        pass

    @abstractmethod
    async def stream_chat(self, messages: List[Message]) -> AsyncIterator[ChatResponse]:
        """Send a chat request and stream the response progressively.

        Args:
            messages: Conversation so far, oldest first

        Yields:
            ChatResponse chunks as they arrive

        Raises:
            ProviderError: If the underlying API call fails
            StreamingError: If streaming fails mid-transfer
        """
        # A `yield` (even unreachable) is required so mypy infers this as an
        # async generator function rather than a plain coroutine - without
        # it, every real override's AsyncIterator return type mismatches.
        if False:  # noqa: SIM105
            yield  # type: ignore[unreachable]

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """Check if provider is healthy and responsive.

        Returns:
            HealthStatus indicating provider health

        Raises:
            ProviderError: If health check fails
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close provider connection and cleanup resources.

        This method should be called when done with the provider to
        release any open connections or resources.
        """
        pass
