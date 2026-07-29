"""Unit tests for configuration module."""

import pytest

from neuravo.core.config import Config


class TestConfigValidation:
    """Test configuration validation."""

    def test_timeout_min_boundary(self):
        """Test minimum timeout value."""
        with pytest.raises(Exception):
            Config(timeout=0.5)

    def test_timeout_max_boundary(self):
        """Test maximum timeout value."""
        with pytest.raises(Exception):
            Config(timeout=4000.0)

    def test_max_retries_boundary(self):
        """Test max_retries boundaries."""
        config = Config(max_retries=0)
        assert config.max_retries == 0

        config = Config(max_retries=10)
        assert config.max_retries == 10

        with pytest.raises(Exception):
            Config(max_retries=11)

    def test_backoff_factor_boundary(self):
        """Test backoff_factor boundaries."""
        config = Config(backoff_factor=1.0)
        assert config.backoff_factor == 1.0

        with pytest.raises(Exception):
            Config(backoff_factor=0.5)

        with pytest.raises(Exception):
            Config(backoff_factor=11.0)

    def test_valid_provider_names(self):
        """Test various valid provider names."""
        for provider in ["bedrock", "openai", "anthropic"]:
            config = Config(provider=provider)
            assert config.provider == provider.lower()

    def test_debug_flag(self):
        """Test debug flag."""
        config = Config(debug=True)
        assert config.debug is True

        config = Config(debug=False)
        assert config.debug is False
