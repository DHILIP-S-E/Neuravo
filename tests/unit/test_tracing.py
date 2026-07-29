"""Tests for the observability Tracer."""

import pytest

from neuravo.observability.tracing import Tracer


def test_start_span_records_duration_and_attributes():
    tracer = Tracer()

    with tracer.start_span("bedrock.chat", model="claude-3-haiku") as span:
        assert span.duration_ms is None  # not yet finished

    recorded = tracer.get_spans()
    assert len(recorded) == 1
    assert recorded[0].name == "bedrock.chat"
    assert recorded[0].attributes == {"model": "claude-3-haiku"}
    assert recorded[0].duration_ms is not None
    assert recorded[0].duration_ms >= 0


def test_nested_spans_record_parent_id():
    tracer = Tracer()

    with tracer.start_span("outer") as outer:
        with tracer.start_span("inner"):
            pass

    spans = {s.name: s for s in tracer.get_spans()}
    assert spans["outer"].parent_id is None
    assert spans["inner"].parent_id == outer.span_id


def test_span_records_error_and_reraises():
    tracer = Tracer()

    with pytest.raises(ValueError):
        with tracer.start_span("risky"):
            raise ValueError("boom")

    recorded = tracer.get_spans()
    assert recorded[0].error == "boom"


def test_reset_clears_spans():
    tracer = Tracer()
    with tracer.start_span("a"):
        pass

    tracer.reset()

    assert tracer.get_spans() == []
