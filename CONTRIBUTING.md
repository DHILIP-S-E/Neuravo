# Contributing to Neuravo

Thanks for your interest in contributing to Neuravo, a provider-agnostic Python
SDK for AI infrastructure (chat, streaming, retry, observability, cost tracking,
and more across providers like AWS Bedrock and OpenAI). This document covers
how to get set up, how the project is tested, and — because it's the most
common contribution — how to add a new provider.

## Getting started

Clone the repo and install it in editable mode with the dev extras:

```bash
git clone https://github.com/DHILIP-S-E/Neuravo.git
cd Neuravo
pip install -e ".[dev]"
```

This pulls in pytest, hypothesis, ruff, mypy, and the other tools used across
the CI workflows.

## Running the checks locally

Before opening a PR, run the same three checks that CI runs
(`.github/workflows/lint.yml`, `test.yml`, `type-check.yml`):

```bash
# Tests (176 passing as of this writing)
pytest

# Lint
ruff check src tests

# Type checking (strict mode)
mypy src
```

All three must pass. If `ruff` flags formatting issues, `ruff format src tests`
(or `black src tests`) will fix most of them automatically.

Tests are organized under `tests/` by kind: `unit/`, `integration/`,
`properties/` (hypothesis-based), and `performance/`. New code should
generally be covered by a unit test at minimum; provider code should also get
a properties or integration test where it makes sense.

## Branch and PR workflow

- Branch off `main`, one logical change per branch/PR.
- Keep PRs focused — if you find an unrelated issue while working, file it
  separately or mention it in the PR description rather than folding it in.
- Make sure `pytest`, `ruff check`, and `mypy src` all pass before requesting
  review (CI will re-run them anyway, but catching failures locally is
  faster for everyone).
- Update or add tests alongside behavioral changes — a PR that changes
  behavior without a corresponding test change will likely get asked to add
  one.
- Commit messages: there's no enforced convention (no Conventional Commits,
  no required prefixes) yet. Just write clear, descriptive messages that
  explain *why* the change was made, not just what changed.

## Adding a new provider

This is the single most structured type of contribution in this repo, so
follow the pattern exactly rather than improvising a new one. A new provider
under `src/neuravo/providers/<name>/` must do all of the following:

1. **Implement the full `BaseProvider` contract.** `BaseProvider`
   (`src/neuravo/providers/base.py`) is an ABC with seven methods:
   `initialize`, `validate_config`, `get_available_models`, `chat`,
   `stream_chat`, `health_check`, and `close`. Every method must be a real,
   working implementation — no `NotImplementedError` stubs, no "not
   supported for this provider" placeholders. If the underlying vendor SDK
   genuinely can't support one of these (e.g. no streaming API), that's a
   sign the method needs a real fallback implementation, not a stub — raise
   the question in the PR rather than shipping a stub.

2. **Self-register with `ProviderRegistry`.** In your
   `providers/<name>/__init__.py`, register the class on import:

   ```python
   from neuravo.providers.registry import ProviderRegistry
   from neuravo.providers.<name>.<module> import <Name>Provider

   ProviderRegistry.register("<name>", <Name>Provider)
   ```

   See `src/neuravo/providers/aws/__init__.py` for the exact pattern
   (including the try/except around registration used for test isolation).

3. **Add a contract-style test suite that mocks the vendor SDK — never the
   real network.** Tests live under `tests/unit/providers/<name>/`. Mock at
   the SDK boundary, not inside your own code:
   - For AWS-backed providers, use `botocore.stub.Stubber` against the real
     boto3 client, the way `tests/unit/providers/aws/test_bedrock.py` does —
     it stubs the `converse` operation with realistic request/response
     shapes so the test validates against the actual service model.
   - For OpenAI-style HTTP SDKs, use `unittest.mock.AsyncMock` around the
     SDK client, following `tests/unit/providers/openai/` as the reference.
   - At minimum, cover: missing/invalid config raising the right exception,
     a successful `chat()` call round-tripping a realistic response,
     `stream_chat()` yielding chunks correctly, and `health_check()`
     reflecting both healthy and unhealthy states.

**The reference implementation to copy from is
`src/neuravo/providers/aws/bedrock.py` paired with
`tests/unit/providers/aws/test_bedrock.py`.** If you're unsure how detailed
your implementation or tests need to be, match what's there rather than
guessing — it's the pattern reviewers will be checking your PR against.

A provider PR that's missing one of the seven `BaseProvider` methods, doesn't
self-register, or only has tests that mock your own wrapper code (instead of
the vendor SDK boundary) will be sent back for changes before review.

## Questions

If something in this doc is unclear or you're unsure how a change fits into
the existing architecture, open an issue or draft PR and ask — that's a
normal part of contributing here.
