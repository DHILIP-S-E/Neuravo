"""Named metric primitives for Neuravo SDK.

Simple counter/gauge/histogram types, in the same spirit as the existing
Monitor but usable for arbitrary named metrics rather than only the fixed
request/latency fields Monitor tracks.
"""

from typing import Dict, List, Optional


class Counter:
    """A monotonically increasing named value."""

    def __init__(self, name: str) -> None:
        """Initialize a counter at zero.

        Args:
            name: Metric name
        """
        self.name = name
        self.value = 0.0

    def inc(self, amount: float = 1.0) -> None:
        """Increase the counter.

        Args:
            amount: Amount to add (default 1.0)
        """
        self.value += amount


class Gauge:
    """A named value that can go up or down."""

    def __init__(self, name: str) -> None:
        """Initialize a gauge at zero.

        Args:
            name: Metric name
        """
        self.name = name
        self.value = 0.0

    def set(self, value: float) -> None:
        """Set the gauge to a specific value.

        Args:
            value: New value
        """
        self.value = value


class Histogram:
    """Records individual observations of a named value for later summary."""

    def __init__(self, name: str) -> None:
        """Initialize an empty histogram.

        Args:
            name: Metric name
        """
        self.name = name
        self.observations: List[float] = []

    def observe(self, value: float) -> None:
        """Record an observation.

        Args:
            value: Observed value
        """
        self.observations.append(value)

    def mean(self) -> float:
        """Mean of all observations.

        Returns:
            Mean, or 0.0 if there are no observations
        """
        if not self.observations:
            return 0.0
        return sum(self.observations) / len(self.observations)

    def percentile(self, p: float) -> float:
        """Nearest-rank percentile of all observations.

        Args:
            p: Percentile in [0, 100]

        Returns:
            The value at that percentile, or 0.0 if there are no observations

        Raises:
            ValueError: If p is not between 0 and 100
        """
        if not 0 <= p <= 100:
            raise ValueError("percentile must be between 0 and 100")
        if not self.observations:
            return 0.0
        ordered = sorted(self.observations)
        index = max(0, min(len(ordered) - 1, int(round(p / 100 * (len(ordered) - 1)))))
        return ordered[index]


class MetricsRegistry:
    """Creates and retrieves named metrics by type.

    Each name is scoped independently per metric type, so a Counter and a
    Gauge can share the same name without colliding.
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}

    def counter(self, name: str) -> Counter:
        """Get or create a named counter.

        Args:
            name: Metric name

        Returns:
            The Counter for this name
        """
        return self._counters.setdefault(name, Counter(name))

    def gauge(self, name: str) -> Gauge:
        """Get or create a named gauge.

        Args:
            name: Metric name

        Returns:
            The Gauge for this name
        """
        return self._gauges.setdefault(name, Gauge(name))

    def histogram(self, name: str) -> Histogram:
        """Get or create a named histogram.

        Args:
            name: Metric name

        Returns:
            The Histogram for this name
        """
        return self._histograms.setdefault(name, Histogram(name))


_registry: Optional[MetricsRegistry] = None


def get_metrics_registry() -> MetricsRegistry:
    """Get the global metrics registry.

    Returns:
        MetricsRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = MetricsRegistry()
    return _registry
