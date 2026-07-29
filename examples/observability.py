"""Tracing, metrics, and cost tracking around a chat call.

Run:
    python examples/observability.py

Requires AWS credentials with Bedrock access.
"""

import asyncio

from neuravo import Client, Config
from neuravo.cost import CostTracker
from neuravo.observability import get_metrics_registry, get_monitor, get_tracer


async def main() -> None:
    client = Client(Config(provider="bedrock", region="us-east-1"))
    tracer = get_tracer()
    monitor = get_monitor()
    metrics = get_metrics_registry()
    cost_tracker = CostTracker()

    try:
        with tracer.start_span("example.chat_call", prompt_length=len("Hello!")):
            response = await client.chat("Hello!")

        # Record this call in the in-process request monitor.
        monitor.record_request(duration_ms=tracer.get_spans()[-1].duration_ms, success=True)

        # Track a custom named metric alongside the built-in monitor.
        metrics.counter("example.chat_calls").inc()
        metrics.histogram("example.response_tokens").observe(response.usage.total_tokens)

        # Track spend for this call.
        cost = cost_tracker.record(response.model, response.usage)

        print(f"Response: {response.content}\n")
        print(f"Span recorded: {tracer.get_spans()[-1].name} "
              f"({tracer.get_spans()[-1].duration_ms:.1f}ms)")
        print(f"Monitor snapshot: {monitor.get_snapshot()}")
        print(f"This call cost: ${cost:.6f}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
