"""Error handling example.

Shows how to handle various error scenarios.

Run:
    python examples/error_handling.py
"""

import asyncio
from neuravo import Client, Config
from neuravo.core.exceptions import (
    NeurevoError,
    ConfigError,
    ProviderError,
    ValidationError,
)


async def main():
    """Error handling example."""
    # Example 1: Configuration error
    try:
        config = Config(provider="bedrock", timeout=5000)  # Invalid: too long
    except Exception as e:
        print(f"Configuration error: {e}")

    # Example 2: Provider error (bad credentials)
    try:
        config = Config(provider="bedrock", region="us-east-1")
        client = Client(config)
        await client.initialize()
    except ConfigError as e:
        print(f"Configuration issue: {e}")
    except ProviderError as e:
        print(f"Provider unavailable: {e}")
    except NeurevoError as e:
        print(f"Unexpected error: {e}")

    # Example 3: Validation error (empty prompt)
    try:
        config = Config(provider="bedrock", region="us-east-1")
        client = Client(config)
        await client.initialize()

        # Empty prompt should raise ValidationError
        response = await client.chat("")

    except ValidationError as e:
        print(f"Input validation failed: {e}")
    except NeurevoError as e:
        print(f"Error: {e}")
    finally:
        try:
            await client.close()
        except Exception:
            pass

    # Example 4: Timeout handling
    try:
        config = Config(provider="bedrock", timeout=0.001)  # Very short timeout
        client = Client(config)
        await client.initialize()

        response = await client.chat("Hello")

    except TimeoutError as e:
        print(f"Request timed out: {e}")
    except NeurevoError as e:
        print(f"Error: {e}")
    finally:
        try:
            await client.close()
        except Exception:
            pass

    print("\nError handling examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
