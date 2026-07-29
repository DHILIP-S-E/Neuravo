"""Third-party plugin discovery and loading.

Uses Python's standard entry-points mechanism (`importlib.metadata`) so a
plugin package just declares itself in its own pyproject.toml - Neuravo
never needs to know about it in advance.
"""

from dataclasses import dataclass, field
from importlib.metadata import EntryPoint, entry_points
from typing import Dict, List, Optional, Tuple

from neuravo.providers.registry import ProviderRegistry

ENTRY_POINT_GROUP = "neuravo.plugins"


@dataclass
class PluginLoadResult:
    """Outcome of loading all discovered plugins.

    Attributes:
        loaded: Names of plugins that registered successfully
        failed: Failing plugin name -> error message (a bad plugin doesn't
            prevent the others from loading)
    """

    loaded: List[str] = field(default_factory=list)
    failed: Dict[str, str] = field(default_factory=dict)


def discover_plugin_entry_points() -> Tuple[EntryPoint, ...]:
    """Find every entry point registered under the Neuravo plugin group.

    Returns:
        Discovered entry points (empty if none are installed)
    """
    return tuple(entry_points(group=ENTRY_POINT_GROUP))


def load_plugins(registry: Optional[ProviderRegistry] = None) -> PluginLoadResult:
    """Discover and register every installed plugin.

    Args:
        registry: Registry to register plugins against (defaults to the
            global ProviderRegistry singleton)

    Returns:
        PluginLoadResult listing what loaded and what failed
    """
    target_registry = registry or ProviderRegistry.instance()
    result = PluginLoadResult()

    for entry_point in discover_plugin_entry_points():
        try:
            plugin_factory = entry_point.load()
            plugin = plugin_factory() if isinstance(plugin_factory, type) else plugin_factory
            plugin.register(target_registry)
        except Exception as exc:  # noqa: BLE001 - one bad plugin must not block the rest
            result.failed[entry_point.name] = str(exc)
            continue
        result.loaded.append(entry_point.name)

    return result
