"""Tests for the Bedrock provider against realistic mocked AWS responses.

Uses botocore's Stubber rather than raw mocks so the request/response
shapes are validated against the actual bedrock-runtime service model.
"""

import pytest
from botocore.stub import Stubber

from neuravo.core.config import Config
from neuravo.core.exceptions import BedrockError, MissingConfigError
from neuravo.core.types import Message
from neuravo.providers.aws.bedrock import (
    BedrockProvider,
    ChatHandler,
    StreamingHandler,
)


@pytest.mark.asyncio
async def test_initialize_rejects_missing_region():
    provider = BedrockProvider()
    with pytest.raises(MissingConfigError):
        await provider.initialize(Config(provider="bedrock", region=None))


@pytest.mark.asyncio
async def test_chat_returns_response_from_converse():
    provider = BedrockProvider()
    await provider.initialize(
        Config(provider="bedrock", region="us-east-1", model="anthropic.claude-3-haiku-20240307-v1:0")
    )

    stubber = Stubber(provider.client)
    stubber.add_response(
        "converse",
        {
            "output": {"message": {"role": "assistant", "content": [{"text": "Hello there!"}]}},
            "usage": {"inputTokens": 5, "outputTokens": 3, "totalTokens": 8},
            "stopReason": "end_turn",
            "metrics": {"latencyMs": 123},
        },
        {
            "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
            "messages": [{"role": "user", "content": [{"text": "Hi"}]}],
        },
    )
    stubber.activate()

    response = await provider.chat([Message(role="user", content="Hi")])

    assert response.content == "Hello there!"
    assert response.usage.total_tokens == 8
    assert response.provider == "bedrock"
    stubber.deactivate()
    stubber.assert_no_pending_responses()


@pytest.mark.asyncio
async def test_chat_wraps_client_errors_as_bedrock_error():
    provider = BedrockProvider()
    await provider.initialize(Config(provider="bedrock", region="us-east-1"))

    stubber = Stubber(provider.client)
    stubber.add_client_error("converse", service_error_code="ThrottlingException")
    stubber.activate()

    with pytest.raises(BedrockError):
        await provider.chat([Message(role="user", content="Hi")])

    stubber.deactivate()


@pytest.mark.asyncio
async def test_health_check_reports_unhealthy_before_initialize():
    provider = BedrockProvider()
    status = await provider.health_check()
    assert status.is_healthy is False


@pytest.mark.asyncio
async def test_health_check_healthy_when_control_plane_responds():
    provider = BedrockProvider()
    await provider.initialize(Config(provider="bedrock", region="us-east-1"))

    stubber = Stubber(provider._control_client)
    stubber.add_response("list_foundation_models", {"modelSummaries": []}, {})
    stubber.activate()

    status = await provider.health_check()

    assert status.is_healthy is True
    stubber.deactivate()


def test_format_messages_splits_system_prompt():
    messages = [
        Message(role="system", content="Be concise."),
        Message(role="user", content="Hi"),
    ]
    turns, system_blocks = ChatHandler.format_messages(messages)

    assert turns == [{"role": "user", "content": [{"text": "Hi"}]}]
    assert system_blocks == [{"text": "Be concise."}]


def test_parse_response_extracts_text_and_usage():
    response = {
        "output": {"message": {"content": [{"text": "42"}]}},
        "usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2},
    }
    text, usage = ChatHandler.parse_response(response)

    assert text == "42"
    assert usage.total_tokens == 2


@pytest.mark.asyncio
async def test_streaming_handler_yields_text_deltas():
    events = [
        {"contentBlockDelta": {"delta": {"text": "Hel"}}},
        {"contentBlockDelta": {"delta": {"text": "lo"}}},
        {"metadata": {"usage": {"inputTokens": 2, "outputTokens": 2, "totalTokens": 4}}},
    ]

    chunks = [
        chunk
        async for chunk in StreamingHandler.handle_stream({"stream": events}, model="test-model")
    ]

    # The trailing "metadata" (usage-only) event carries no text and isn't
    # surfaced as a chunk - ChatResponse requires non-empty content.
    assert "".join(c.content for c in chunks) == "Hello"
    assert all(c.metadata.get("chunk") for c in chunks)
