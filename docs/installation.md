# Installation Guide

## Requirements

- Python 3.10 or later
- pip, poetry, or other package manager
- AWS account with Bedrock access (for Bedrock provider)

## Installing Neuravo

### Via pip (Recommended)

```bash
pip install neuravo
```

### Via poetry

```bash
poetry add neuravo
```

### Via git (Development)

```bash
git clone https://github.com/neuravo/neuravo-sdk.git
cd neuravo-sdk
pip install -e ".[dev]"
```

## Verifying Installation

```python
import neuravo
print(neuravo.__version__)  # Should print: 0.1.0
```

## Setting Up AWS Credentials

### Option 1: Environment Variables (Easiest)

```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1
```

### Option 2: AWS Credentials File

Create `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your-key
aws_secret_access_key = your-secret
```

Create `~/.aws/config`:

```ini
[default]
region = us-east-1
```

### Option 3: IAM Role (Production)

If running on EC2 or ECS, use IAM roles for automatic credential management.

## Testing Installation

```python
import asyncio
from neuravo import Client, Config

async def test():
    config = Config(provider="bedrock", region="us-east-1")
    client = Client(config)
    
    try:
        await client.initialize()
        response = await client.chat("Hello")
        print(f"Success! Response: {response.content[:100]}")
    finally:
        await client.close()

asyncio.run(test())
```

## Troubleshooting

### AWS Credentials Not Found

```
ProviderError: Failed to initialize Bedrock: Unable to locate credentials
```

Solution: Set AWS credentials using environment variables or credential file.

### Model Not Available

```
ProviderError: Model 'model-name' is not available
```

Solution: Check available models with `client.get_available_models()`.

### Permission Denied

```
ProviderError: User is not authorized to perform bedrock operations
```

Solution: Ensure your AWS credentials have Bedrock permissions.

## Installing Optional Dependencies

### For Development

```bash
pip install neuravo[dev]
```

This includes:
- pytest, pytest-asyncio, pytest-cov
- hypothesis (property-based testing)
- black, ruff, mypy (code quality)
- sphinx (documentation)

### For Documentation

```bash
pip install neuravo[docs]
```

---

Ready to get started? See [Getting Started Guide](getting-started.md).
