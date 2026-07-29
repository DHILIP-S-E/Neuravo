"""Integration tests for provider registry."""

import pytest

from neuravo.core.exceptions import ProviderNotFoundError
from neuravo.providers.base import BaseProvider
from neuravo.providers.registry import ProviderRegistry


class DummyProvider(BaseProvider):
    """Dummy provider for testing."""

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


class TestProviderRegistry:
    """Test provider registry functionality."""

    def test_registry_singleton(self):
        """Test registry is singleton."""
        registry1 = ProviderRegistry.instance()
        registry2 = ProviderRegistry.instance()
        assert registry1 is registry2

    def test_register_provider(self):
        """Test registering a provider."""
        registry = ProviderRegistry()
        registry.register("dummy", DummyProvider)
        assert registry.is_available("dummy")

    def test_get_provider(self):
        """Test getting a registered provider."""
        registry = ProviderRegistry()
        registry.unregister("dummy")  # Clean up first
        registry.register("dummy", DummyProvider)
        provider = registry.get("dummy")
        assert isinstance(provider, DummyProvider)

    def test_get_nonexistent_provider(self):
        """Test getting non-existent provider raises error."""
        registry = ProviderRegistry()
        with pytest.raises(ProviderNotFoundError):
            registry.get("nonexistent")

    def test_list_available_providers(self):
        """Test listing available providers."""
        registry = ProviderRegistry()
        providers = registry.list_available()
        assert isinstance(providers, list)
