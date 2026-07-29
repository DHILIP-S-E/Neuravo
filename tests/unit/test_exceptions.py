"""Unit tests for exception classes."""

from neuravo.core.exceptions import (
    ConfigError,
    NeurevoError,
    ProviderError,
)


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_provider_error_is_neuravo_error(self):
        """Test ProviderError inherits from NeurevoError."""
        error = ProviderError("Test error")
        assert isinstance(error, NeurevoError)

    def test_config_error_is_neuravo_error(self):
        """Test ConfigError inherits from NeurevoError."""
        error = ConfigError("Test error")
        assert isinstance(error, NeurevoError)

    def test_exception_string_representation(self):
        """Test exception string formatting."""
        error = NeurevoError("Test message", "TEST_CODE")
        assert "[TEST_CODE]" in str(error)
        assert "Test message" in str(error)
