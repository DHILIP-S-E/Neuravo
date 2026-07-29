# Cost Intelligence

> **The built-in pricing table is illustrative only — it is not guaranteed
> accurate.** `neuravo.cost.pricing.PRICING` hardcodes a handful of USD
> rates per 1,000 tokens as a starting point. AWS Bedrock and OpenAI both
> change published pricing over time (and Bedrock pricing varies by
> region), so anything that matters for real billing should verify current
> rates against the provider's official pricing page and override the
> table rather than trust it. The source itself carries this caveat:
> "Indicative rates as of this writing - verify against AWS's published
> Bedrock pricing before relying on these for real cost accounting."

Everything below is imported from `neuravo.cost`:

```python
from neuravo.cost import CostTracker, calculate_cost, get_pricing
```

## One-off cost calculation

`calculate_cost(usage, model)` computes the USD cost of a single call from
a `TokenUsage` (which has `prompt_tokens`, `completion_tokens`,
`total_tokens`) and a model identifier:

```python
from neuravo.cost import calculate_cost

cost = calculate_cost(response.usage, response.model)
print(f"${cost:.4f}")
```

It looks the model up in `PRICING` and raises `KeyError` if the model isn't
registered. To check pricing without risking that exception, use
`get_pricing(model)`, which returns a `ModelPricing(input_per_1k,
output_per_1k)` or `None` if the model is unknown:

```python
from neuravo.cost import get_pricing

pricing = get_pricing("anthropic.claude-3-haiku-20240307-v1:0")
if pricing is not None:
    print(pricing.input_per_1k, pricing.output_per_1k)
```

The models Neuravo ships pricing for out of the box are
`anthropic.claude-3-sonnet-20240229-v1:0`,
`anthropic.claude-3-haiku-20240307-v1:0`, and `meta.llama2-70b-chat-v1` —
again, treat these rates as placeholders, not current published prices.
For any other model (including every OpenAI model), either add an entry to
`PRICING` yourself or call `calculate_cost`/`CostTracker.record` expecting
a `KeyError` until you do.

## Tracking spend across calls

`CostTracker` accumulates cost over many calls, broken down by model:

```python
from neuravo.cost import CostTracker

tracker = CostTracker()

response = await client.chat("Hello")
cost = tracker.record(response.model, response.usage)
print(f"This call cost ${cost:.4f}")
```

`record(model, usage) -> float` calculates the cost of that single call
(same logic as `calculate_cost`, and it raises the same `KeyError` for an
unpriced model), adds it to the running totals, and returns just that
call's cost so you can log or display it immediately.

`tracker.get_snapshot()` returns a copy — a `CostSnapshot` with:

- `total_cost_usd` — cumulative spend across every `record()` call
- `total_calls` — number of `record()` calls made
- `cost_by_model: Dict[str, float]` — cumulative spend per model

```python
snapshot = tracker.get_snapshot()
print(snapshot.total_cost_usd, snapshot.total_calls, snapshot.cost_by_model)
```

`tracker.reset()` clears the tracker back to a fresh, zeroed `CostSnapshot`.

## Realistic usage pattern

Record cost right after every chat call so spend accumulates as the
application runs:

```python
from neuravo import Client, Config
from neuravo.cost import CostTracker

config = Config(provider="bedrock", region="us-east-1")
client = Client(config)
tracker = CostTracker()

try:
    response = await client.chat("What is machine learning?")
    call_cost = tracker.record(response.model, response.usage)
    print(f"This call: ${call_cost:.4f}")

    snapshot = tracker.get_snapshot()
    print(f"Running total: ${snapshot.total_cost_usd:.4f} across {snapshot.total_calls} calls")
finally:
    await client.close()
```

If you call a model that isn't in `PRICING` (any OpenAI model today, or a
Bedrock model outside the three listed above), `tracker.record` raises
`KeyError` — either catch it, or extend `neuravo.cost.pricing.PRICING` with
the models and rates you actually use before wiring cost tracking into
production.
