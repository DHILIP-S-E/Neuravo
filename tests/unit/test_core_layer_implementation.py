"""Comprehensive tests for core layer implementation (tasks 2.1-6.1)."""

from datetime import datetime

import pytest

from neuravo.core.config import Config
from neuravo.core.exceptions import (
    BedrockError,
    ConfigError,
    NeurevoError,
    ProviderError,
    ProviderNotFoundError,
    RetryExhaustedError,
    StreamingError,
    TimeoutError,
    ValidationError,
)
from neuravo.core.types import (
    ChatResponse,
    HealthStatus,
    Message,
    TokenUsage,
)
from neuravo.observability.logging import (
    get_logger,
    redact_sensitive_data,
    setup_logging,
)
from neuravo.providers.base import BaseProvider
from neuravo.providers.registry import ProviderRegistry
from neuravo.retry import (
    ExponentialBackoffRetry,
    RetryConfig,
    RetryStrategy,
)


class TestTask21ExceptionHierarchy:
    """Task 2.1: Core exception hierarchy"""

    def test_exception_base_class(self):
        """All exceptions must inherit from NeurevoError."""
        error = NeurevoError("test", "TEST_CODE")
        assert isinstance(error, Exception)
        assert error.error_code == "TEST_CODE"
        assert error.message == "test"

    def test_provider_error_hierarchy(self):
        """Provider errors must inherit from NeurevoError."""
        err = ProviderError("test", "PROVIDER_ERROR")
        assert isinstance(err, NeurevoError)

    def test_bedrock_error_hierarchy(self):
        """BedrockError must inherit from ProviderError."""
        err = BedrockError("test", "BEDROCK_ERROR")
        assert isinstance(err, ProviderError)
        assert isinstance(err, NeurevoError)

    def test_provider_not_found_error(self):
        """ProviderNotFoundError must have message about missing provider."""
        err = ProviderNotFoundError("unknown")
        assert isinstance(err, ProviderError)
        assert "unknown" in str(err).lower()

    def test_config_error_hierarchy(self):
        """ConfigError must inherit from NeurevoError."""
        err = ConfigError("test", "CONFIG_ERROR")
        assert isinstance(err, NeurevoError)

    def test_all_exception_types_have_error_code(self):
        """All exception types must have error_code attribute."""
        exceptions = [
            NeurevoError("msg", "CODE"),
            ProviderError("msg"),
            ConfigError("msg"),
            ValidationError("msg"),
            TimeoutError("msg", 30.0),
            RetryExhaustedError("msg", 3),
            StreamingError("msg"),
        ]
        for exc in exceptions:
            assert hasattr(exc, "error_code")
            assert isinstance(exc.error_code, str)

    def test_all_exception_types_have_message(self):
        """All exception types must have message attribute."""
        exceptions = [
            NeurevoError("msg", "CODE"),
            ProviderError("msg"),
            ConfigError("msg"),
        ]
        for exc in exceptions:
            assert hasattr(exc, "message")
            assert isinstance(exc.message, str)

    def test_exception_string_format(self):
        """Exception string must include error code."""
        err = NeurevoError("test message", "TEST_CODE")
        assert "[TEST_CODE]" in str(err)
        assert "test message" in str(err)

    def test_debug_details_optional(self):
        """Debug details must be optional."""
        err = NeurevoError("msg", "CODE")
        assert err.debug_details == {}

        err2 = NeurevoError("msg", "CODE", {"key": "value"})
        assert err2.debug_details["key"] == "value"


class TestTask31ConfigManagement:
    """Task 3.1: Configuration management"""

    def test_config_creation_with_defaults(self):
        """Config can be created with default values."""
        config = Config()
        assert config.provider == "bedrock"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.backoff_factor == 2.0
        assert config.debug is False

    def test_config_field_validation(self):
        """Config fields must be validated on creation."""
        # Valid config
        config = Config(timeout=60.0, max_retries=5)
        assert config.timeout == 60.0
        assert config.max_retries == 5

        # Invalid timeout (too small)
        with pytest.raises(Exception):
            Config(timeout=0.5)

        # Invalid timeout (too large)
        with pytest.raises(Exception):
            Config(timeout=4000.0)

        # Invalid max_retries
        with pytest.raises(Exception):
            Config(max_retries=11)

        # Invalid backoff_factor
        with pytest.raises(Exception):
            Config(backoff_factor=0.5)

    def test_config_provider_lowercase(self):
        """Provider name must be lowercased."""
        config = Config(provider="BEDROCK")
        assert config.provider == "bedrock"

        config = Config(provider="OpenAI")
        assert config.provider == "openai"

    def test_config_immutability(self):
        """Config must be immutable after creation."""
        config = Config()
        with pytest.raises(Exception):
            config.provider = "openai"

    def test_config_serialization(self):
        """Config must serialize to dictionary."""
        config = Config(provider="bedrock", region="us-east-1", debug=True)
        data = config.to_dict()

        assert isinstance(data, dict)
        assert data["provider"] == "bedrock"
        assert data["region"] == "us-east-1"
        assert data["debug"] is True
        assert data["timeout"] == 30.0

    def test_config_deserialization(self):
        """Config must deserialize from dictionary."""
        data = {
            "provider": "bedrock",
            "region": "us-west-2",
            "timeout": 45.0,
            "debug": True,
        }
        config = Config.from_dict(data)

        assert config.provider == "bedrock"
        assert config.region == "us-west-2"
        assert config.timeout == 45.0
        assert config.debug is True

    def test_config_roundtrip(self):
        """Config must survive serialization roundtrip."""
        original = Config(
            provider="bedrock",
            region="us-west-2",
            timeout=45.0,
            max_retries=5,
            debug=True,
        )
        serialized = original.to_dict()
        restored = Config.from_dict(serialized)

        assert restored.provider == original.provider
        assert restored.region == original.region
        assert restored.timeout == original.timeout
        assert restored.max_retries == original.max_retries
        assert restored.debug == original.debug

    def test_config_all_fields_typed(self):
        """All Config fields must be properly typed."""
        config = Config()
        assert isinstance(config.provider, str)
        assert isinstance(config.timeout, float)
        assert isinstance(config.max_retries, int)
        assert isinstance(config.backoff_factor, float)
        assert isinstance(config.debug, bool)


class TestTask41LoggingInfrastructure:
    """Task 4.1: Logging infrastructure"""

    def test_setup_logging_with_default_level(self):
        """setup_logging must work with default level."""
        setup_logging()  # Should not raise

    def test_setup_logging_with_custom_level(self):
        """setup_logging must accept custom log levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            setup_logging(level)  # Should not raise

    def test_setup_logging_invalid_level(self):
        """setup_logging must reject invalid log levels."""
        with pytest.raises(ValueError):
            setup_logging("INVALID_LEVEL")

    def test_get_logger(self):
        """get_logger must return logger with correct name."""
        logger = get_logger("test")
        assert "neuravo" in logger.name

    def test_get_logger_full_name_already_prefixed(self):
        """get_logger must not double-prefix names."""
        logger = get_logger("neuravo.test")
        assert logger.name == "neuravo.test"

    def test_redact_sensitive_data_api_key(self):
        """redact_sensitive_data must redact API keys."""
        text = "api_key=sk-1234567890abcdef"
        redacted = redact_sensitive_data(text)
        assert "[REDACTED]" in redacted
        assert "sk-1234567890abcdef" not in redacted

    def test_redact_sensitive_data_password(self):
        """redact_sensitive_data must redact passwords."""
        text = "password=mysecretpassword123"
        redacted = redact_sensitive_data(text)
        assert "[REDACTED]" in redacted
        assert "mysecretpassword123" not in redacted

    def test_redact_sensitive_data_aws_keys(self):
        """redact_sensitive_data must redact AWS credentials."""
        text = "aws_access_key=AKIAIOSFODNN7EXAMPLE"
        redacted = redact_sensitive_data(text)
        assert "[REDACTED]" in redacted

    def test_redact_sensitive_data_preserves_normal_text(self):
        """redact_sensitive_data must preserve normal text."""
        text = "This is a normal log message with no secrets"
        redacted = redact_sensitive_data(text)
        assert redacted == text

    def test_redact_sensitive_data_multiple_patterns(self):
        """redact_sensitive_data must handle multiple patterns."""
        text = "api_key=abc123 and password=xyz789"
        redacted = redact_sensitive_data(text)
        assert redacted.count("[REDACTED]") == 2


class TestTask51RetryStrategy:
    """Task 5.1: Retry strategy infrastructure"""

    def test_retry_config_defaults(self):
        """RetryConfig must have sensible defaults."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.backoff_factor == 2.0
        assert config.base_wait == 1.0
        assert config.max_wait == 60.0
        assert config.jitter is True

    def test_retry_strategy_is_abstract(self):
        """RetryStrategy must be abstract."""
        with pytest.raises(TypeError):
            RetryStrategy()

    def test_exponential_backoff_retry_creation(self):
        """ExponentialBackoffRetry can be instantiated."""
        config = RetryConfig()
        strategy = ExponentialBackoffRetry(config)
        assert strategy.config == config

    @pytest.mark.asyncio
    async def test_exponential_backoff_success_on_first_try(self):
        """ExponentialBackoffRetry must succeed on first try if func succeeds."""
        config = RetryConfig(max_retries=3)
        strategy = ExponentialBackoffRetry(config)

        async def always_succeeds():
            return "success"

        result = await strategy.execute(always_succeeds)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_exponential_backoff_with_sync_function(self):
        """ExponentialBackoffRetry must handle sync functions."""
        config = RetryConfig(max_retries=1)
        strategy = ExponentialBackoffRetry(config)

        def sync_func():
            return "sync_success"

        result = await strategy.execute(sync_func)
        assert result == "sync_success"

    @pytest.mark.asyncio
    async def test_exponential_backoff_retries_on_retryable_error(self):
        """ExponentialBackoffRetry must retry on retryable errors."""
        config = RetryConfig(
            max_retries=2,
            base_wait=0.01,
            backoff_factor=1.5,
        )
        strategy = ExponentialBackoffRetry(config)

        attempts = [0]

        async def fails_once():
            attempts[0] += 1
            if attempts[0] < 2:
                raise TimeoutError("Temporary timeout")
            return "success"

        result = await strategy.execute(fails_once)
        assert result == "success"
        assert attempts[0] == 2

    def test_calculate_wait_exponential(self):
        """_calculate_wait must implement exponential backoff."""
        config = RetryConfig(
            base_wait=1.0,
            backoff_factor=2.0,
            max_wait=60.0,
            jitter=False,
        )
        strategy = ExponentialBackoffRetry(config)

        wait_0 = strategy._calculate_wait(0)
        wait_1 = strategy._calculate_wait(1)
        wait_2 = strategy._calculate_wait(2)

        # Exponential: 1.0, 2.0, 4.0
        assert wait_0 == 1.0
        assert wait_1 == 2.0
        assert wait_2 == 4.0

    def test_calculate_wait_capped_at_max(self):
        """_calculate_wait must cap at max_wait."""
        config = RetryConfig(
            base_wait=1.0,
            backoff_factor=10.0,
            max_wait=10.0,
            jitter=False,
        )
        strategy = ExponentialBackoffRetry(config)

        wait = strategy._calculate_wait(5)
        assert wait <= 10.0

    def test_calculate_wait_with_jitter(self):
        """_calculate_wait with jitter must produce varied results."""
        config = RetryConfig(
            base_wait=1.0,
            backoff_factor=2.0,
            jitter=True,
        )
        strategy = ExponentialBackoffRetry(config)

        waits = [strategy._calculate_wait(1) for _ in range(10)]
        base = config.base_wait * (config.backoff_factor**1)

        # All should be between 50% and 100% of base
        for wait in waits:
            assert wait >= base * 0.5
            assert wait <= base * 1.0

    def test_is_retryable_timeout_error(self):
        """_is_retryable must identify timeout errors."""
        assert ExponentialBackoffRetry._is_retryable(TimeoutError("timeout"))

    def test_is_retryable_throttling_error(self):
        """_is_retryable must identify throttling errors."""
        error = Exception("ThrottlingException")
        assert ExponentialBackoffRetry._is_retryable(error)

    def test_is_retryable_service_unavailable(self):
        """_is_retryable must identify service unavailable errors."""
        error = Exception("ServiceUnavailableException")
        assert ExponentialBackoffRetry._is_retryable(error)

    def test_is_not_retryable_auth_error(self):
        """_is_retryable must not retry auth errors."""
        error = Exception("AuthenticationError")
        assert not ExponentialBackoffRetry._is_retryable(error)


class TestTask61ProviderRegistry:
    """Task 6.1: Provider registry"""

    def test_registry_singleton(self):
        """ProviderRegistry must be singleton."""
        registry1 = ProviderRegistry.instance()
        registry2 = ProviderRegistry.instance()
        assert registry1 is registry2

    def test_registry_register_provider(self):
        """ProviderRegistry must register providers."""

        class TestProvider(BaseProvider):
            async def initialize(self, config):
                pass

            def validate_config(self, config):
                return True

            def get_available_models(self):
                return []

            async def health_check(self):
                pass

            async def close(self):
                pass

            async def chat(self, messages):
                pass

            async def stream_chat(self, messages):
                pass

        registry = ProviderRegistry.instance()
        registry.register("test_provider", TestProvider)
        assert registry.is_available("test_provider")

    def test_registry_get_provider(self):
        """ProviderRegistry must retrieve registered providers."""

        class TestProvider(BaseProvider):
            async def initialize(self, config):
                pass

            def validate_config(self, config):
                return True

            def get_available_models(self):
                return []

            async def health_check(self):
                pass

            async def close(self):
                pass

            async def chat(self, messages):
                pass

            async def stream_chat(self, messages):
                pass

        registry = ProviderRegistry.instance()
        registry.register("get_test", TestProvider)

        provider = registry.get("get_test")
        assert isinstance(provider, TestProvider)

    def test_registry_not_found(self):
        """ProviderRegistry must raise error for unknown provider."""
        registry = ProviderRegistry.instance()
        with pytest.raises(ProviderNotFoundError):
            registry.get("nonexistent_provider_xyz")

    def test_registry_list_available(self):
        """ProviderRegistry must list available providers."""

        class Provider1(BaseProvider):
            async def initialize(self, config):
                pass

            def validate_config(self, config):
                return True

            def get_available_models(self):
                return []

            async def health_check(self):
                pass

            async def close(self):
                pass

            async def chat(self, messages):
                pass

            async def stream_chat(self, messages):
                pass

        registry = ProviderRegistry.instance()
        registry.register("list_test_1", Provider1)
        registry.register("list_test_2", Provider1)

        available = registry.list_available()
        assert isinstance(available, list)
        assert "list_test_1" in available
        assert "list_test_2" in available

    def test_registry_duplicate_registration(self):
        """ProviderRegistry must prevent duplicate registration."""

        class TestProvider(BaseProvider):
            async def initialize(self, config):
                pass

            def validate_config(self, config):
                return True

            def get_available_models(self):
                return []

            async def health_check(self):
                pass

            async def close(self):
                pass

            async def chat(self, messages):
                pass

            async def stream_chat(self, messages):
                pass

        registry = ProviderRegistry.instance()
        registry.register("dup_test", TestProvider)

        with pytest.raises(ProviderError):
            registry.register("dup_test", TestProvider)


class TestCoreTypesIntegration:
    """Integration tests for core types (Task 6.1)"""

    def test_token_usage_validation(self):
        """TokenUsage must validate token counts."""
        # Valid
        usage = TokenUsage(10, 20, 30)
        assert usage.total_tokens == 30

        # Invalid - total mismatch
        with pytest.raises(ValueError):
            TokenUsage(10, 20, 25)

        # Invalid - negative tokens
        with pytest.raises(ValueError):
            TokenUsage(-1, 20, 19)

    def test_message_immutability(self):
        """Message must be immutable."""
        msg = Message(role="user", content="Hello")
        with pytest.raises(Exception):
            msg.role = "assistant"

    def test_message_empty_content_rejected(self):
        """Message must reject empty content."""
        with pytest.raises(ValueError):
            Message(role="user", content="")

    def test_chat_response_all_fields_present(self):
        """ChatResponse must have all required fields."""
        response = ChatResponse(
            content="Hello",
            model="test-model",
            usage=TokenUsage(10, 20, 30),
            timestamp=datetime.now(),
            provider="bedrock",
        )

        assert response.content is not None
        assert response.model is not None
        assert response.usage is not None
        assert response.timestamp is not None
        assert response.provider is not None

    def test_health_status_validation(self):
        """HealthStatus must validate combinations."""
        # Valid - healthy without error
        status = HealthStatus(is_healthy=True, latency_ms=100.0)
        assert status.is_healthy is True

        # Invalid - healthy with error
        with pytest.raises(ValueError):
            HealthStatus(
                is_healthy=True,
                latency_ms=100.0,
                error_message="Error",
            )

        # Valid - unhealthy with error
        status2 = HealthStatus(
            is_healthy=False,
            latency_ms=5000.0,
            error_message="Connection failed",
        )
        assert status2.is_healthy is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
