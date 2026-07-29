"""Plugin system for Neuravo SDK.

Third-party packages register new providers (or other capabilities) via
Python entry points, without Neuravo needing to know about them in advance.

Examples:
    Load every installed plugin at startup::

        from neuravo.plugins import load_plugins

        result = load_plugins()
        print(f"loaded: {result.loaded}, failed: {result.failed}")
"""

from neuravo.plugins.base import PluginProtocol
from neuravo.plugins.loader import PluginLoadResult, load_plugins

__all__ = [
    "PluginProtocol",
    "PluginLoadResult",
    "load_plugins",
]
