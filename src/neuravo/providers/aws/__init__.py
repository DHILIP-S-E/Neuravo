"""AWS provider family for Neuravo SDK.

Groups all AWS-backed providers (currently Bedrock only). Each provider
module self-registers with the provider registry when imported.
"""

from neuravo.providers.aws.bedrock import BedrockProvider

__all__ = [
    "BedrockProvider",
]

try:
    from neuravo.providers.registry import ProviderRegistry
    ProviderRegistry.register("bedrock", BedrockProvider)
except Exception:
    # Silently fail if registration fails (for testing scenarios)
    pass
