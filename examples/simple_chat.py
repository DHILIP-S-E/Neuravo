"""Simple chat example.

A basic example showing how to use Neuravo SDK for chat interactions.

Run:
    python examples/simple_chat.py
"""

import asyncio
from neuravo import Client, Config


async def main():
    """Run simple chat example."""
    # Create configuration
    config = Config(
        provider="bedrock",
        region="us-east-1",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
    )

    # Create client
    client = Client(config)

    try:
        # Initialize (establishes connection to Bedrock)
        print("Initializing client...")
        await client.initialize()

        # Send a simple message
        print("\nSending message to Claude...")
        response = await client.chat("What is machine learning?")

        # Display response
        print("\nResponse:")
        print(f"Model: {response.model}")
        print(f"Content: {response.content}")
        print(f"Tokens: {response.usage.total_tokens}")

    finally:
        # Always close the connection
        await client.close()
        print("\nClient closed.")


if __name__ == "__main__":
    asyncio.run(main())
