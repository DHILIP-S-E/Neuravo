"""Tests for the sequential workflow engine."""

import pytest

from neuravo.core.exceptions import WorkflowError
from neuravo.workflows import Step, Workflow


@pytest.mark.asyncio
async def test_steps_run_in_order_and_share_context():
    order = []

    async def step_a(ctx):
        order.append("a")
        return {"a_ran": True}

    async def step_b(ctx):
        order.append("b")
        assert ctx["a_ran"] is True
        return {"b_ran": True}

    workflow = Workflow([Step("a", step_a), Step("b", step_b)])
    result = await workflow.run()

    assert order == ["a", "b"]
    assert result == {"a_ran": True, "b_ran": True}


@pytest.mark.asyncio
async def test_initial_context_is_available_to_first_step():
    async def greet(ctx):
        return {"greeting": f"Hello, {ctx['name']}!"}

    workflow = Workflow([Step("greet", greet)])
    result = await workflow.run({"name": "Ada"})

    assert result["greeting"] == "Hello, Ada!"


@pytest.mark.asyncio
async def test_initial_context_is_not_mutated():
    async def step(ctx):
        return {"new_key": "value"}

    initial = {"name": "Ada"}
    workflow = Workflow([Step("step", step)])
    await workflow.run(initial)

    assert initial == {"name": "Ada"}


@pytest.mark.asyncio
async def test_step_returning_none_leaves_context_unchanged():
    async def side_effect_only(ctx):
        return None

    workflow = Workflow([Step("noop", side_effect_only)])
    result = await workflow.run({"x": 1})

    assert result == {"x": 1}


@pytest.mark.asyncio
async def test_failing_step_raises_workflow_error_naming_the_step():
    async def boom(ctx):
        raise RuntimeError("kaboom")

    workflow = Workflow([Step("risky-step", boom)])

    with pytest.raises(WorkflowError) as exc_info:
        await workflow.run()

    assert exc_info.value.step_name == "risky-step"


@pytest.mark.asyncio
async def test_step_after_a_failure_does_not_run():
    ran = []

    async def boom(ctx):
        raise RuntimeError("kaboom")

    async def never_runs(ctx):
        ran.append("should not happen")
        return None

    workflow = Workflow([Step("boom", boom), Step("after", never_runs)])

    with pytest.raises(WorkflowError):
        await workflow.run()

    assert ran == []
