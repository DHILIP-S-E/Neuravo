# Quickstart

Get from `pip install` to a working chat call in a couple of minutes.

## Install

```bash
pip install neuravo
```

The default install supports the **Bedrock** provider (via `boto3`, installed
automatically) with no extra setup beyond AWS credentials. If you want to use
OpenAI instead, see the aside at the bottom of this page.

## Prerequisites (Bedrock)

Neuravo doesn't manage AWS credentials itself — it hands them to `boto3`,
which uses the standard AWS credential chain. The easiest option for a quick
test is environment variables:

```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1
```

## Your first chat call

```python
import asyncio
from neuravo import Client, Config


async def main():
    config = Config(
        provider="bedrock",
        region="us-east-1",
        model="anthropic.claude-3-haiku-20240307-v1:0",
    )
    client = Client(config)

    try:
        response = await client.chat("What is machine learning?")
        print(response.content)
        print(f"tokens used: {response.usage.total_tokens}")
    finally:
        await client.close()


asyncio.run(main())
```

Notes:

- `client.initialize()` doesn't need to be called explicitly — `chat()` lazily
  initializes the provider on first use.
- `region` falls back to the `AWS_REGION` environment variable if omitted from
  `Config`.
- Always `await client.close()` when you're done to release the underlying
  provider connection.

## Streaming a response

```python
import asyncio
from neuravo import Client, Config


async def main():
    config = Config(provider="bedrock", region="us-east-1")
    client = Client(config)

    try:
        async for chunk in client.stream("Tell me a short story"):
            print(chunk.content, end="", flush=True)
        print()
    finally:
        await client.close()


asyncio.run(main())
```

Each `chunk` is a `ChatResponse` with just the incremental `content` text —
accumulate it yourself if you need the full message (the `Client` does this
internally for conversation history).

## Using OpenAI instead

Switching providers is a one-string change to `Config`. OpenAI support needs
the optional extra and an API key:

```bash
pip install "neuravo[openai]"
export OPENAI_API_KEY=sk-...
```

```python
config = Config(provider="openai", model="gpt-4o-mini")
client = Client(config)
response = await client.chat("What is machine learning?")
```

See [configuration.md](configuration.md) for all `Config` fields and
[providers.md](providers.md) for provider-specific details.
