"""Lightweight tracing for Neuravo SDK operations.

A minimal span/trace implementation - no OpenTelemetry dependency here.
OTel is a future integration (see the growth plan's integrations/opentelemetry
module); this is the internal tracer the SDK itself uses and that an OTel
bridge could later export from.
"""

import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

_current_span_id: ContextVar[Optional[str]] = ContextVar("_current_span_id", default=None)


@dataclass
class Span:
    """A single traced operation.

    Attributes:
        span_id: Unique identifier for this span
        parent_id: The enclosing span's id, if any
        name: Operation name (e.g. "bedrock.chat")
        start_time: When the span started
        duration_ms: How long the span took, set when it ends
        attributes: Arbitrary key/value metadata attached to the span
        error: Error message if the operation raised, else None
    """

    span_id: str
    parent_id: Optional[str]
    name: str
    start_time: datetime
    duration_ms: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class Tracer:
    """Collects spans for SDK operations.

    Spans nest via the current context: starting a span while another is
    active makes the new one a child of it.
    """

    def __init__(self) -> None:
        """Initialize the tracer with no recorded spans."""
        self.spans: List[Span] = []

    @contextmanager
    def start_span(self, name: str, **attributes: Any) -> Iterator[Span]:
        """Start a span for the duration of the ``with`` block.

        Args:
            name: Operation name for this span
            **attributes: Arbitrary metadata to attach to the span

        Yields:
            The Span, so callers can add attributes or read its id
        """
        parent_id = _current_span_id.get()
        span = Span(
            span_id=str(uuid.uuid4()),
            parent_id=parent_id,
            name=name,
            start_time=datetime.now(),
            attributes=dict(attributes),
        )
        token = _current_span_id.set(span.span_id)
        start = time.perf_counter()
        try:
            yield span
        except Exception as exc:
            span.error = str(exc)
            raise
        finally:
            span.duration_ms = (time.perf_counter() - start) * 1000
            self.spans.append(span)
            _current_span_id.reset(token)

    def get_spans(self) -> List[Span]:
        """Get all recorded spans, oldest first.

        Returns:
            List of completed spans
        """
        return list(self.spans)

    def reset(self) -> None:
        """Clear all recorded spans."""
        self.spans = []


_tracer: Optional[Tracer] = None


def get_tracer() -> Tracer:
    """Get the global tracer instance.

    Returns:
        Tracer instance
    """
    global _tracer
    if _tracer is None:
        _tracer = Tracer()
    return _tracer
