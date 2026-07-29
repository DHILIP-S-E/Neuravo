"""Tests for plugin discovery and loading, against fake entry points."""

from types import SimpleNamespace

from neuravo.plugins import PluginProtocol, load_plugins
from neuravo.providers.base import BaseProvider
from neuravo.providers.registry import ProviderRegistry


class _FakeProvider(BaseProvider):
    async def initialize(self, config):
        pass

    def validate_config(self, config):
        return True

    def get_available_models(self):
        return []

    async def chat(self, messages):
        pass

    async def stream_chat(self, messages):
        pass

    async def health_check(self):
        pass

    async def close(self):
        pass


class _WorkingPlugin:
    def register(self, registry: ProviderRegistry) -> None:
        registry.register("plugin-provider", _FakeProvider)


class _BrokenPlugin:
    def register(self, registry: ProviderRegistry) -> None:
        raise RuntimeError("plugin is broken")


def _fake_entry_point(name, factory):
    return SimpleNamespace(name=name, load=lambda: factory)


def test_working_plugin_registers_provider(monkeypatch):
    registry = ProviderRegistry.instance()
    if registry.is_available("plugin-provider"):
        registry.unregister("plugin-provider")

    monkeypatch.setattr(
        "neuravo.plugins.loader.entry_points",
        lambda group: [_fake_entry_point("working", _WorkingPlugin)],
    )

    result = load_plugins(registry)

    assert result.loaded == ["working"]
    assert result.failed == {}
    assert registry.is_available("plugin-provider")
    registry.unregister("plugin-provider")


def test_broken_plugin_is_recorded_as_failed_without_blocking_others(monkeypatch):
    registry = ProviderRegistry.instance()
    if registry.is_available("plugin-provider"):
        registry.unregister("plugin-provider")

    monkeypatch.setattr(
        "neuravo.plugins.loader.entry_points",
        lambda group: [
            _fake_entry_point("broken", _BrokenPlugin),
            _fake_entry_point("working", _WorkingPlugin),
        ],
    )

    result = load_plugins(registry)

    assert result.loaded == ["working"]
    assert "broken" in result.failed
    assert "plugin is broken" in result.failed["broken"]
    registry.unregister("plugin-provider")


def test_no_installed_plugins_returns_empty_result(monkeypatch):
    monkeypatch.setattr("neuravo.plugins.loader.entry_points", lambda group: [])

    result = load_plugins()

    assert result.loaded == []
    assert result.failed == {}


def test_fake_provider_satisfies_plugin_protocol_via_working_plugin():
    assert isinstance(_WorkingPlugin(), PluginProtocol)
