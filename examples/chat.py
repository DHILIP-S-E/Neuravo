"""Multi-turn chat with conversation history.

Run:
    python examples/chat.py

Requires AWS credentials with Bedrock access.
"""

import asyncio

from neuravo import Client, Config


async def main() -> None:
    """Send a few turns of conversation and print the running history."""
    client = Client(
        Config(
            provider="bedrock",
            region="us-east-1",
            model="anthropic.claude-3-haiku-20240307-v1:0",
        )
    )

    try:
        for prompt in [
            "What is the capital of France?",
            "What's a famous landmark there?",
        ]:
            response = await client.chat(prompt)
            print(f"> {prompt}")
            print(f"{response.content}\n")

        print("--- Full conversation history ---")
        for message in await client.get_chat_history():
            print(f"[{message.role}] {message.content}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
