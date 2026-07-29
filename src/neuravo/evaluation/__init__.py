"""Evaluation capability for Neuravo SDK.

Run a batch of prompts through a client and score the responses against
expected values, using pluggable scorer functions.

Examples:
    Basic evaluation::

        from neuravo import Client, Config
        from neuravo.evaluation import EvalCase, EvaluationRunner
        from neuravo.evaluation.scorers import contains

        client = Client(Config(provider="bedrock", region="us-east-1"))
        cases = [
            EvalCase(prompt="What is 2+2?", expected="4", scorer=contains),
        ]
        summary = await EvaluationRunner(client).run(cases)
        print(f"{summary.passed}/{summary.total} passed")
"""

from neuravo.evaluation.case import EvalCase
from neuravo.evaluation.result import EvalResult, EvalSummary
from neuravo.evaluation.runner import EvaluationRunner

__all__ = [
    "EvalCase",
    "EvalResult",
    "EvalSummary",
    "EvaluationRunner",
]
