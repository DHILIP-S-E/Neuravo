"""Spend tracking across calls."""

from dataclasses import dataclass, field, replace
from typing import Dict

from neuravo.core.types import TokenUsage
from neuravo.cost.pricing import calculate_cost


@dataclass
class CostSnapshot:
    """Accumulated spend at a point in time.

    Attributes:
        total_cost_usd: Total spend across all recorded calls
        total_calls: Number of calls recorded
        cost_by_model: Spend broken down per model
    """

    total_cost_usd: float = 0.0
    total_calls: int = 0
    cost_by_model: Dict[str, float] = field(default_factory=dict)


class CostTracker:
    """Accumulates cost across chat calls, by model.

    Examples:
        Track cost after each call::

            tracker = CostTracker()
            response = await client.chat("Hello")
            tracker.record(response.model, response.usage)
            print(tracker.get_snapshot().total_cost_usd)
    """

    def __init__(self) -> None:
        """Initialize the tracker with zero recorded spend."""
        self.snapshot = CostSnapshot()

    def record(self, model: str, usage: TokenUsage) -> float:
        """Record one call's usage and return its cost.

        Args:
            model: Model identifier used for the call
            usage: Token usage for the call

        Returns:
            Cost of this call in USD

        Raises:
            KeyError: If no pricing is registered for the given model
        """
        cost = calculate_cost(usage, model)
        self.snapshot.total_cost_usd += cost
        self.snapshot.total_calls += 1
        self.snapshot.cost_by_model[model] = self.snapshot.cost_by_model.get(model, 0.0) + cost
        return cost

    def get_snapshot(self) -> CostSnapshot:
        """Get accumulated spend so far.

        Returns a copy so callers can't mutate the tracker's internal
        state through the returned object.

        Returns:
            CostSnapshot with current totals
        """
        return replace(self.snapshot, cost_by_model=dict(self.snapshot.cost_by_model))

    def reset(self) -> None:
        """Clear all recorded spend."""
        self.snapshot = CostSnapshot()
