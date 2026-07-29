"""Type definitions and data structures for Neuravo SDK.

This module defines all core data structures used across the SDK:
- Message: Chat message representation
- ChatResponse: Response from chat operations
- TokenUsage: Token usage tracking
- HealthStatus: Provider health information
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Literal, Optional


@dataclass(frozen=True)
class TokenUsage:
    """Token usage statistics for API calls.

    Attributes:
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        total_tokens: Total tokens used (prompt + completion)
    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def __post_init__(self) -> None:
        """Validate token counts."""
        if self.prompt_tokens < 0 or self.completion_tokens < 0:
            raise ValueError("Token counts cannot be negative")
        if self.total_tokens != self.prompt_tokens + self.completion_tokens:
            raise ValueError(
                "Total tokens must equal prompt_tokens + completion_tokens"
            )


@dataclass(frozen=True)
class Message:
    """Immutable chat message representation.

    Attributes:
        role: Message role (user, assistant, or system)
        content: Message text content
        timestamp: When the message was created
        metadata: Additional message metadata
    """

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate message content."""
        if not self.content:
            raise ValueError("Message content cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary.

        Returns:
            Dictionary representation of message
        """
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Deserialize message from dictionary.

        Args:
            data: Dictionary containing message data

        Returns:
            Message instance

        Raises:
            ValueError: If required fields are missing
        """
        if "role" not in data or "content" not in data:
            raise ValueError("Message dict must contain 'role' and 'content'")

        timestamp_str = data.get("timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()

        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=timestamp,
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class ChatResponse:
    """Response from a chat operation.

    Attributes:
        content: The model's response text
        model: The model that generated the response
        usage: Token usage statistics
        timestamp: When the response was generated
        provider: The provider that generated the response
        metadata: Additional response metadata
    """

    content: str
    model: str
    usage: TokenUsage
    timestamp: datetime
    provider: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate response content."""
        if not self.content:
            raise ValueError("Response content cannot be empty")
        if not self.model:
            raise ValueError("Model name cannot be empty")
        if not self.provider:
            raise ValueError("Provider name cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize response to dictionary.

        Returns:
            Dictionary representation of response
        """
        return {
            "content": self.content,
            "model": self.model,
            "usage": {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
                "total_tokens": self.usage.total_tokens,
            },
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatResponse":
        """Deserialize response from dictionary.

        Args:
            data: Dictionary containing response data

        Returns:
            ChatResponse instance
        """
        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        timestamp_str = data.get("timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()

        return cls(
            content=data["content"],
            model=data["model"],
            usage=usage,
            timestamp=timestamp,
            provider=data.get("provider", "unknown"),
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class HealthStatus:
    """Provider health status information.

    Attributes:
        is_healthy: Whether the provider is operational
        latency_ms: Round-trip latency in milliseconds
        error_message: Error message if unhealthy
        last_check: When the health check was performed
    """

    is_healthy: bool
    latency_ms: float
    error_message: Optional[str] = None
    last_check: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate health status."""
        if self.latency_ms < 0:
            raise ValueError("Latency cannot be negative")
        if self.is_healthy and self.error_message:
            raise ValueError("Cannot be healthy with an error message")
