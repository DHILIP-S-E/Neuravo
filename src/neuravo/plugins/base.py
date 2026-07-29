"""The plugin contract.

A Protocol, not an ABC: a third-party plugin package satisfies this by
having the right shape, not by inheriting from a base class this repo
ships - the same reasoning as `core`'s provider ports.
"""

from typing import Protocol, runtime_checkable

from neuravo.providers.registry import ProviderRegistry


@runtime_checkable
class PluginProtocol(Protocol):
    """What a Neuravo plugin must implement.

    Examples:
        A plugin registering a custom provider::

            class MyPlugin:
                def register(self, registry: ProviderRegistry) -> None:
                    registry.register("my-provider", MyProvider)

            # In the plugin package's pyproject.toml:
            # [project.entry-points."neuravo.plugins"]
            # my_plugin = "my_package.plugin:MyPlugin"
    """

    def register(self, registry: ProviderRegistry) -> None:
        """Register this plugin's capabilities.

        Args:
            registry: The provider registry to register against
        """
        ...
