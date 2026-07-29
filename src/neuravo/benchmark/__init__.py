"""Benchmark capability for Neuravo SDK.

Measures per-call latency of a client's chat calls over repeated runs.

Examples:
    Benchmark a client::

        from neuravo.benchmark import run_benchmark

        result = await run_benchmark(client, "Hello", n=20)
        print(f"mean={result.mean_latency_ms:.1f}ms p95={result.percentile_latency_ms(95):.1f}ms")
"""

from neuravo.benchmark.runner import BenchmarkResult, run_benchmark

__all__ = [
    "BenchmarkResult",
    "run_benchmark",
]
