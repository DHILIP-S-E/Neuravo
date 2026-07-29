"""AWS Bedrock provider implementation for Neuravo SDK.

This module implements support for AWS Bedrock, providing access to multiple
foundation models (Anthropic Claude, Meta Llama, etc.) through a unified
interface. It bundles configuration, model metadata, the provider itself,
and the chat/streaming request handlers into a single module, consistent
with the v0.1 provider layout (one flat file per vendor rather than a
nested package).

Talks to Bedrock via the ``converse``/``converse_stream`` APIs, which use
the same request/response shape across model families (Claude, Llama,
Titan, ...) instead of each model's own ``invoke_model`` payload format.

Examples:
    Use Bedrock provider::

        from neuravo import Client, Config

        config = Config(
            provider="bedrock",
            region="us-east-1",
            model="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        client = Client(config)
        response = await client.chat("Hello, world!")
"""

import asyncio
import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from neuravo.core.config import Config
from neuravo.core.exceptions import BedrockError, MissingConfigError
from neuravo.core.types import ChatResponse, HealthStatus, Message, TokenUsage
from neuravo.providers.base import BaseProvider, ModelInfo

DEFAULT_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# Sentinel used to signal the end of a background thread's event queue.
_STREAM_DONE = object()


class BedrockConfig(Config):
    """AWS Bedrock-specific configuration.

    Extends the base Config with Bedrock-specific settings.

    Attributes:
        access_key_id: AWS access key (uses AWS_ACCESS_KEY_ID env var if not set)
        secret_access_key: AWS secret access key (uses AWS_SECRET_ACCESS_KEY if not set)
        session_token: Optional AWS session token
        inference_id: Optional inference ID for tracking
    """

    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
    inference_id: Optional[str] = None


@dataclass
class BedrockModel:
    """Bedrock model information.

    Attributes:
        id: Model identifier (e.g., anthropic.claude-3-sonnet)
        name: Human-readable name
        provider: Model provider (Anthropic, Meta, etc.)
        max_tokens: Maximum context window size
        supports_streaming: Whether model supports streaming
        description: Model description
    """

    id: str
    name: str
    provider: str
    max_tokens: int
    supports_streaming: bool
    description: Optional[str] = None


# List of available Bedrock models (v0.1)
BEDROCK_MODELS: List[BedrockModel] = [
    BedrockModel(
        id="anthropic.claude-3-sonnet-20240229-v1:0",
        name="Claude 3 Sonnet",
        provider="Anthropic",
        max_tokens=200000,
        supports_streaming=True,
        description="Fast and compact model for general use",
    ),
    BedrockModel(
        id="anthropic.claude-3-haiku-20240307-v1:0",
        name="Claude 3 Haiku",
        provider="Anthropic",
        max_tokens=200000,
        supports_streaming=True,
        description="Fastest model, optimized for speed",
    ),
    BedrockModel(
        id="meta.llama2-70b-chat-v1",
        name="Llama 2 70B Chat",
        provider="Meta",
        max_tokens=4096,
        supports_streaming=True,
        description="Open-source model for general conversation",
    ),
]


def get_model_by_id(model_id: str) -> Optional[BedrockModel]:
    """Get model information by model ID.

    Args:
        model_id: Model identifier

    Returns:
        BedrockModel if found, None otherwise
    """
    for model in BEDROCK_MODELS:
        if model.id == model_id:
            return model
    return None


def get_all_models() -> List[BedrockModel]:
    """Get all available Bedrock models.

    Returns:
        List of all BedrockModel objects
    """
    return BEDROCK_MODELS.copy()


class ChatHandler:
    """Handles chat request/response formatting for Bedrock.

    Provides methods to format chat messages for Bedrock's Converse API
    and parse responses back into ChatResponse-ready values.
    """

    @staticmethod
    def format_messages(
        messages: List[Message],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """Format messages for the Bedrock Converse API.

        Converse takes ``system`` prompts separately from the conversation
        turns, so system-role messages are split out rather than included
        inline.

        Args:
            messages: List of messages to format

        Returns:
            Tuple of (conversation turns, system blocks) in Converse format
        """
        turns: List[Dict[str, Any]] = []
        system_blocks: List[Dict[str, str]] = []

        for message in messages:
            if message.role == "system":
                system_blocks.append({"text": message.content})
            else:
                turns.append(
                    {
                        "role": message.role,
                        "content": [{"text": message.content}],
                    }
                )

        return turns, system_blocks

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> Tuple[str, TokenUsage]:
        """Parse a Bedrock Converse response.

        Args:
            response: Raw Bedrock ``converse`` API response

        Returns:
            Tuple of (response text, token usage)

        Raises:
            BedrockError: If the response has no text content
        """
        try:
            content_blocks = response["output"]["message"]["content"]
            text = "".join(
                block["text"] for block in content_blocks if "text" in block
            )
        except (KeyError, IndexError) as exc:
            raise BedrockError(
                f"Unexpected Bedrock response shape: {exc}",
                debug_details={"response": response},
            ) from exc

        usage_data = response.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("inputTokens", 0),
            completion_tokens=usage_data.get("outputTokens", 0),
            total_tokens=usage_data.get(
                "totalTokens",
                usage_data.get("inputTokens", 0) + usage_data.get("outputTokens", 0),
            ),
        )
        return text, usage


class StreamingHandler:
    """Handles streaming responses from Bedrock.

    Processes ``converse_stream`` event-stream responses and yields
    response chunks as they arrive.
    """

    @staticmethod
    async def handle_stream(
        stream_response: Dict[str, Any],
        model: str,
    ) -> AsyncIterator[ChatResponse]:
        """Handle a streaming response from Bedrock.

        ``converse_stream``'s event iterator performs blocking network
        reads, so it's consumed on a background thread and bridged to an
        async generator through a queue.

        Args:
            stream_response: Bedrock ``converse_stream`` API response
            model: Model ID that produced this response, for ChatResponse.metadata

        Yields:
            ChatResponse chunks as they arrive
        """
        loop = asyncio.get_event_loop()
        q: "queue.Queue[Any]" = queue.Queue()

        def _consume() -> None:
            try:
                for event in stream_response["stream"]:
                    q.put(event)
            except Exception as exc:  # noqa: BLE001 - forwarded to the async side
                q.put(exc)
            finally:
                q.put(_STREAM_DONE)

        threading.Thread(target=_consume, daemon=True).start()

        while True:
            event = await loop.run_in_executor(None, q.get)
            if event is _STREAM_DONE:
                break
            if isinstance(event, Exception):
                raise BedrockError(f"Bedrock stream failed: {event}") from event

            # Bedrock also emits a trailing "metadata" event carrying final
            # token usage, but ChatResponse requires non-empty content (a
            # real domain invariant - see core/types.py), so there's no
            # content-free chunk to attach it to. Usage totals belong to
            # the non-streaming chat() path; streaming here only carries
            # text deltas.
            delta = event.get("contentBlockDelta", {}).get("delta", {})
            text = delta.get("text")
            if text:
                yield ChatResponse(
                    content=text,
                    model=model,
                    usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                    timestamp=datetime.now(),
                    provider="bedrock",
                    metadata={"chunk": True},
                )


class BedrockProvider(BaseProvider):
    """AWS Bedrock provider implementation.

    Handles all interactions with AWS Bedrock, including:
    - Authentication via AWS credentials
    - Model discovery and selection
    - Chat requests and streaming responses
    - Health monitoring

    Attributes:
        client: Boto3 Bedrock runtime client
        config: Provider configuration
    """

    def __init__(self) -> None:
        """Initialize Bedrock provider."""
        super().__init__()
        self.client: Optional[Any] = None
        self._control_client: Optional[Any] = None
        self.config: Optional[Config] = None
        self._model: str = DEFAULT_MODEL_ID

    async def initialize(self, config: Config) -> None:
        """Initialize Bedrock provider.

        Establishes connection to AWS Bedrock and validates credentials.

        Args:
            config: Configuration specifying region and model

        Raises:
            BedrockError: If AWS credentials are invalid or missing
            MissingConfigError: If region is not specified
        """
        self.validate_config(config)
        self.config = config
        self._model = config.model or DEFAULT_MODEL_ID

        client_kwargs: Dict[str, Any] = {"region_name": config.region}
        if isinstance(config, BedrockConfig):
            if config.access_key_id:
                client_kwargs["aws_access_key_id"] = config.access_key_id
            if config.secret_access_key:
                client_kwargs["aws_secret_access_key"] = config.secret_access_key
            if config.session_token:
                client_kwargs["aws_session_token"] = config.session_token

        try:
            self.client = await asyncio.to_thread(
                boto3.client, "bedrock-runtime", **client_kwargs
            )
            # Separate control-plane client (model listing, health checks) —
            # "bedrock-runtime" only exposes converse/converse_stream/invoke_model.
            self._control_client = await asyncio.to_thread(
                boto3.client, "bedrock", **client_kwargs
            )
        except (BotoCoreError, ClientError) as exc:
            raise BedrockError(f"Failed to initialize Bedrock client: {exc}") from exc

    def validate_config(self, config: Config) -> bool:
        """Validate Bedrock-specific configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if valid

        Raises:
            MissingConfigError: If region is missing
        """
        if not config.region:
            raise MissingConfigError(["region"])
        return True

    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available Bedrock models.

        Returns:
            List of supported foundation models

        Examples:
            Get available models::

                provider = BedrockProvider()
                models = provider.get_available_models()
                for model in models:
                    print(f"{model.name}: {model.id}")
        """
        return [
            ModelInfo(
                id=model.id,
                provider="bedrock",
                name=model.name,
                description=model.description,
                capabilities=["streaming"] if model.supports_streaming else [],
                max_tokens=model.max_tokens,
            )
            for model in BEDROCK_MODELS
        ]

    async def chat(self, messages: List[Message]) -> ChatResponse:
        """Send a chat request to Bedrock and return the complete response.

        Args:
            messages: Conversation so far, oldest first

        Returns:
            ChatResponse with the model's reply

        Raises:
            BedrockError: If the underlying API call fails
        """
        if self.client is None:
            raise BedrockError("Bedrock provider is not initialized")

        turns, system_blocks = ChatHandler.format_messages(messages)
        request: Dict[str, Any] = {"modelId": self._model, "messages": turns}
        if system_blocks:
            request["system"] = system_blocks

        try:
            response = await asyncio.to_thread(self.client.converse, **request)
        except (BotoCoreError, ClientError) as exc:
            raise BedrockError(f"Bedrock chat request failed: {exc}") from exc

        text, usage = ChatHandler.parse_response(response)
        return ChatResponse(
            content=text,
            model=self._model,
            usage=usage,
            timestamp=datetime.now(),
            provider="bedrock",
        )

    async def stream_chat(self, messages: List[Message]) -> AsyncIterator[ChatResponse]:
        """Send a chat request to Bedrock and stream the response.

        Args:
            messages: Conversation so far, oldest first

        Yields:
            ChatResponse chunks as they arrive

        Raises:
            BedrockError: If the underlying API call fails
        """
        if self.client is None:
            raise BedrockError("Bedrock provider is not initialized")

        turns, system_blocks = ChatHandler.format_messages(messages)
        request: Dict[str, Any] = {"modelId": self._model, "messages": turns}
        if system_blocks:
            request["system"] = system_blocks

        try:
            stream_response = await asyncio.to_thread(
                self.client.converse_stream, **request
            )
        except (BotoCoreError, ClientError) as exc:
            raise BedrockError(f"Bedrock streaming request failed: {exc}") from exc

        async for chunk in StreamingHandler.handle_stream(stream_response, self._model):
            yield chunk

    async def health_check(self) -> HealthStatus:
        """Check Bedrock provider health.

        Returns:
            HealthStatus indicating service availability
        """
        if self.client is None or self._control_client is None:
            return HealthStatus(
                is_healthy=False,
                latency_ms=0.0,
                error_message="Provider not initialized",
            )

        start = time.perf_counter()
        try:
            await asyncio.to_thread(self._control_client.list_foundation_models)
            latency_ms = (time.perf_counter() - start) * 1000
            return HealthStatus(is_healthy=True, latency_ms=latency_ms)
        except (BotoCoreError, ClientError) as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            return HealthStatus(
                is_healthy=False,
                latency_ms=latency_ms,
                error_message=str(exc),
            )

    async def close(self) -> None:
        """Close Bedrock connection."""
        self.client = None
        self._control_client = None
