"""The smallest possible Neuravo example.

Run:
    python examples/hello_world.py

Requires AWS credentials with Bedrock access (via the standard boto3
credential chain: environment variables, ~/.aws/credentials, or an IAM role)
and a region with Bedrock model access enabled.
"""

import asyncio

from neuravo import Client, Config


async def main() -> None:
    """Send one message and print the reply."""
    client = Client(Config(provider="bedrock", region="us-east-1"))
    response = await client.chat("Say hello in one sentence.")
    print(response.content)
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
