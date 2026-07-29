# Getting Started with Neuravo SDK

Welcome to Neuravo! This guide will get you up and running in 5 minutes.

## Prerequisites

- Python 3.10 or later
- pip or poetry
- AWS credentials (for Bedrock provider)

## Installation

Install Neuravo using pip:

```bash
pip install neuravo
```

## Setup AWS Credentials

For Bedrock support, configure your AWS credentials:

```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1

# Option 2: AWS credentials file (~/.aws/credentials)
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key

# Option 3: AWS config file (~/.aws/config)
[default]
region = us-east-1
```

## Your First Chat

Create a file `hello_neuravo.py`:

```python
import asyncio
from neuravo import Client, Config

async def main():
    # Create configuration
    config = Config(
        provider="bedrock",
        region="us-east-1",
        model="anthropic.claude-3-sonnet-20240229-v1:0"
    )
    
    # Create client
    client = Client(config)
    
    # Initialize (establishes connection)
    await client.initialize()
    
    try:
        # Send message
        response = await client.chat("What is machine learning?")
        print(f"Response: {response.content}")
        
    finally:
        await client.close()

# Run the example
asyncio.run(main())
```

Run it:

```bash
python hello_neuravo.py
```

## Streaming Responses

For progressive response delivery:

```python
async def stream_example():
    config = Config(provider="bedrock", region="us-east-1")
    client = Client(config)
    
    await client.initialize()
    
    try:
        print("Streaming response:")
        async for chunk in client.stream("Tell me a short story"):
            print(chunk.content, end="", flush=True)
        print()  # Newline at end
        
    finally:
        await client.close()

asyncio.run(stream_example())
```

## Error Handling

Handle errors gracefully:

```python
from neuravo.core.exceptions import (
    NeurevoError,
    ConfigError,
    ProviderError,
    ValidationError,
)

async def robust_example():
    config = Config(provider="bedrock", region="us-east-1")
    client = Client(config)
    
    try:
        await client.initialize()
        response = await client.chat("Hello!")
        print(response.content)
        
    except ConfigError as e:
        print(f"Configuration error: {e}")
    except ProviderError as e:
        print(f"Provider error: {e}")
    except ValidationError as e:
        print(f"Validation error: {e}")
    except NeurevoError as e:
        print(f"SDK error: {e}")
    finally:
        await client.close()
```

## Configuration Options

```python
config = Config(
    provider="bedrock",           # AI provider
    region="us-east-1",           # AWS region
    model="anthropic.claude-3-sonnet-20240229-v1:0",  # Model to use
    timeout=30.0,                 # Request timeout (seconds)
    max_retries=3,                # Automatic retries
    backoff_factor=2.0,           # Retry backoff multiplier
    debug=False                   # Debug logging
)
```

## Accessing Chat History

```python
async def with_history():
    config = Config(provider="bedrock", region="us-east-1")
    client = Client(config)
    
    await client.initialize()
    
    try:
        # First message
        response1 = await client.chat("What is Python?")
        
        # Second message
        response2 = await client.chat("What are its uses?")
        
        # Get history
        history = await client.get_chat_history()
        for msg in history:
            print(f"{msg.role}: {msg.content}")
        
    finally:
        await client.close()
```

## Next Steps

- Read the [Chat Guide](guides/chat-guide.md) for advanced usage
- Check [API Reference](api-reference/index.md) for complete documentation
- Explore [Examples](../examples/) directory for more patterns
- See [Troubleshooting](troubleshooting.md) if you hit issues

## Getting Help

- GitHub Issues: https://github.com/neuravo/neuravo-sdk/issues
- Documentation: https://neuravo.readthedocs.io
- Email: support@neuravo.ai

---

Happy coding with Neuravo! 🚀
