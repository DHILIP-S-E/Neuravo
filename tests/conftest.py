"""Pytest configuration and shared fixtures.

Provides fixtures for testing Neuravo SDK components, including:
- Mock AWS Bedrock responses
- Test configurations
- Test clients
"""


import pytest
import pytest_asyncio


@pytest.fixture
def mock_aws_credentials(monkeypatch):
    """Provide mock AWS credentials."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")


@pytest.fixture
def sample_config():
    """Provide sample configuration for testing."""
    from neuravo.core.config import Config

    return Config(
        provider="bedrock",
        region="us-east-1",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
    )


@pytest.fixture
def sample_message():
    """Provide sample message for testing."""
    from neuravo.core.types import Message

    return Message(role="user", content="Hello, world!")


@pytest.fixture
def sample_response():
    """Provide sample chat response for testing."""
    from datetime import datetime

    from neuravo.core.types import ChatResponse, TokenUsage

    return ChatResponse(
        content="Hello! How can I help you?",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        usage=TokenUsage(
            prompt_tokens=10,
            completion_tokens=12,
            total_tokens=22,
        ),
        timestamp=datetime.now(),
        provider="bedrock",
    )


@pytest_asyncio.fixture
async def async_client(sample_config):
    """Provide async client for testing."""
    from neuravo import Client

    client = Client(sample_config)
    yield client
    # Cleanup


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for pytest-asyncio."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
