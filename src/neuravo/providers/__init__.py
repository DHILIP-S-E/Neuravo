"""Provider abstraction layer for Neuravo SDK.

This module provides the provider registry and base interfaces that enable
pluggable provider implementations. Providers allow Neuravo to work with
multiple AI services (Bedrock, OpenAI, Anthropic, etc.) through a unified
abstraction.

Provider Registration:
    Providers self-register when imported, making them available for use.
    The registry discovers available providers at runtime.

Example::

    from neuravo.providers.registry import ProviderRegistry

    registry = ProviderRegistry.instance()
    bedrock_provider = registry.get("bedrock")
"""

from neuravo.providers.base import BaseProvider
from neuravo.providers.registry import ProviderRegistry

__all__ = [
    "ProviderRegistry",
    "BaseProvider",
]
