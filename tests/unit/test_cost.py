"""Tests for cost calculation and tracking."""

import pytest

from neuravo.core.types import TokenUsage
from neuravo.cost import CostTracker, calculate_cost, get_pricing


def test_calculate_cost_uses_input_and_output_rates():
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=1000, total_tokens=2000)
    cost = calculate_cost(usage, "anthropic.claude-3-haiku-20240307-v1:0")

    assert cost == pytest.approx(0.00025 + 0.00125)


def test_calculate_cost_unknown_model_raises():
    usage = TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2)
    with pytest.raises(KeyError):
        calculate_cost(usage, "unknown-model")


def test_get_pricing_returns_none_for_unknown_model():
    assert get_pricing("unknown-model") is None


def test_tracker_accumulates_across_calls():
    tracker = CostTracker()
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=0, total_tokens=1000)

    cost1 = tracker.record("anthropic.claude-3-haiku-20240307-v1:0", usage)
    cost2 = tracker.record("anthropic.claude-3-haiku-20240307-v1:0", usage)

    snapshot = tracker.get_snapshot()
    assert snapshot.total_calls == 2
    assert snapshot.total_cost_usd == pytest.approx(cost1 + cost2)
    assert snapshot.cost_by_model["anthropic.claude-3-haiku-20240307-v1:0"] == pytest.approx(
        cost1 + cost2
    )


def test_tracker_breaks_down_cost_by_model():
    tracker = CostTracker()
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=1000, total_tokens=2000)

    tracker.record("anthropic.claude-3-haiku-20240307-v1:0", usage)
    tracker.record("meta.llama2-70b-chat-v1", usage)

    by_model = tracker.get_snapshot().cost_by_model
    assert set(by_model.keys()) == {
        "anthropic.claude-3-haiku-20240307-v1:0",
        "meta.llama2-70b-chat-v1",
    }


def test_get_snapshot_returns_independent_copy():
    tracker = CostTracker()
    tracker.record(
        "anthropic.claude-3-haiku-20240307-v1:0",
        TokenUsage(prompt_tokens=1000, completion_tokens=0, total_tokens=1000),
    )

    snapshot = tracker.get_snapshot()
    snapshot.total_cost_usd = 999.0
    snapshot.cost_by_model["anthropic.claude-3-haiku-20240307-v1:0"] = 999.0

    fresh = tracker.get_snapshot()
    assert fresh.total_cost_usd != 999.0


def test_reset_clears_tracker():
    tracker = CostTracker()
    tracker.record(
        "anthropic.claude-3-haiku-20240307-v1:0",
        TokenUsage(prompt_tokens=1000, completion_tokens=0, total_tokens=1000),
    )

    tracker.reset()

    snapshot = tracker.get_snapshot()
    assert snapshot.total_calls == 0
    assert snapshot.total_cost_usd == 0.0
    assert snapshot.cost_by_model == {}
