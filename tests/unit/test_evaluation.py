"""Tests for the evaluation module, against a fake client (no AWS calls)."""

from datetime import datetime
from typing import AsyncIterator, List

import pytest

from neuravo.core.client import BaseClient
from neuravo.core.config import Config
from neuravo.core.types import ChatResponse, HealthStatus, Message, TokenUsage
from neuravo.evaluation import EvalCase, EvaluationRunner
from neuravo.evaluation.scorers import contains, exact_match, regex_match


class ScriptedClient(BaseClient):
    """Fake client that returns a fixed response per prompt, or raises."""

    def __init__(self, config: Config, responses: dict, raises_for: set = frozenset()):
        super().__init__(config)
        self.responses = responses
        self.raises_for = raises_for

    async def initialize(self) -> None:
        pass

    async def chat(self, prompt: str) -> ChatResponse:
        if prompt in self.raises_for:
            raise RuntimeError(f"simulated failure for: {prompt}")
        return ChatResponse(
            content=self.responses[prompt],
            model="fake-model",
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            timestamp=datetime.now(),
            provider="fake",
        )

    async def stream(self, prompt: str) -> AsyncIterator[ChatResponse]:
        yield await self.chat(prompt)

    async def get_chat_history(self) -> List[Message]:
        return []

    async def clear_history(self) -> None:
        pass

    async def health_check(self) -> HealthStatus:
        return HealthStatus(is_healthy=True, latency_ms=0.0)

    async def close(self) -> None:
        pass


def _client(responses, raises_for=frozenset()):
    return ScriptedClient(Config(provider="fake", region="us-east-1"), responses, raises_for)


def test_exact_match_scorer():
    assert exact_match("4", "4") is True
    assert exact_match("four", "4") is False


def test_contains_scorer_is_case_insensitive():
    assert contains("The answer is 4.", "answer") is True
    assert contains("The ANSWER is 4.", "answer") is True
    assert contains("nope", "answer") is False


def test_regex_match_scorer():
    assert regex_match("The answer is 42", r"\d+") is True
    assert regex_match("no digits here", r"\d+") is False


@pytest.mark.asyncio
async def test_runner_scores_passing_and_failing_cases():
    client = _client({"2+2?": "4", "capital of France?": "London"})
    cases = [
        EvalCase(prompt="2+2?", expected="4", scorer=exact_match),
        EvalCase(prompt="capital of France?", expected="Paris", scorer=exact_match),
    ]

    summary = await EvaluationRunner(client).run(cases)

    assert summary.total == 2
    assert summary.passed == 1
    assert summary.failed == 1
    assert summary.pass_rate == 0.5


@pytest.mark.asyncio
async def test_runner_records_client_errors_as_failures_without_aborting():
    client = _client({"ok?": "yes"}, raises_for={"boom?"})
    cases = [
        EvalCase(prompt="boom?", expected="anything", scorer=exact_match),
        EvalCase(prompt="ok?", expected="yes", scorer=exact_match),
    ]

    summary = await EvaluationRunner(client).run(cases)

    assert summary.total == 2
    assert summary.results[0].passed is False
    assert summary.results[0].error is not None
    assert summary.results[1].passed is True


@pytest.mark.asyncio
async def test_empty_case_list_has_zero_pass_rate():
    summary = await EvaluationRunner(_client({})).run([])
    assert summary.total == 0
    assert summary.pass_rate == 0.0


def test_eval_case_display_name_defaults_to_prompt():
    case = EvalCase(prompt="hello")
    assert case.display_name() == "hello"
    named = EvalCase(prompt="hello", name="greeting-case")
    assert named.display_name() == "greeting-case"
