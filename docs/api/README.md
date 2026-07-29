# API Reference

This folder is a placeholder for generated API reference documentation.
Nothing here is generated yet.

## How this will work

Neuravo's public modules (`core/`, `providers/`, `chat/`, `observability/`,
`cost/`, and the rest) are documented via docstrings on every public class
and function. The plan is to generate HTML reference docs from those
docstrings with [Sphinx](https://www.sphinx-doc.org/), which is already
listed in the project's `dev` extra:

```bash
pip install -e ".[dev]"
```

That pulls in `sphinx` and `sphinx-rtd-theme` alongside the rest of the
dev tooling (pytest, mypy, ruff, etc.). From there, the usual Sphinx
workflow applies: a `docs/conf.py` plus `sphinx-apidoc` (or hand-written
`.rst`/`.md` source files) to pull in the `neuravo` package's docstrings,
then `sphinx-build` to render them to HTML. That wiring — the Sphinx
config, the source files, and the build output — doesn't exist in this
repository yet; this folder will hold the generated output once it does.

## Where to look right now

Until the generated docs exist, the docstrings themselves are the
authoritative API reference. Every public module has them, including
argument/return descriptions and, where useful, runnable examples. Read
them directly in source, for example:

- `src/neuravo/core/` — `Client`, `Config`, exceptions, core types
  (`ChatResponse`, `TokenUsage`, `Message`, ...)
- `src/neuravo/providers/` — `BaseProvider` contract, Bedrock and OpenAI
  provider implementations, `ProviderRegistry`
- `src/neuravo/chat/` — conversation history management
- `src/neuravo/observability/` — `Tracer`, `MetricsRegistry`, `Monitor`,
  `CloudWatchExporter`, logging/redaction (see [`../observability.md`](../observability.md)
  for a narrative walkthrough with verified examples)
- `src/neuravo/cost/` — pricing table, `calculate_cost`, `CostTracker`
  (see [`../cost.md`](../cost.md))
- `src/neuravo/evaluation/`, `src/neuravo/prompts/`, `src/neuravo/benchmark/`,
  `src/neuravo/security/`, `src/neuravo/workflows/`, `src/neuravo/plugins/` —
  the rest of the capabilities listed in [`../roadmap.md`](../roadmap.md)

Your editor's "go to definition" / hover-docs on any import from `neuravo`
will surface the same docstrings without leaving your code.
