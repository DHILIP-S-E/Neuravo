# Providers

Neuravo ships with two built-in providers: **AWS Bedrock** and **OpenAI**.
Both implement the same `BaseProvider` interface, so switching between them
is a one-line change to `Config(provider=...)` — the rest of your `Client`
code (`chat()`, `stream()`, `get_chat_history()`, etc.) stays identical.

| | Bedrock | OpenAI |
|---|---|---|
| `provider` value | `"bedrock"` | `"openai"` |
| Install | included by default | `pip install "neuravo[openai]"` |
| Config class | `BedrockConfig` | `OpenAIConfig` |
| Auth | standard AWS credential chain (env vars, `~/.aws/credentials`, IAM role) or explicit `access_key_id`/`secret_access_key` on `BedrockConfig` | `OPENAI_API_KEY` env var or explicit `api_key` on `OpenAIConfig` |
| Required config | `region` (raises `MissingConfigError` if absent) | none — API key can come entirely from the environment |
| Default model | `anthropic.claude-3-haiku-20240307-v1:0` | `gpt-4o-mini` |

## AWS Bedrock

`from neuravo.providers.aws.bedrock import BedrockConfig`

Talks to Bedrock through the `converse` / `converse_stream` APIs, which give
a single request/response shape across model families instead of each
model's own `invoke_model` payload format.

**Requirements:**
- An AWS account with Bedrock access and model access enabled for the models
  you want to use.
- Credentials resolvable by `boto3` — environment variables, an
  `~/.aws/credentials` file, an IAM role (e.g. on EC2/ECS), or explicit
  `access_key_id` / `secret_access_key` / `session_token` on `BedrockConfig`.
- `region` set on `Config` (or the `AWS_REGION` environment variable) —
  Bedrock initialization raises `MissingConfigError` without it.

**Available models** (`neuravo.providers.aws.bedrock.BEDROCK_MODELS`):

| Model ID | Name | Provider | Max tokens |
|---|---|---|---|
| `anthropic.claude-3-sonnet-20240229-v1:0` | Claude 3 Sonnet | Anthropic | 200,000 |
| `anthropic.claude-3-haiku-20240307-v1:0` | Claude 3 Haiku | Anthropic | 200,000 |
| `meta.llama2-70b-chat-v1` | Llama 2 70B Chat | Meta | 4,096 |

```python
from neuravo import Client, Config

config = Config(
    provider="bedrock",
    region="us-east-1",
    model="anthropic.claude-3-sonnet-20240229-v1:0",
)
client = Client(config)
response = await client.chat("Hello, world!")
```

## OpenAI

`from neuravo.providers.openai.chat import OpenAIConfig`

Uses OpenAI's own async SDK (`AsyncOpenAI`) directly, so no thread-bridging
is needed for streaming (unlike Bedrock, whose blocking event stream is
consumed on a background thread internally).

**Requirements:**
- The optional extra: `pip install "neuravo[openai]"` (installs `openai>=1.0`).
- An API key — either the `OPENAI_API_KEY` environment variable, or an
  explicit `api_key` on `OpenAIConfig`. No field is strictly required at the
  config level; validation always passes and the underlying `openai` SDK
  handles the environment-variable fallback.

**Available models** (`neuravo.providers.openai.chat._MODEL_CATALOG`):

| Model ID | Name | Max tokens |
|---|---|---|
| `gpt-4o` | GPT-4o | 128,000 |
| `gpt-4o-mini` | GPT-4o mini | 128,000 |
| `gpt-3.5-turbo` | GPT-3.5 Turbo | 16,385 |

```python
from neuravo import Client
from neuravo.providers.openai.chat import OpenAIConfig

config = OpenAIConfig(provider="openai", model="gpt-4o")
client = Client(config)
response = await client.chat("Hello, world!")
```

## The `BaseProvider` contract

Both providers subclass `neuravo.providers.base.BaseProvider`, an abstract
class requiring `initialize(config)`, `validate_config(config)`,
`get_available_models()`, `chat(messages)`, `stream_chat(messages)`,
`health_check()`, and `close()`. Because both implementations satisfy the
exact same contract and return the same `ChatResponse` / `HealthStatus`
shapes, `Client` (and your application code) can treat any registered
provider interchangeably — the only thing that changes between Bedrock and
OpenAI is which `Config` subclass you build and the `provider` string you
pass in.

If you want to add support for another vendor, see `CONTRIBUTING.md` for the
steps to implement and register a new `BaseProvider`.
