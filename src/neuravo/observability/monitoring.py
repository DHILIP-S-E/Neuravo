"""Monitoring and observability infrastructure.

Provides metrics collection and observability features.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Dict, Optional


@dataclass
class MetricsSnapshot:
    """Snapshot of system metrics.

    Attributes:
        timestamp: When metrics were collected
        requests_total: Total requests processed
        requests_succeeded: Successful requests
        requests_failed: Failed requests
        avg_latency_ms: Average request latency
        errors_by_type: Error counts by type
    """

    timestamp: datetime = field(default_factory=datetime.now)
    requests_total: int = 0
    requests_succeeded: int = 0
    requests_failed: int = 0
    avg_latency_ms: float = 0.0
    errors_by_type: Dict[str, int] = field(default_factory=dict)


class Monitor:
    """Monitors SDK operations and collects metrics.

    Tracks request metrics, error rates, and performance indicators.
    """

    def __init__(self) -> None:
        """Initialize monitor."""
        self.metrics = MetricsSnapshot()

    def record_request(
        self,
        duration_ms: float,
        success: bool,
        error_type: Optional[str] = None,
    ) -> None:
        """Record request metrics.

        Args:
            duration_ms: Request duration in milliseconds
            success: Whether request succeeded
            error_type: Error type if request failed
        """
        self.metrics.requests_total += 1
        if success:
            self.metrics.requests_succeeded += 1
        else:
            self.metrics.requests_failed += 1
            if error_type:
                self.metrics.errors_by_type[error_type] = (
                    self.metrics.errors_by_type.get(error_type, 0) + 1
                )

        # Running average over all requests seen so far.
        previous_total = self.metrics.requests_total - 1
        self.metrics.avg_latency_ms = (
            self.metrics.avg_latency_ms * previous_total + duration_ms
        ) / self.metrics.requests_total

    def get_snapshot(self) -> MetricsSnapshot:
        """Get current metrics snapshot.

        Returns a copy so callers can't mutate the monitor's internal state
        through the returned object.

        Returns:
            Current metrics snapshot
        """
        return replace(self.metrics, errors_by_type=dict(self.metrics.errors_by_type))

    def reset(self) -> None:
        """Reset metrics."""
        self.metrics = MetricsSnapshot()


# Global monitor instance
_monitor: Optional[Monitor] = None


def get_monitor() -> Monitor:
    """Get global monitor instance.

    Returns:
        Monitor instance
    """
    global _monitor
    if _monitor is None:
        _monitor = Monitor()
    return _monitor
