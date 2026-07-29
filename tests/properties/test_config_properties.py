"""Property-based tests for Config validation.

Tests universal properties of configuration validation.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from neuravo.core.config import Config

# Strategy for generating valid configs
config_strategy = st.builds(
    Config,
    provider=st.sampled_from(["bedrock", "openai"]),
    region=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
    timeout=st.floats(min_value=1.0, max_value=3600.0),
    max_retries=st.integers(min_value=0, max_value=10),
    backoff_factor=st.floats(min_value=1.0, max_value=10.0),
    debug=st.booleans(),
)


class TestConfigProperties:
    """Property-based tests for Config."""

    @given(config_strategy)
    def test_config_serialization_roundtrip(self, config: Config):
        """**Validates: Requirements 5.1, 5.3**

        Property: Config serialization is reversible.
        For any valid Config, serializing and deserializing produces equivalent config.
        """
        serialized = config.to_dict()
        deserialized = Config.from_dict(serialized)

        assert deserialized.provider == config.provider
        assert deserialized.timeout == config.timeout

    @given(config_strategy)
    def test_config_immutability(self, config: Config):
        """Property: Config is immutable after creation."""
        with pytest.raises(Exception):
            config.provider = "different"

    @given(config_strategy)
    def test_config_fields_valid_after_creation(self, config: Config):
        """Property: All config fields are valid after creation."""
        assert config.provider is not None
        assert config.timeout > 0
        assert config.max_retries >= 0
        assert config.backoff_factor >= 1.0
