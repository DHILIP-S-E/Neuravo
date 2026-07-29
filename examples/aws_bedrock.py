"""Bedrock-specific features: explicit credentials, model discovery, health checks.

Run:
    python examples/aws_bedrock.py

By default this uses the standard boto3 credential chain (same as the other
examples). Pass explicit credentials via BedrockConfig only if you need to
target a specific access key rather than your environment's default.
"""

import asyncio

from neuravo import Client
from neuravo.providers.aws.bedrock import BedrockConfig, BedrockProvider


async def main() -> None:
    # BedrockConfig extends Config with AWS-specific fields (all optional -
    # omit them to use the standard boto3 credential chain instead).
    config = BedrockConfig(
        provider="bedrock",
        region="us-east-1",
        model="anthropic.claude-3-haiku-20240307-v1:0",
        # access_key_id="...",       # only needed to override the default chain
        # secret_access_key="...",
    )

    client = Client(config)

    try:
        # Discover available models without sending a chat request.
        provider = BedrockProvider()
        print("Available Bedrock models:")
        for model in provider.get_available_models():
            print(f"  - {model.id} ({model.name})")

        response = await client.chat("What's the fastest way to learn Python?")
        print(f"\n{response.content}")
        print(f"\nTokens used: {response.usage.total_tokens}")

        status = await client.health_check()
        print(f"Provider healthy: {status.is_healthy} ({status.latency_ms:.1f}ms)")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
