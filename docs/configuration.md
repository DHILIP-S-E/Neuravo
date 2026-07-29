# Configuration

Neuravo is configured through a `Config` object (a `pydantic.BaseModel`).
`Config` is **immutable** — it's a frozen pydantic model, so once you've
constructed one you can't reassign its fields (`config.model = "x"` will
raise). To change settings, construct a new `Config`.

```python
from neuravo import Config

config = Config(provider="bedrock", region="us-east-1")
```

## Base `Config` fields

| Field            | Type            | Default      | Notes |
|------------------|-----------------|--------------|-------|
| `provider`       | `str`           | `"bedrock"`  | Provider name, e.g. `"bedrock"` or `"openai"`. Lowercased and validated (non-empty, ≤50 chars). |
| `region`         | `Optional[str]` | `None`       | AWS region for Bedrock. If not provided, falls back to the `AWS_REGION` environment variable. |
| `model`          | `Optional[str]` | `None`       | Model identifier. Provider-specific — see [providers.md](providers.md) for the available IDs. If omitted, each provider uses its own default model. |
| `timeout`        | `float`         | `30.0`       | Request timeout in seconds. Must be between 1.0 and 3600.0. |
| `max_retries`    | `int`           | `3`          | Maximum retry attempts on a failed `chat()` call. Must be between 0 and 10. |
| `backoff_factor` | `float`         | `2.0`        | Exponential backoff multiplier between retries. Must be between 1.0 and 10.0. |
| `debug`          | `bool`          | `False`      | Enable debug logging. |

Retries are handled automatically — `Client.chat()` wraps the provider call in
a `neuravo.retry.ExponentialBackoffRetry` built from `max_retries` and
`backoff_factor`, so you don't need to implement retry logic yourself.

### Example

```python
from neuravo import Config

config = Config(
    provider="bedrock",
    region="us-east-1",
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    timeout=60.0,
    max_retries=5,
    backoff_factor=1.5,
    debug=True,
)
```

## `BedrockConfig`

`from neuravo.providers.aws.bedrock import BedrockConfig`

Extends `Config` with AWS credential fields. All are optional — if omitted,
`boto3` falls back to its standard credential chain (environment variables,
`~/.aws/credentials`, IAM role, etc.).

| Field                | Type            | Default | Notes |
|----------------------|-----------------|---------|-------|
| `access_key_id`      | `Optional[str]` | `None`  | AWS access key. Falls back to `AWS_ACCESS_KEY_ID` via boto3 if not set. |
| `secret_access_key`  | `Optional[str]` | `None`  | AWS secret key. Falls back to `AWS_SECRET_ACCESS_KEY` via boto3 if not set. |
| `session_token`      | `Optional[str]` | `None`  | Optional AWS session token (e.g. for temporary/STS credentials). |
| `inference_id`       | `Optional[str]` | `None`  | Optional inference ID for tracking. |

### Example

```python
from neuravo import Client
from neuravo.providers.aws.bedrock import BedrockConfig

config = BedrockConfig(
    provider="bedrock",
    region="us-east-1",
    model="anthropic.claude-3-haiku-20240307-v1:0",
    access_key_id="AKIA...",
    secret_access_key="...",
)
client = Client(config)
```

## `OpenAIConfig`

`from neuravo.providers.openai.chat import OpenAIConfig`

Requires the `neuravo[openai]` extra (`pip install "neuravo[openai]"`).
Extends `Config` with OpenAI-specific auth fields.

| Field          | Type            | Default | Notes |
|----------------|-----------------|---------|-------|
| `api_key`      | `Optional[str]` | `None`  | OpenAI API key. If not set, the underlying `openai` SDK falls back to the `OPENAI_API_KEY` environment variable. |
| `organization` | `Optional[str]` | `None`  | Optional OpenAI organization ID. |

### Example

```python
from neuravo import Client
from neuravo.providers.openai.chat import OpenAIConfig

config = OpenAIConfig(
    provider="openai",
    model="gpt-4o-mini",
    api_key="sk-...",
)
client = Client(config)
```

See [providers.md](providers.md) for available models and per-provider setup
details.
