"""Evaluation case definition."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from neuravo.evaluation.scorers import exact_match


@dataclass
class EvalCase:
    """A single prompt to send and a way to judge the response.

    Attributes:
        prompt: The input to send to the client
        expected: The expected value passed to the scorer (meaning depends
            on the scorer - e.g. the exact text, or a regex pattern)
        scorer: Callable(actual_response_text, expected) -> bool
        name: Human-readable case name for reporting (defaults to the prompt)
        metadata: Arbitrary extra data carried through to the result
    """

    prompt: str
    expected: Optional[str] = None
    scorer: Callable[[str, Optional[str]], bool] = exact_match
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def display_name(self) -> str:
        """Human-readable label for this case, for reporting.

        Returns:
            The case's name, or its prompt if no name was given
        """
        return self.name or self.prompt
