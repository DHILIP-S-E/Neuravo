"""Cost intelligence capability for Neuravo SDK.

Token-usage cost calculation and spend tracking. Pricing data is
indicative only - see cost/pricing.py for the caveat on accuracy.

Examples:
    Track cost per call::

        from neuravo.cost import CostTracker

        tracker = CostTracker()
        response = await client.chat("Hello")
        cost = tracker.record(response.model, response.usage)
        print(f"This call cost ${cost:.4f}")
"""

from neuravo.cost.pricing import ModelPricing, calculate_cost, get_pricing
from neuravo.cost.tracker import CostSnapshot, CostTracker

__all__ = [
    "ModelPricing",
    "calculate_cost",
    "get_pricing",
    "CostSnapshot",
    "CostTracker",
]
