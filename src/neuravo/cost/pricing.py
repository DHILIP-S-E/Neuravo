"""Per-model pricing table and cost calculation.

Rates are USD per 1,000 tokens and are illustrative defaults only - AWS
Bedrock pricing changes over time and varies by region, so callers running
real cost tracking should override `PRICING` with current published rates
rather than trust these as billing-accurate.
"""

from dataclasses import dataclass
from typing import Dict, Optional

from neuravo.core.types import TokenUsage


@dataclass(frozen=True)
class ModelPricing:
    """Price per 1,000 tokens for a single model.

    Attributes:
        input_per_1k: USD per 1,000 prompt tokens
        output_per_1k: USD per 1,000 completion tokens
    """

    input_per_1k: float
    output_per_1k: float


# Indicative rates as of this writing - verify against AWS's published
# Bedrock pricing before relying on these for real cost accounting.
PRICING: Dict[str, ModelPricing] = {
    "anthropic.claude-3-sonnet-20240229-v1:0": ModelPricing(
        input_per_1k=0.003, output_per_1k=0.015
    ),
    "anthropic.claude-3-haiku-20240307-v1:0": ModelPricing(
        input_per_1k=0.00025, output_per_1k=0.00125
    ),
    "meta.llama2-70b-chat-v1": ModelPricing(input_per_1k=0.00195, output_per_1k=0.00256),
}


def calculate_cost(usage: TokenUsage, model: str) -> float:
    """Calculate the USD cost of a single call's token usage.

    Args:
        usage: Token usage for the call
        model: Model identifier used for the call

    Returns:
        Cost in USD

    Raises:
        KeyError: If no pricing is registered for the given model
    """
    pricing = PRICING[model]
    return (
        usage.prompt_tokens / 1000 * pricing.input_per_1k
        + usage.completion_tokens / 1000 * pricing.output_per_1k
    )


def get_pricing(model: str) -> Optional[ModelPricing]:
    """Look up pricing for a model without raising if it's unknown.

    Args:
        model: Model identifier

    Returns:
        ModelPricing if known, else None
    """
    return PRICING.get(model)
