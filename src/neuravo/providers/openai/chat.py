"""OpenAI provider implementation for Neuravo SDK.

Requires the optional `openai` dependency (`pip install neuravo[openai]`).
Unlike Bedrock, OpenAI's own SDK is natively async, so no thread-bridging
is needed here.
"""

import time
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

import openai
from openai import AsyncOpenAI

from neuravo.core.config import Config
from neuravo.core.exceptions import OpenAIError
from neuravo.core.types import ChatResponse, HealthStatus, Message, TokenUsage
from neuravo.providers.base import BaseProvider, ModelInfo

DEFAULT_MODEL_ID = "gpt-4o-mini"


class OpenAIConfig(Config):
    """OpenAI-specific configuration.

    Attributes:
        api_key: OpenAI API key (uses OPENAI_API_KEY env var if not set -
            the openai SDK itself handles that fallback)
        organization: Optional OpenAI organization id
    """

    api_key: Optional[str] = None
    organization: Optional[str] = None


_MODEL_CATALOG = [
    ("gpt-4o", "GPT-4o", 128000),
    ("gpt-4o-mini", "GPT-4o mini", 128000),
    ("gpt-3.5-turbo", "GPT-3.5 Turbo", 16385),
]


def get_available_model_infos() -> List[ModelInfo]:
    """Get the curated list of supported OpenAI chat models.

    Returns:
        List of ModelInfo for supported models
    """
    return [
        ModelInfo(
            id=model_id,
            provider="openai",
            name=name,
            capabilities=["streaming"],
            max_tokens=max_tokens,
        )
        for model_id, name, max_tokens in _MODEL_CATALOG
    ]


class ChatHandler:
    """Formats messages for and parses responses from the OpenAI Chat Completions API."""

    @staticmethod
    def format_messages(messages: List[Message]) -> List[Dict[str, str]]:
        """Format messages for the OpenAI API.

        Unlike Bedrock's Converse API, OpenAI accepts "system" as a normal
        message role, so no splitting is needed.

        Args:
            messages: List of messages to format

        Returns:
            List of message dicts in OpenAI's format
        """
        return [{"role": message.role, "content": message.content} for message in messages]


class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation.

    Attributes:
        client: AsyncOpenAI client
        config: Provider configuration
    """

    def __init__(self) -> None:
        """Initialize OpenAI provider."""
        super().__init__()
        self.client: Optional[AsyncOpenAI] = None
        self.config: Optional[Config] = None
        self._model: str = DEFAULT_MODEL_ID

    async def initialize(self, config: Config) -> None:
        """Initialize the OpenAI provider.

        Args:
            config: Configuration specifying model and (optionally) API key

        Raises:
            OpenAIError: If the client fails to construct
        """
        self.validate_config(config)
        self.config = config
        self._model = config.model or DEFAULT_MODEL_ID

        client_kwargs: Dict[str, Any] = {}
        if isinstance(config, OpenAIConfig):
            if config.api_key:
                client_kwargs["api_key"] = config.api_key
            if config.organization:
                client_kwargs["organization"] = config.organization

        try:
            self.client = AsyncOpenAI(**client_kwargs)
        except openai.OpenAIError as exc:
            raise OpenAIError(f"Failed to initialize OpenAI client: {exc}") from exc

    def validate_config(self, config: Config) -> bool:
        """Validate OpenAI-specific configuration.

        Unlike Bedrock, no field is strictly required - the API key can
        come from the OPENAI_API_KEY environment variable.

        Args:
            config: Configuration to validate

        Returns:
            True (always - see above)
        """
        return True

    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available OpenAI chat models.

        Returns:
            List of supported models
        """
        return get_available_model_infos()

    async def chat(self, messages: List[Message]) -> ChatResponse:
        """Send a chat request to OpenAI and return the complete response.

        Args:
            messages: Conversation so far, oldest first

        Returns:
            ChatResponse with the model's reply

        Raises:
            OpenAIError: If the underlying API call fails
        """
        if self.client is None:
            raise OpenAIError("OpenAI provider is not initialized")

        try:
            # openai's stubs want a precise TypedDict union per role; plain
            # dicts are accepted at runtime and are what ChatHandler builds.
            response = await self.client.chat.completions.create(
                model=self._model,
                messages=ChatHandler.format_messages(messages),  # type: ignore[arg-type]
            )
        except openai.OpenAIError as exc:
            raise OpenAIError(f"OpenAI chat request failed: {exc}") from exc

        choice = response.choices[0]
        usage = response.usage
        return ChatResponse(
            content=choice.message.content or "",
            model=self._model,
            usage=TokenUsage(
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
            ),
            timestamp=datetime.now(),
            provider="openai",
        )

    async def stream_chat(self, messages: List[Message]) -> AsyncIterator[ChatResponse]:
        """Send a chat request to OpenAI and stream the response.

        Args:
            messages: Conversation so far, oldest first

        Yields:
            ChatResponse chunks as they arrive

        Raises:
            OpenAIError: If the underlying API call fails
        """
        if self.client is None:
            raise OpenAIError("OpenAI provider is not initialized")

        try:
            stream = await self.client.chat.completions.create(
                model=self._model,
                messages=ChatHandler.format_messages(messages),  # type: ignore[arg-type]
                stream=True,
            )
        except openai.OpenAIError as exc:
            raise OpenAIError(f"OpenAI streaming request failed: {exc}") from exc

        # mypy sees the non-streaming/streaming overload as a Union here
        # since `stream` isn't visible to it as a Literal[True] through the
        # kwargs dict built by this method's own call.
        async for chunk in stream:  # type: ignore[union-attr]
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield ChatResponse(
                    content=delta,
                    model=self._model,
                    usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                    timestamp=datetime.now(),
                    provider="openai",
                    metadata={"chunk": True},
                )

    async def health_check(self) -> HealthStatus:
        """Check OpenAI provider health.

        Returns:
            HealthStatus indicating service availability
        """
        if self.client is None:
            return HealthStatus(
                is_healthy=False,
                latency_ms=0.0,
                error_message="Provider not initialized",
            )

        start = time.perf_counter()
        try:
            await self.client.models.list()
            latency_ms = (time.perf_counter() - start) * 1000
            return HealthStatus(is_healthy=True, latency_ms=latency_ms)
        except openai.OpenAIError as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            return HealthStatus(is_healthy=False, latency_ms=latency_ms, error_message=str(exc))

    async def close(self) -> None:
        """Close the OpenAI client connection."""
        if self.client is not None:
            await self.client.close()
        self.client = None
