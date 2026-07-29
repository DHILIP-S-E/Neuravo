"""Tests for timeout management."""

import asyncio

import pytest

from neuravo.core.exceptions import TimeoutError as NeuravoTimeoutError
from neuravo.retry.timeout import TimeoutConfig, TimeoutManager


def test_get_timeout_returns_configured_value_per_type():
    manager = TimeoutManager(
        TimeoutConfig(request_timeout=10.0, stream_timeout=60.0, connect_timeout=5.0)
    )
    assert manager._get_timeout("request") == 10.0
    assert manager._get_timeout("stream") == 60.0
    assert manager._get_timeout("connect") == 5.0


def test_get_timeout_falls_back_to_request_for_unknown_type():
    manager = TimeoutManager(TimeoutConfig(request_timeout=10.0))
    assert manager._get_timeout("unknown") == 10.0


@pytest.mark.asyncio
async def test_execute_with_timeout_returns_result_when_fast_enough():
    manager = TimeoutManager(TimeoutConfig(request_timeout=1.0))

    async def fast() -> str:
        return "done"

    assert await manager.execute_with_timeout(fast()) == "done"


@pytest.mark.asyncio
async def test_execute_with_timeout_raises_neuravo_timeout_error():
    manager = TimeoutManager(TimeoutConfig(request_timeout=0.05))

    async def slow() -> str:
        await asyncio.sleep(1.0)
        return "too late"

    with pytest.raises(NeuravoTimeoutError):
        await manager.execute_with_timeout(slow())
