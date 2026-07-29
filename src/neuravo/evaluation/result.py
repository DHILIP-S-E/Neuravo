"""Evaluation result types."""

from dataclasses import dataclass, field
from typing import List, Optional

from neuravo.evaluation.case import EvalCase


@dataclass
class EvalResult:
    """Outcome of running a single EvalCase.

    Attributes:
        case: The case that was run
        response_text: The model's response text, if the call succeeded
        passed: Whether the scorer judged the response a pass
        error: Error message if the call itself failed (passed is False)
    """

    case: EvalCase
    response_text: Optional[str]
    passed: bool
    error: Optional[str] = None


@dataclass
class EvalSummary:
    """Aggregate outcome of an evaluation run.

    Attributes:
        results: Per-case results, in the order they were run
        total: Total number of cases run
        passed: Number of cases that passed
        failed: Number of cases that failed (includes call errors)
        pass_rate: passed / total, or 0.0 if there were no cases
    """

    results: List[EvalResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total number of cases run.

        Returns:
            Count of results
        """
        return len(self.results)

    @property
    def passed(self) -> int:
        """Number of cases that passed.

        Returns:
            Count of passing results
        """
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        """Number of cases that failed.

        Returns:
            Count of failing results
        """
        return self.total - self.passed

    @property
    def pass_rate(self) -> float:
        """Fraction of cases that passed.

        Returns:
            passed / total, or 0.0 if there were no cases
        """
        if self.total == 0:
            return 0.0
        return self.passed / self.total
