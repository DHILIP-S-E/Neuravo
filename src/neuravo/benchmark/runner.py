"""Latency benchmarking for client chat calls."""

import time
from dataclasses import dataclass, field
from typing import List

from neuravo.core.client import BaseClient
from neuravo.observability.metrics import Histogram


@dataclass
class BenchmarkResult:
    """Outcome of a benchmark run.

    Attributes:
        total_runs: Number of calls attempted
        successes: Number of calls that completed without raising
        failures: Number of calls that raised
        errors: Error messages from failed calls, in the order they occurred
        latencies_ms: Per-call latency in milliseconds, successes only
    """

    total_runs: int = 0
    successes: int = 0
    failures: int = 0
    errors: List[str] = field(default_factory=list)
    latencies_ms: List[float] = field(default_factory=list)

    def _histogram(self) -> Histogram:
        hist = Histogram("benchmark_latency_ms")
        for value in self.latencies_ms:
            hist.observe(value)
        return hist

    @property
    def mean_latency_ms(self) -> float:
        """Mean latency across successful calls.

        Returns:
            Mean latency in milliseconds, or 0.0 if there were no successes
        """
        return self._histogram().mean()

    def percentile_latency_ms(self, p: float) -> float:
        """Latency at a given percentile across successful calls.

        Args:
            p: Percentile in [0, 100]

        Returns:
            Latency in milliseconds at that percentile, or 0.0 if there
            were no successes
        """
        return self._histogram().percentile(p)


async def run_benchmark(client: BaseClient, prompt: str, n: int = 10) -> BenchmarkResult:
    """Send the same prompt through a client `n` times and measure latency.

    Runs are sequential (not concurrent) so each call's latency reflects
    the client alone, not contention between simultaneous requests. A
    failing call is recorded rather than aborting the remaining runs.

    Args:
        client: Client to benchmark
        prompt: Prompt to send on every run
        n: Number of times to send it

    Returns:
        BenchmarkResult with per-call latencies and any errors
    """
    result = BenchmarkResult(total_runs=n)

    for _ in range(n):
        start = time.perf_counter()
        try:
            await client.chat(prompt)
        except Exception as exc:  # noqa: BLE001 - one bad run must not abort the benchmark
            result.failures += 1
            result.errors.append(str(exc))
            continue
        result.successes += 1
        result.latencies_ms.append((time.perf_counter() - start) * 1000)

    return result
