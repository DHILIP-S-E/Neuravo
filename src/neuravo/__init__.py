"""Neuravo: Production-Grade Python AI Infrastructure SDK.

A provider-agnostic interface for AI model interactions with production-ready
error handling, retry logic, and streaming support.

Examples:
    Basic usage::

        import asyncio
        from neuravo import Client, Config

        async def main():
            config = Config(provider="bedrock", region="us-east-1")
            client = Client(config)
            response = await client.chat("What is machine learning?")
            print(response.content)

        asyncio.run(main())

    Streaming responses::

        async def stream_chat():
            async for chunk in client.stream("Tell me a story"):
                print(chunk.content, end="", flush=True)

Version:
    0.1.0 (MVP with Bedrock support)
"""

import logging
from typing import AsyncIterator, List, Optional, cast

# Importing each provider family triggers its self-registration with
# ProviderRegistry (see providers/aws/__init__.py). providers.openai is a
# no-op if the optional `openai` dependency isn't installed.
import neuravo.providers.aws  # noqa: F401,E402
import neuravo.providers.openai  # noqa: F401,E402
from neuravo.chat.history import ConversationHistory
from neuravo.core.client import BaseClient
from neuravo.core.config import Config
from neuravo.core.exceptions import (
    ConfigError,
    NeurevoError,
    ProviderError,
    StreamingError,
    ValidationError,
)
from neuravo.core.exceptions import (
    TimeoutError as NeurevoTimeoutError,
)
from neuravo.core.types import ChatResponse, HealthStatus, Message
from neuravo.observability.logging import get_logger as _get_logger_impl
from neuravo.observability.logging import setup_logging as _setup_logging_impl
from neuravo.providers.base import BaseProvider
from neuravo.providers.registry import ProviderRegistry
from neuravo.retry import ExponentialBackoffRetry, RetryConfig
from neuravo.utils.validators import validate_prompt
from neuravo.version import __version__

__all__ = [
    "__version__",
    "Client",
    "Config",
    "BaseClient",
    "NeurevoError",
    "ProviderError",
    "ConfigError",
    "NeurevoTimeoutError",
    "ValidationError",
    "StreamingError",
    "setup_logging",
    "get_logger",
]


class Client(BaseClient):
    """Main client interface for AI interactions.

    The Client provides a unified interface for interacting with AI providers
    (Bedrock, OpenAI, Anthropic, etc.) with automatic provider selection based
    on configuration.

    Attributes:
        config: Configuration object specifying provider and behavior
        provider: Active provider instance

    Examples:
        Create and use a client::

            config = Config(provider="bedrock", region="us-east-1")
            client = Client(config)
            response = await client.chat("Hello, world!")
    """

    def __init__(self, config: Config) -> None:
        """Initialize client with configuration.

        Args:
            config: Configuration object specifying provider and settings
        """
        super().__init__(config)
        self._provider: Optional[BaseProvider] = None
        self._history = ConversationHistory()

    async def initialize(self) -> None:
        """Resolve and initialize the configured provider.

        Called automatically on first use if not called explicitly.

        Raises:
            ProviderNotFoundError: If the configured provider isn't registered
            ProviderError: If the provider fails to initialize
        """
        if self._provider is not None:
            return
        provider = ProviderRegistry.get(self.config.provider)
        await provider.initialize(self.config)
        self._provider = provider

    async def chat(self, prompt: str) -> ChatResponse:
        """Send a chat prompt and get a response.

        Args:
            prompt: User input message

        Returns:
            ChatResponse containing the model's response

        Raises:
            ValidationError: If prompt is empty or invalid
            ProviderError: If the provider call fails
        """
        validate_prompt(prompt)
        if self._provider is None:
            await self.initialize()
        assert self._provider is not None  # initialize() always sets this or raises

        self._history.add(Message(role="user", content=prompt))
        retry = ExponentialBackoffRetry(
            RetryConfig(
                max_retries=self.config.max_retries,
                backoff_factor=self.config.backoff_factor,
            )
        )
        response = cast(
            ChatResponse,
            await retry.execute(self._provider.chat, self._history.get_all()),
        )
        self._history.add(Message(role="assistant", content=response.content))
        return response

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
        validate_prompt(prompt)
        if self._provider is None:
            await self.initialize()
        assert self._provider is not None  # initialize() always sets this or raises

        self._history.add(Message(role="user", content=prompt))
        accumulated = ""
        async for chunk in self._provider.stream_chat(self._history.get_all()):
            if chunk.content:
                accumulated += chunk.content
            yield chunk

        self._history.add(Message(role="assistant", content=accumulated))

    async def get_chat_history(self) -> List[Message]:
        """Get the conversation history.

        Returns:
            List of messages in chronological order
        """
        return self._history.get_all()

    async def clear_history(self) -> None:
        """Clear the conversation history."""
        self._history.clear()

    async def health_check(self) -> HealthStatus:
        """Check if the provider is healthy.

        Returns:
            HealthStatus indicating provider health
        """
        if self._provider is None:
            return HealthStatus(
                is_healthy=False,
                latency_ms=0.0,
                error_message="Client not initialized",
            )
        return await self._provider.health_check()

    async def close(self) -> None:
        """Close the client connection and cleanup resources."""
        if self._provider is not None:
            await self._provider.close()
            self._provider = None


def setup_logging(level: str = "INFO") -> None:
    """Configure SDK logging with sensible defaults.

    Sets up logging for all neuravo modules with the specified level.
    Logs are written to stderr and optionally to a file.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Examples:
        Enable debug logging::

            from neuravo import setup_logging
            setup_logging("DEBUG")
    """
    _setup_logging_impl(level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module.

    Args:
        name: Module name (e.g., "core", "providers.aws.bedrock")

    Returns:
        Configured logger instance
    """
    return _get_logger_impl(name)
