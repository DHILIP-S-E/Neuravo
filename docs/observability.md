# Observability

Neuravo ships a lightweight observability stack: nested tracing, named
metrics (counters/gauges/histograms), in-process request monitoring, a
CloudWatch exporter, and logging with automatic sensitive-data redaction.
None of it depends on OpenTelemetry — an OTel bridge is potential future
work, not something this SDK provides today.

Everything below is imported from `neuravo.observability`:

```python
from neuravo.observability import (
    get_tracer,
    get_metrics_registry,
    get_monitor,
    CloudWatchExporter,
)
```

## Tracing

`get_tracer()` returns a process-wide `Tracer`. Use `tracer.start_span(name,
**attrs)` as a context manager around any operation you want timed; spans
started while another span is active automatically become children of it
via a `contextvars`-based current-span stack.

```python
from neuravo.observability import get_tracer

tracer = get_tracer()

with tracer.start_span("bedrock.chat", model="anthropic.claude-3-haiku-20240307-v1:0") as outer:
    with tracer.start_span("bedrock.invoke_model") as inner:
        inner.attributes["retry_count"] = 0
        # ... do the actual work here ...
    outer.attributes["response_tokens"] = 128
```

If the block raises, the exception's string is recorded on `span.error` and
the exception is re-raised — the span is still appended to the tracer's
history with `duration_ms` set.

`tracer.get_spans()` returns the completed spans, oldest first, as `Span`
dataclass instances:

```python
for span in tracer.get_spans():
    print(span.span_id, span.parent_id, span.name, span.duration_ms, span.attributes, span.error)
```

`Span` fields: `span_id`, `parent_id` (the enclosing span's id, or `None`
for a root span), `name`, `start_time` (a `datetime`), `duration_ms` (set
once the span ends), `attributes` (dict of whatever you passed as
`**attributes`, plus anything you mutate on the yielded `Span` inside the
block), and `error`.

Call `tracer.reset()` to clear recorded spans (useful between test runs).

## Metrics

`get_metrics_registry()` returns a process-wide `MetricsRegistry`. Ask it
for a `Counter`, `Gauge`, or `Histogram` by name — each metric type has its
own independent namespace, so a counter and a gauge can share a name
without colliding, and repeated calls with the same name return the same
object:

```python
from neuravo.observability import get_metrics_registry

registry = get_metrics_registry()

chat_calls = registry.counter("chat.calls")
chat_calls.inc()          # amount defaults to 1.0
chat_calls.inc(amount=5.0)

queue_depth = registry.gauge("queue.depth")
queue_depth.set(3)

latency = registry.histogram("chat.latency_ms")
latency.observe(87.2)
latency.observe(142.9)

print(latency.mean())          # 0.0 if no observations recorded yet
print(latency.percentile(95))  # nearest-rank percentile; raises ValueError outside [0, 100]
```

- `Counter.inc(amount: float = 1.0)` — monotonically increases `.value`.
- `Gauge.set(value: float)` — sets `.value` directly (can go up or down).
- `Histogram.observe(value: float)` — appends to `.observations`;
  `.mean()` and `.percentile(p)` summarize them (both return `0.0` on an
  empty histogram).

## Request monitoring

`get_monitor()` returns a process-wide `Monitor` purpose-built for the
request/success/failure/latency shape rather than arbitrary named metrics.
Record each call's outcome with `record_request`:

```python
import time
from neuravo.observability import get_monitor

monitor = get_monitor()

start = time.perf_counter()
try:
    response = await client.chat("Hello")
    monitor.record_request((time.perf_counter() - start) * 1000, success=True)
except Exception as exc:
    monitor.record_request(
        (time.perf_counter() - start) * 1000,
        success=False,
        error_type=type(exc).__name__,
    )
```

`record_request(duration_ms, success, error_type=None)` updates a running
average latency and, on failure, increments a per-`error_type` counter.

`monitor.get_snapshot()` returns a copy (mutating it won't affect the
monitor) — a `MetricsSnapshot` with:

- `requests_total`, `requests_succeeded`, `requests_failed`
- `avg_latency_ms` — running average across every recorded request
- `errors_by_type: Dict[str, int]`

```python
snapshot = monitor.get_snapshot()
print(snapshot.requests_total, snapshot.avg_latency_ms, snapshot.errors_by_type)
```

`monitor.reset()` clears all counters back to a fresh `MetricsSnapshot()`.

## Exporting to CloudWatch

`CloudWatchExporter` ships a `MetricsSnapshot` to AWS CloudWatch as custom
metrics under a namespace (`RequestsTotal`, `RequestsSucceeded`,
`RequestsFailed`, `AverageLatency`, plus one `ErrorsByType` data point per
error type with an `ErrorType` dimension).

```python
from neuravo.observability import get_monitor, CloudWatchExporter

monitor = get_monitor()
exporter = CloudWatchExporter(namespace="Neuravo", region="us-east-1")

exporter.export_snapshot(monitor.get_snapshot())
```

**This is a real, billed AWS API call (`cloudwatch:PutMetricData`) — it is
never triggered automatically by the SDK.** Nothing in Neuravo calls
`export_snapshot` on your behalf; you decide when, and how often, to ship
metrics to CloudWatch. A failed call raises `neuravo.core.exceptions.ProviderError`.

`region` defaults to whatever the standard AWS credential chain resolves
(e.g. `AWS_REGION`) if not given explicitly.

## Logging and redaction

```python
from neuravo import setup_logging, get_logger

setup_logging("INFO")
logger = get_logger("providers.bedrock")  # -> logger name "neuravo.providers.bedrock"
logger.info("using api_key=sk-abc123xyz to call the provider")
```

Every log record emitted through a Neuravo logger passes through a
`logging.Filter` that redacts sensitive substrings **automatically, with no
opt-in required** — API keys/secrets, AWS access keys and secret keys,
passwords, tokens, bearer credentials, and `Authorization` header values are
all replaced with `[REDACTED]` before the line is written, whether the
message goes to stderr or to an optional log file. In the example above,
the emitted line reads `using api_key=[REDACTED] to call the provider`.
