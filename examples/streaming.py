"""Stream a chat response progressively instead of waiting for the whole reply.

Run:
    python examples/streaming.py

Requires AWS credentials with Bedrock access.
"""

import asyncio

from neuravo import Client, Config


async def main() -> None:
    """Print response chunks as they arrive."""
    client = Client(
        Config(
            provider="bedrock",
            region="us-east-1",
            model="anthropic.claude-3-sonnet-20240229-v1:0",
        )
    )

    try:
        async for chunk in client.stream("Tell me a short story about a lighthouse."):
            print(chunk.content, end="", flush=True)
        print()

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
