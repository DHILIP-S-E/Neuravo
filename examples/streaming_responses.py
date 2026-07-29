"""Streaming response example.

Shows how to stream chat responses progressively.

Run:
    python examples/streaming_responses.py
"""

import asyncio
from neuravo import Client, Config


async def main():
    """Stream chat response example."""
    # Create configuration
    config = Config(
        provider="bedrock",
        region="us-east-1",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
    )

    # Create client
    client = Client(config)

    try:
        await client.initialize()

        print("Streaming response from Claude:\n")

        # Stream response
        async for chunk in client.stream("Tell me about artificial intelligence in 3 paragraphs"):
            print(chunk.content, end="", flush=True)

        print("\n\nStreaming complete!")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
