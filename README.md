# Neuravo

**A provider-agnostic Python SDK for AI model interactions** — write your chat
logic once, run it against AWS Bedrock or OpenAI interchangeably, with retry
logic, streaming, observability, and cost tracking built in.

[![Tests](https://github.com/DHILIP-S-E/Neuravo/actions/workflows/test.yml/badge.svg)](https://github.com/DHILIP-S-E/Neuravo/actions/workflows/test.yml)
[![Lint](https://github.com/DHILIP-S-E/Neuravo/actions/workflows/lint.yml/badge.svg)](https://github.com/DHILIP-S-E/Neuravo/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](pyproject.toml)

## Why Neuravo?

Every LLM provider's SDK looks slightly different — different auth patterns,
different response shapes, different streaming mechanics. Neuravo puts one
consistent interface in front of them: the same `Client`, the same
`ChatResponse`, the same retry and error-handling behavior, regardless of
which vendor is actually answering the request. Switching providers is a
one-string change (`Config(provider="bedrock")` → `Config(provider="openai")`);
nothing else in your application code changes.

## Features

- **Provider-agnostic** — Bedrock and OpenAI today, both implementing the
  identical `BaseProvider` contract, so they're interchangeable
- **Production-ready core** — automatic retry with exponential backoff,
  configurable timeouts, a normalized exception hierarchy (no vendor-specific
  `except` clauses in your code)
- **Streaming** — progressive response delivery via `async for`
- **Type-safe** — full type hints, `mypy --strict` clean, ships `py.typed`
- **Observability** — nested tracing spans, named metrics (counters/gauges/
  histograms), in-process request monitoring, and a CloudWatch exporter
- **Cost tracking** — per-call and running-total USD cost from token usage
- **Evaluation** — run prompt/expected-output cases through a client and score
  the responses with pluggable scorers
- **Prompt management** — named, versioned prompt templates
- **Benchmarking** — latency statistics (mean, percentiles) over repeated calls
- **Security** — prompt-level block-list checks and output redaction
- **Workflow engine** — chain multi-step operations over a shared context
- **Plugins** — third-party providers register via standard Python entry points
- **Sensitive-data redaction** — API keys, tokens, and credentials are
  automatically stripped from log output

## Installation

```bash
pip install neuravo
```

Using OpenAI instead of (or alongside) Bedrock:

```bash
pip install "neuravo[openai]"
```

## Quick Start

```python
import asyncio
from neuravo import Client, Config


async def main():
    client = Client(Config(provider="bedrock", region="us-east-1"))
    try:
        response = await client.chat("What is machine learning?")
        print(response.content)
    finally:
        await client.close()


asyncio.run(main())
```

Streaming instead of waiting for the full response:

```python
async for chunk in client.stream("Tell me a story"):
    print(chunk.content, end="", flush=True)
```

Switching to OpenAI is a one-line change:

```python
client = Client(Config(provider="openai", model="gpt-4o-mini"))
```

## Examples

Runnable, self-contained scripts in [`examples/`](examples/):

| Script | Demonstrates |
|---|---|
| [`hello_world.py`](examples/hello_world.py) | The smallest possible chat call |
| [`chat.py`](examples/chat.py) | Multi-turn conversation with history |
| [`streaming.py`](examples/streaming.py) | Streaming a response progressively |
| [`aws_bedrock.py`](examples/aws_bedrock.py) | Bedrock-specific config, model discovery, health checks |
| [`observability.py`](examples/observability.py) | Tracing, metrics, and cost tracking around a call |

```bash
python examples/hello_world.py
```

## Supported Providers

| Provider | `provider` value | Install |
|---|---|---|
| AWS Bedrock | `"bedrock"` | included by default |
| OpenAI | `"openai"` | `pip install "neuravo[openai]"` |

See [docs/providers.md](docs/providers.md) for available models and
per-provider setup details.

## Documentation

- [Quickstart](docs/quickstart.md)
- [Configuration](docs/configuration.md)
- [Providers](docs/providers.md)
- [Observability](docs/observability.md)
- [Cost tracking](docs/cost.md)
- [Roadmap](docs/roadmap.md)
- [API reference](docs/api/README.md)
- [Getting started guide](docs/getting-started.md) / [Installation](docs/installation.md)

## Roadmap

The capabilities above (observability, cost tracking, evaluation, prompt
management, benchmarking, security, workflows, plugins) are already real,
working, tested code on `main` — not a future promise. The package version
hasn't been formally bumped past `0.1.0` yet. See
[docs/roadmap.md](docs/roadmap.md) for exactly what's shipped versus what's
still a placeholder (`cache/`, rate limiting, `agents/`, `embeddings/`,
`memory/`).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, running tests/
lint/type-checks, and — especially — the steps for adding a new provider.

Please also read the [Code of Conduct](CODE_OF_CONDUCT.md). For security
issues, see [SECURITY.md](SECURITY.md) rather than opening a public issue.

## License

[MIT](LICENSE)
