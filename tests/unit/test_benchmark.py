"""Tests for the benchmark runner, against a fake client (no AWS calls)."""

import asyncio
from datetime import datetime
from typing import AsyncIterator, List

import pytest

from neuravo.benchmark import run_benchmark
from neuravo.core.client import BaseClient
from neuravo.core.config import Config
from neuravo.core.types import ChatResponse, HealthStatus, Message, TokenUsage


class DelayedClient(BaseClient):
    """Fake client that sleeps a fixed amount per call and can be made to fail."""

    def __init__(self, config: Config, delay_seconds: float = 0.0, fail_every: int = 0):
        super().__init__(config)
        self.delay_seconds = delay_seconds
        self.fail_every = fail_every
        self.call_count = 0

    async def initialize(self) -> None:
        pass

    async def chat(self, prompt: str) -> ChatResponse:
        self.call_count += 1
        if self.fail_every and self.call_count % self.fail_every == 0:
            raise RuntimeError(f"simulated failure on call {self.call_count}")
        await asyncio.sleep(self.delay_seconds)
        return ChatResponse(
            content="ok",
            model="fake-model",
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            timestamp=datetime.now(),
            provider="fake",
        )

    async def stream(self, prompt: str) -> AsyncIterator[ChatResponse]:
        yield await self.chat(prompt)

    async def get_chat_history(self) -> List[Message]:
        return []

    async def clear_history(self) -> None:
        pass

    async def health_check(self) -> HealthStatus:
        return HealthStatus(is_healthy=True, latency_ms=0.0)

    async def close(self) -> None:
        pass


def _client(**kwargs):
    return DelayedClient(Config(provider="fake", region="us-east-1"), **kwargs)


@pytest.mark.asyncio
async def test_run_benchmark_records_latency_for_every_success():
    result = await run_benchmark(_client(delay_seconds=0.01), "Hello", n=5)

    assert result.total_runs == 5
    assert result.successes == 5
    assert result.failures == 0
    assert len(result.latencies_ms) == 5
    assert all(ms >= 10 for ms in result.latencies_ms)


@pytest.mark.asyncio
async def test_run_benchmark_records_failures_without_aborting():
    result = await run_benchmark(_client(fail_every=2), "Hello", n=4)

    assert result.total_runs == 4
    assert result.successes == 2
    assert result.failures == 2
    assert len(result.errors) == 2


@pytest.mark.asyncio
async def test_mean_and_percentile_latency():
    result = await run_benchmark(_client(delay_seconds=0.0), "Hello", n=3)

    assert result.mean_latency_ms >= 0.0
    assert result.percentile_latency_ms(95) >= 0.0


@pytest.mark.asyncio
async def test_all_failures_gives_zero_latency_stats():
    result = await run_benchmark(_client(fail_every=1), "Hello", n=3)

    assert result.successes == 0
    assert result.failures == 3
    assert result.mean_latency_ms == 0.0
