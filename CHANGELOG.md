# Changelog

All notable changes to Neuravo SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Package version is still `0.1.0` in `pyproject.toml` - the items below are
real, working, tested code already on this branch, not a roadmap. They
haven't been cut as a formal release yet.

### Added
- **Observability**: `Tracer` (nested spans), `MetricsRegistry` (Counter/Gauge/Histogram), `CloudWatchExporter`
- **Cost Intelligence**: per-model pricing table, `CostTracker` with running totals and per-model breakdown
- **OpenAI provider** (`neuravo[openai]` extra) - same `BaseProvider` contract as Bedrock, so it's a drop-in alternative via `Config(provider="openai")`
- **Evaluation**: `PromptTemplate`-driven `EvalCase`s, `EvaluationRunner`, `exact_match`/`contains`/`regex_match` scorers
- **Prompt Management**: `PromptTemplate` with named placeholders, versioned `PromptRegistry`
- **Benchmark**: `run_benchmark` for per-call latency stats (mean/percentile) against any client
- **Security**: `SecurityPolicy` (block-list prompt checks + output redaction)
- **Workflow Engine**: sequential `Step`/`Workflow` pipeline over a shared context
- **Plugin System**: entry-point-based discovery (`neuravo.plugins` group) with per-plugin failure isolation

### Not yet implemented (still stub/placeholder)
- `cache/`, `retry/rate_limit.py`, `retry/timeout.py`, `utils/decorators.py`, `utils/formatting.py` - present but unimplemented
- `agents/`, `embeddings/`, `memory/`, `tools/` - empty packages reserved for future work, not in the current growth plan

## [0.1.0] - 2024

### Added
- Initial release (MVP)
- AWS Bedrock provider support
- Chat feature with streaming
- Retry logic with exponential backoff
- Timeout management
- Configuration management with Pydantic
- Comprehensive logging with sensitive data redaction
- Type hints for all public APIs
- Unit, integration, and property-based tests
- Documentation and examples

### Features
- Chat conversations with message history
- Streaming responses
- Error handling and recovery
- Extensible architecture for additional providers

---

Changelog started with v0.1.0 release.
