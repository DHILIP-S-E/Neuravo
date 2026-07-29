"""Evaluation runner.

Runs a batch of EvalCases through a client and scores the responses.
"""

from typing import List

from neuravo.core.client import BaseClient
from neuravo.evaluation.case import EvalCase
from neuravo.evaluation.result import EvalResult, EvalSummary


class EvaluationRunner:
    """Runs EvalCases against a client and collects scored results.

    Attributes:
        client: The client used to send each case's prompt
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the runner.

        Args:
            client: Client to send each case's prompt through
        """
        self.client = client

    async def run(self, cases: List[EvalCase]) -> EvalSummary:
        """Run every case and return the aggregate outcome.

        A case whose client call raises is recorded as a failed result
        rather than aborting the rest of the run - one bad case shouldn't
        prevent scoring the others.

        Args:
            cases: Evaluation cases to run, in order

        Returns:
            EvalSummary with one EvalResult per case
        """
        results = [await self.run_one(case) for case in cases]
        return EvalSummary(results=results)

    async def run_one(self, case: EvalCase) -> EvalResult:
        """Run a single case and score its response.

        Args:
            case: Evaluation case to run

        Returns:
            EvalResult for this case
        """
        try:
            response = await self.client.chat(case.prompt)
        except Exception as exc:  # noqa: BLE001 - one bad case must not abort the run
            return EvalResult(case=case, response_text=None, passed=False, error=str(exc))

        passed = case.scorer(response.content, case.expected)
        return EvalResult(case=case, response_text=response.content, passed=passed)
