"""A single workflow step."""

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

StepAction = Callable[[Dict[str, Any]], Awaitable[Optional[Dict[str, Any]]]]


@dataclass
class Step:
    """One unit of work in a Workflow.

    Attributes:
        name: Human-readable step name, used in error messages
        action: Async callable that receives the current context dict and
            returns a dict of updates to merge into it (or None for a step
            that only performs a side effect, e.g. logging or validation)
    """

    name: str
    action: StepAction
