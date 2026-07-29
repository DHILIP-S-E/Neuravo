# Neuravo: Python AI Infrastructure SDK

A production-grade, provider-agnostic Python SDK for AI model interactions with support for AWS Bedrock and future multi-provider extensibility.

## Features

- **Provider Agnostic**: Write code once, switch providers without changes
- **Production Ready**: Retry logic, timeout management, comprehensive error handling
- **Type Safe**: Complete type hints, mypy strict compliance
- **Streaming Support**: Progressive response delivery with async/await
- **Extensible Architecture**: Clear extension points for new providers and features
- **Observable**: Structured logging with sensitive data redaction

## Quick Start

### Installation

```bash
pip install neuravo
```

### Basic Usage

```python
from neuravo import Client, Config

# Create configuration
config = Config(provider="bedrock", region="us-east-1")

# Create client
client = Client(config)

# Chat
response = await client.chat("What is machine learning?")
print(response.content)
```

### Streaming Responses

```python
async def stream_example():
    async for chunk in client.stream("Tell me a story"):
        print(chunk.content, end="", flush=True)
```

## Documentation

- [Getting Started Guide](docs/getting-started.md)
- [API Reference](docs/api-reference/index.md)
- [Architecture Overview](docs/architecture/architecture-overview.md)
- [Troubleshooting](docs/troubleshooting.md)

## Support

- **Issues**: https://github.com/neuravo/neuravo-sdk/issues
- **Discussions**: https://github.com/neuravo/neuravo-sdk/discussions
- **Email**: support@neuravo.ai

## License

MIT License - see LICENSE file for details

## Roadmap

- **v0.1** (Current): Bedrock + Chat feature
- **v0.2** (Q2 2025): OpenAI + Embeddings
- **v0.3** (Q3 2025): Agents + Memory
- **v1.0** (Q4 2025): Production stable, multi-provider

## Contributing

See CONTRIBUTING.md for development setup and guidelines.

---

**Version**: 0.1.0 | **Status**: Alpha | **Python**: 3.10+
