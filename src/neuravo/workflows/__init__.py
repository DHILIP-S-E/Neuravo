"""Workflow engine capability for Neuravo SDK.

A minimal sequential pipeline: an ordered list of Steps sharing one
context dict, run one after another.

Examples:
    Chain a fetch step and a chat step::

        from neuravo.workflows import Step, Workflow

        async def summarize(ctx):
            response = await ctx["client"].chat(f"Summarize: {ctx['text']}")
            return {"summary": response.content}

        workflow = Workflow([Step("summarize", summarize)])
        result = await workflow.run({"client": client, "text": "..."})
        print(result["summary"])
"""

from neuravo.workflows.pipeline import Workflow
from neuravo.workflows.step import Step, StepAction

__all__ = [
    "Step",
    "StepAction",
    "Workflow",
]
