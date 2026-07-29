"""Tests for the public Client facade, against a fake in-memory provider.

Exercises Client without touching AWS at all, so these run offline and
verify the orchestration logic (provider resolution, retry, history,
streaming) independently of any real vendor.
"""

from datetime import datetime
from typing import AsyncIterator, List

import pytest

import neuravo
from neuravo import Client, Config
from neuravo.core.exceptions import ValidationError
from neuravo.core.types import ChatResponse, HealthStatus, Message, TokenUsage
from neuravo.providers.base import BaseProvider, ModelInfo
from neuravo.providers.registry import ProviderRegistry


class FakeProvider(BaseProvider):
    """In-memory provider for testing Client without any real network calls."""

    def __init__(self) -> None:
        super().__init__()
        self.initialized = False
        self.closed = False

    async def initialize(self, config: Config) -> None:
        self.initialized = True

    def validate_config(self, config: Config) -> bool:
        return True

    def get_available_models(self) -> List[ModelInfo]:
        return [ModelInfo(id="fake-model", provider="fake")]

    async def chat(self, messages: List[Message]) -> ChatResponse:
        last_user_message = messages[-1].content
        return ChatResponse(
            content=f"echo: {last_user_message}",
            model="fake-model",
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            timestamp=datetime.now(),
            provider="fake",
        )

    async def stream_chat(self, messages: List[Message]) -> AsyncIterator[ChatResponse]:
        for word in ["Hel", "lo"]:
            yield ChatResponse(
                content=word,
                model="fake-model",
                usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                timestamp=datetime.now(),
                provider="fake",
            )

    async def health_check(self) -> HealthStatus:
        return HealthStatus(is_healthy=True, latency_ms=1.0)

    async def close(self) -> None:
        self.closed = True


@pytest.fixture(autouse=True)
def register_fake_provider():
    if not ProviderRegistry.is_available("fake"):
        ProviderRegistry.register("fake", FakeProvider)
    yield
    if ProviderRegistry.is_available("fake"):
        ProviderRegistry.unregister("fake")


@pytest.mark.asyncio
async def test_chat_returns_response_and_records_history():
    client = Client(Config(provider="fake", region="us-east-1"))

    response = await client.chat("Hi there")

    assert response.content == "echo: Hi there"
    history = await client.get_chat_history()
    assert [m.role for m in history] == ["user", "assistant"]
    assert history[0].content == "Hi there"
    assert history[1].content == "echo: Hi there"


@pytest.mark.asyncio
async def test_chat_rejects_empty_prompt():
    client = Client(Config(provider="fake", region="us-east-1"))
    with pytest.raises(ValidationError):
        await client.chat("")


@pytest.mark.asyncio
async def test_stream_yields_chunks_and_records_full_reply():
    client = Client(Config(provider="fake", region="us-east-1"))

    collected = [chunk.content async for chunk in client.stream("Tell me a story")]

    assert collected == ["Hel", "lo"]
    history = await client.get_chat_history()
    assert history[1].content == "Hello"


@pytest.mark.asyncio
async def test_clear_history_empties_conversation():
    client = Client(Config(provider="fake", region="us-east-1"))
    await client.chat("Hi")

    await client.clear_history()

    assert await client.get_chat_history() == []


@pytest.mark.asyncio
async def test_health_check_before_init_reports_unhealthy():
    client = Client(Config(provider="fake", region="us-east-1"))
    status = await client.health_check()
    assert status.is_healthy is False


@pytest.mark.asyncio
async def test_health_check_after_use_delegates_to_provider():
    client = Client(Config(provider="fake", region="us-east-1"))
    await client.chat("Hi")

    status = await client.health_check()

    assert status.is_healthy is True


@pytest.mark.asyncio
async def test_close_releases_provider():
    client = Client(Config(provider="fake", region="us-east-1"))
    await client.chat("Hi")
    provider_instance = client._provider

    await client.close()

    assert provider_instance.closed is True
    assert client._provider is None


def test_setup_logging_and_get_logger_are_wired():
    neuravo.setup_logging("DEBUG")
    logger = neuravo.get_logger("test")
    assert logger.name == "neuravo.test"
