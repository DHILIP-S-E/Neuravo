"""Unit tests for core module.

Tests core abstractions and interfaces.
"""

from datetime import datetime

import pytest

from neuravo.core.config import Config
from neuravo.core.exceptions import ConfigError, NeurevoError
from neuravo.core.types import ChatResponse, HealthStatus, Message, TokenUsage


class TestExceptions:
    """Test exception classes."""

    def test_neuravo_error_creation(self):
        """Test NeurevoError can be created."""
        error = NeurevoError("Test error", "TEST_CODE")
        assert error.message == "Test error"
        assert error.error_code == "TEST_CODE"

    def test_config_error_creation(self):
        """Test ConfigError can be created."""
        error = ConfigError("Invalid config")
        assert isinstance(error, NeurevoError)
        assert error.error_code == "CONFIG_ERROR"


class TestMessage:
    """Test Message data structure."""

    def test_message_creation(self):
        """Test Message can be created."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_immutability(self):
        """Test Message is immutable."""
        msg = Message(role="user", content="Hello")
        with pytest.raises(Exception):
            msg.role = "assistant"

    def test_message_empty_content_fails(self):
        """Test empty message content raises error."""
        with pytest.raises(ValueError):
            Message(role="user", content="")

    def test_message_serialization(self):
        """Test Message can be serialized."""
        msg = Message(role="user", content="Hello", metadata={"key": "value"})
        data = msg.to_dict()
        assert data["role"] == "user"
        assert data["content"] == "Hello"

    def test_message_deserialization(self):
        """Test Message can be deserialized."""
        data = {
            "role": "user",
            "content": "Hello",
            "metadata": {"key": "value"},
        }
        msg = Message.from_dict(data)
        assert msg.role == "user"
        assert msg.content == "Hello"


class TestTokenUsage:
    """Test TokenUsage data structure."""

    def test_token_usage_creation(self):
        """Test TokenUsage can be created."""
        usage = TokenUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )
        assert usage.prompt_tokens == 10
        assert usage.total_tokens == 30

    def test_token_usage_validation(self):
        """Test TokenUsage validates token counts."""
        with pytest.raises(ValueError):
            TokenUsage(
                prompt_tokens=10,
                completion_tokens=20,
                total_tokens=25,  # Should be 30
            )


class TestChatResponse:
    """Test ChatResponse data structure."""

    def test_chat_response_creation(self):
        """Test ChatResponse can be created."""
        response = ChatResponse(
            content="Hello",
            model="test-model",
            usage=TokenUsage(10, 20, 30),
            timestamp=datetime.now(),
            provider="bedrock",
        )
        assert response.content == "Hello"
        assert response.model == "test-model"

    def test_chat_response_empty_content_fails(self):
        """Test empty response content raises error."""
        with pytest.raises(ValueError):
            ChatResponse(
                content="",
                model="test-model",
                usage=TokenUsage(0, 0, 0),
                timestamp=datetime.now(),
                provider="bedrock",
            )


class TestHealthStatus:
    """Test HealthStatus data structure."""

    def test_health_status_healthy(self):
        """Test healthy status."""
        status = HealthStatus(
            is_healthy=True,
            latency_ms=100.0,
        )
        assert status.is_healthy is True
        assert status.latency_ms == 100.0

    def test_health_status_unhealthy(self):
        """Test unhealthy status."""
        status = HealthStatus(
            is_healthy=False,
            latency_ms=5000.0,
            error_message="Connection timeout",
        )
        assert status.is_healthy is False
        assert status.error_message is not None


class TestConfig:
    """Test Config class."""

    def test_config_creation_defaults(self):
        """Test Config creation with defaults."""
        config = Config()
        assert config.provider == "bedrock"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_config_creation_with_values(self):
        """Test Config creation with custom values."""
        config = Config(
            provider="bedrock",
            region="us-west-2",
            timeout=60.0,
        )
        assert config.provider == "bedrock"
        assert config.region == "us-west-2"
        assert config.timeout == 60.0

    def test_config_provider_lowercase(self):
        """Test provider name is lowercased."""
        config = Config(provider="BEDROCK")
        assert config.provider == "bedrock"

    def test_config_immutability(self):
        """Test Config is immutable after creation."""
        config = Config()
        with pytest.raises(Exception):
            config.provider = "openai"

    def test_config_serialization(self):
        """Test Config can be serialized."""
        config = Config(provider="bedrock", region="us-east-1")
        data = config.to_dict()
        assert data["provider"] == "bedrock"
        assert data["region"] == "us-east-1"

    def test_config_deserialization(self):
        """Test Config can be deserialized."""
        data = {
            "provider": "bedrock",
            "region": "us-west-2",
        }
        config = Config.from_dict(data)
        assert config.provider == "bedrock"
        assert config.region == "us-west-2"
