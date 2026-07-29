"""Provider registry for runtime discovery and instantiation.

The registry maintains a mapping of provider names to provider classes,
allowing providers to be discovered and instantiated at runtime without
modification to the core SDK code.
"""

from typing import Dict, List, Optional, Type

from neuravo.core.exceptions import ProviderError, ProviderNotFoundError
from neuravo.providers.base import BaseProvider


class ProviderRegistry:
    """Registry for managing available providers.

    Implements the singleton pattern to provide a single point of access
    for provider discovery and instantiation.

    Examples:
        Get available providers::

            registry = ProviderRegistry.instance()
            providers = registry.list_available()
            print(f"Available: {providers}")

        Register custom provider::

            class MyProvider(BaseProvider):
                pass

            registry.register("myprovider", MyProvider)

        Get provider instance::

            provider = registry.get("bedrock")
    """

    _instance: Optional["ProviderRegistry"] = None
    _providers: Dict[str, Type[BaseProvider]] = {}

    def __new__(cls) -> "ProviderRegistry":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def instance(cls) -> "ProviderRegistry":
        """Get singleton instance of provider registry.

        Returns:
            ProviderRegistry instance
        """
        return cls()

    @classmethod
    def register(cls, name: str, provider_class: Type[BaseProvider]) -> None:
        """Register a provider implementation.

        Args:
            name: Provider name (lowercase, no spaces)
            provider_class: Provider class implementing BaseProvider

        Raises:
            ProviderError: If provider is already registered
            TypeError: If provider_class doesn't inherit from BaseProvider

        Examples:
            Register provider::

                class CustomProvider(BaseProvider):
                    pass

                ProviderRegistry.register("custom", CustomProvider)
        """
        if not issubclass(provider_class, BaseProvider):
            raise TypeError(
                f"{provider_class} must inherit from BaseProvider"
            )

        name_lower = name.lower()

        if name_lower in cls._providers:
            raise ProviderError(
                f"Provider '{name_lower}' is already registered"
            )

        cls._providers[name_lower] = provider_class

    @classmethod
    def get(cls, name: str) -> BaseProvider:
        """Get provider instance by name.

        Args:
            name: Provider name to retrieve

        Returns:
            Instance of the requested provider

        Raises:
            ProviderNotFoundError: If provider is not registered

        Examples:
            Get provider::

                provider = ProviderRegistry.get("bedrock")
        """
        name_lower = name.lower()

        if name_lower not in cls._providers:
            available = list(cls._providers.keys())
            raise ProviderNotFoundError(
                name_lower,
                debug_details={
                    "available_providers": available,
                },
            )

        provider_class = cls._providers[name_lower]
        return provider_class()

    @classmethod
    def list_available(cls) -> List[str]:
        """Get list of available provider names.

        Returns:
            List of registered provider names (sorted)

        Examples:
            List providers::

                providers = ProviderRegistry.list_available()
                print(f"Available: {providers}")
        """
        return sorted(cls._providers.keys())

    @classmethod
    def is_available(cls, name: str) -> bool:
        """Check if a provider is registered.

        Args:
            name: Provider name to check

        Returns:
            True if provider is registered, False otherwise
        """
        return name.lower() in cls._providers

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a provider (for testing only).

        Args:
            name: Provider name to unregister

        Raises:
            ProviderNotFoundError: If provider is not registered
        """
        name_lower = name.lower()
        if name_lower not in cls._providers:
            raise ProviderNotFoundError(name_lower)
        del cls._providers[name_lower]
