"""OpenAI provider for Neuravo SDK.

Requires the optional `openai` dependency: `pip install neuravo[openai]`.
Self-registers with ProviderRegistry when imported.
"""

try:
    from neuravo.providers.openai.chat import OpenAIProvider

    __all__ = ["OpenAIProvider"]

    from neuravo.providers.registry import ProviderRegistry

    ProviderRegistry.register("openai", OpenAIProvider)
except ImportError:
    # openai package not installed - this provider is simply unavailable
    # until `pip install neuravo[openai]` is run.
    __all__ = []
except Exception:
    # Registration failure (e.g. re-import in tests) - non-fatal.
    pass
