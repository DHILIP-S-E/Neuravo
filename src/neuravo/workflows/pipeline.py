"""Sequential workflow execution.

A deliberately simple engine: an ordered list of steps sharing one context
dict, run one after another. No branching, retries, or parallel steps -
those are real future extensions once a sequential pipeline proves not to
be enough, not something to guess the shape of upfront.
"""

from typing import Any, Dict, List, Optional

from neuravo.core.exceptions import WorkflowError
from neuravo.workflows.step import Step


class Workflow:
    """Runs a fixed sequence of steps against a shared context.

    Examples:
        Build and run a two-step workflow::

            async def fetch(ctx):
                return {"raw": await get_data(ctx["url"])}

            async def summarize(ctx):
                return {"summary": await client.chat(f"Summarize: {ctx['raw']}")}

            workflow = Workflow([Step("fetch", fetch), Step("summarize", summarize)])
            result = await workflow.run({"url": "https://example.com"})
    """

    def __init__(self, steps: List[Step]) -> None:
        """Initialize the workflow.

        Args:
            steps: Steps to run, in order
        """
        self.steps = steps

    async def run(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run every step in order against a shared context.

        Args:
            context: Initial context values (not mutated - a copy is used)

        Returns:
            The final context after every step has run

        Raises:
            WorkflowError: If a step raises - `step_name` on the error
                identifies which one
        """
        ctx = dict(context or {})
        for step in self.steps:
            try:
                updates = await step.action(ctx)
            except Exception as exc:
                raise WorkflowError(step.name, f"Step '{step.name}' failed: {exc}") from exc
            if updates:
                ctx.update(updates)
        return ctx
