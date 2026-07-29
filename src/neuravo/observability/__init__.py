"""Observability capability for Neuravo SDK.

Provides logging (with sensitive-data redaction), in-process request
monitoring, named metrics, lightweight tracing, and a CloudWatch exporter.
An OpenTelemetry bridge remains a future integration (see the growth plan).
"""

from neuravo.observability.exporters import CloudWatchExporter
from neuravo.observability.logging import get_logger, setup_logging
from neuravo.observability.metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricsRegistry,
    get_metrics_registry,
)
from neuravo.observability.monitoring import get_monitor
from neuravo.observability.tracing import Span, Tracer, get_tracer

__all__ = [
    "setup_logging",
    "get_logger",
    "get_monitor",
    "Counter",
    "Gauge",
    "Histogram",
    "MetricsRegistry",
    "get_metrics_registry",
    "Span",
    "Tracer",
    "get_tracer",
    "CloudWatchExporter",
]
