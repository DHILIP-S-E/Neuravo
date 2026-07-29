"""Tests for the OpenAI provider, against a mocked openai SDK client.

There's no official request/response stub tool for the openai SDK (unlike
botocore's Stubber for AWS), so these mock the client's async methods
directly and assert on what OpenAIProvider does with their return values.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import openai
import pytest

from neuravo.core.exceptions import OpenAIError
from neuravo.core.types import Message
from neuravo.providers.openai.chat import ChatHandler, OpenAIConfig, OpenAIProvider


def _config(**overrides):
    return OpenAIConfig(provider="openai", model="gpt-4o-mini", api_key="test-key", **overrides)


def _make_completion(content: str, prompt_tokens=5, completion_tokens=3, total_tokens=8):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        ),
    )


async def _fake_stream(chunks):
    for chunk in chunks:
        yield chunk


@pytest.mark.asyncio
async def test_initialize_creates_client():
    provider = OpenAIProvider()
    await provider.initialize(_config())
    assert provider.client is not None
    await provider.close()


@pytest.mark.asyncio
async def test_chat_returns_response_from_completion():
    provider = OpenAIProvider()
    await provider.initialize(_config())
    provider.client.chat.completions.create = AsyncMock(
        return_value=_make_completion("Hello there!")
    )

    response = await provider.chat([Message(role="user", content="Hi")])

    assert response.content == "Hello there!"
    assert response.usage.total_tokens == 8
    assert response.provider == "openai"


@pytest.mark.asyncio
async def test_chat_wraps_openai_errors():
    provider = OpenAIProvider()
    await provider.initialize(_config())
    provider.client.chat.completions.create = AsyncMock(
        side_effect=openai.APIConnectionError(request=SimpleNamespace())
    )

    with pytest.raises(OpenAIError):
        await provider.chat([Message(role="user", content="Hi")])


@pytest.mark.asyncio
async def test_chat_before_initialize_raises():
    provider = OpenAIProvider()
    with pytest.raises(OpenAIError):
        await provider.chat([Message(role="user", content="Hi")])


@pytest.mark.asyncio
async def test_stream_chat_yields_text_deltas():
    provider = OpenAIProvider()
    await provider.initialize(_config())

    chunks = [
        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Hel"))]),
        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="lo"))]),
        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=None))]),
    ]
    provider.client.chat.completions.create = AsyncMock(return_value=_fake_stream(chunks))

    collected = [
        chunk.content async for chunk in provider.stream_chat([Message(role="user", content="Hi")])
    ]

    assert "".join(collected) == "Hello"


def test_format_messages_keeps_system_role_inline():
    messages = [
        Message(role="system", content="Be concise."),
        Message(role="user", content="Hi"),
    ]
    formatted = ChatHandler.format_messages(messages)

    assert formatted == [
        {"role": "system", "content": "Be concise."},
        {"role": "user", "content": "Hi"},
    ]


@pytest.mark.asyncio
async def test_health_check_before_initialize_reports_unhealthy():
    provider = OpenAIProvider()
    status = await provider.health_check()
    assert status.is_healthy is False


@pytest.mark.asyncio
async def test_health_check_healthy_when_models_list_succeeds():
    provider = OpenAIProvider()
    await provider.initialize(_config())
    provider.client.models.list = AsyncMock(return_value=SimpleNamespace(data=[]))

    status = await provider.health_check()

    assert status.is_healthy is True


def test_get_available_models_returns_curated_catalog():
    provider = OpenAIProvider()
    models = provider.get_available_models()
    ids = {m.id for m in models}
    assert "gpt-4o-mini" in ids
    assert all(m.provider == "openai" for m in models)
