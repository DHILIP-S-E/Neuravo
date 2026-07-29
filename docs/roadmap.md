# Roadmap

This page tracks what Neuravo's growth plan promised versus what's actually
implemented in the codebase today, verified against
[`CHANGELOG.md`](../CHANGELOG.md).

## Important: version number vs. capability

The package version in `pyproject.toml` is still **`0.1.0`**. That number
has *not* been bumped to track the work below — everything through "v1.0"
in the growth plan is **real, working, tested code already on the `main`
branch**, not an aspirational plan or a description of a future release.
Treat the "vX.Y" labels below as growth-plan milestones the codebase has
already reached, not as SDK release tags you can `pip install` by number
yet. A formal version bump and release cut is still pending.

## Growth plan status

| Milestone | Capability | Status |
|---|---|---|
| v0.1 | Core client, AWS Bedrock provider, Chat, Streaming | Done |
| v0.2 | Observability (tracing, metrics, monitoring, CloudWatch export) | Done |
| v0.3 | Cost Intelligence (pricing table, `CostTracker`) | Done |
| v0.4 | OpenAI Provider | Done |
| v0.5 | Evaluation | Done |
| v0.6 | Prompt Management | Done |
| v0.7 | Benchmark | Done |
| v0.8 | Security | Done |
| v0.9 | Workflow Engine | Done |
| v1.0 | Plugin System | Done |

What "done" means for each, concretely:

- **v0.1 — Core + Bedrock + Chat + Streaming**: `Client`/`Config` in
  `neuravo.core`, an AWS Bedrock provider under `neuravo.providers`, chat
  with conversation history (`neuravo.chat`), and streaming responses.
- **v0.2 — Observability**: `Tracer` with nested spans, `MetricsRegistry`
  (`Counter`/`Gauge`/`Histogram`), in-process `Monitor`, and
  `CloudWatchExporter` — all in `neuravo.observability`. See
  [`observability.md`](observability.md).
- **v0.3 — Cost Intelligence**: a per-model pricing table plus
  `CostTracker` with running totals and a per-model breakdown, in
  `neuravo.cost`. See [`cost.md`](cost.md).
- **v0.4 — OpenAI Provider**: installed via the `neuravo[openai]` extra,
  implementing the same `BaseProvider` contract as Bedrock, so switching
  is a one-string change to `Config(provider="openai")`.
- **v0.5 — Evaluation**: `PromptTemplate`-driven `EvalCase`s run through an
  `EvaluationRunner`, scored with `exact_match`/`contains`/`regex_match`.
- **v0.6 — Prompt Management**: `PromptTemplate` with named placeholders
  and a versioned `PromptRegistry`.
- **v0.7 — Benchmark**: `run_benchmark` computes per-call latency stats
  (mean/percentile) against any client.
- **v0.8 — Security**: `SecurityPolicy` combining block-list prompt checks
  with output redaction.
- **v0.9 — Workflow Engine**: a sequential `Step`/`Workflow` pipeline that
  passes a shared context between steps.
- **v1.0 — Plugin System**: entry-point-based discovery under the
  `neuravo.plugins` group, with per-plugin failure isolation so one bad
  plugin doesn't take down the others.

## Future work (genuinely not done yet)

These exist as placeholder packages or stub modules in the source tree
today — present, but not functional, and not something you should build
against yet:

- **`cache/`** — `Cache` class exists with the right method signatures
  (`get`, `set`, `clear`), but every method body is an unimplemented
  `pass`. No actual caching happens.
- **`retry/rate_limit.py`** — `RateLimiter`/`RateLimitConfig` exist with a
  token-bucket shape, but `acquire()` and `_refill()` are both `pass`. No
  rate limiting is actually enforced.
- **`retry/timeout.py`** — `TimeoutManager`/`TimeoutConfig` exist, but
  `execute_with_timeout()` and `_get_timeout()` are both `pass`. No
  timeout is actually enforced by this module (note: this is distinct from
  the retry/backoff logic used by `Client.chat`, which is implemented).
- **`agents/`, `embeddings/`, `memory/`** — empty placeholder packages
  (an `__init__.py` and nothing else). These are reserved namespace for
  potential future capabilities and are **not part of the current growth
  plan** — there's no committed design or timeline for them yet.

If you're evaluating Neuravo for a use case that depends on caching, rate
limiting, enforced timeouts, agents, embeddings, or memory, assume none of
that exists yet and plan accordingly.
