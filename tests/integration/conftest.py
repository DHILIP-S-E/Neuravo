"""Integration test fixtures and configuration.

Provides fixtures for integration tests with mocked AWS responses.
"""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_bedrock_client():
    """Provide mocked Bedrock boto3 client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def mock_bedrock_response():
    """Provide sample Bedrock API response."""
    return {
        "contentBlocks": [
            {
                "type": "text",
                "text": "Hello! I'm Claude, an AI assistant made by Anthropic.",
            }
        ],
        "usage": {
            "inputTokens": 10,
            "outputTokens": 20,
        },
        "stopReason": "end_turn",
    }


@pytest.fixture
def mock_bedrock_streaming_response():
    """Provide sample Bedrock streaming response."""

    async def stream_response():
        yield {
            "type": "content_block_delta",
            "delta": {"type": "text_delta", "text": "Hello"},
        }
        yield {
            "type": "content_block_delta",
            "delta": {"type": "text_delta", "text": " from"},
        }
        yield {
            "type": "content_block_delta",
            "delta": {"type": "text_delta", "text": " Claude!"},
        }

    return stream_response()
