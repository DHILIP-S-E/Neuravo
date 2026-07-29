"""Tests for named metric primitives."""

import pytest

from neuravo.observability.metrics import MetricsRegistry


def test_counter_increments():
    registry = MetricsRegistry()
    counter = registry.counter("requests")

    counter.inc()
    counter.inc(4.0)

    assert counter.value == 5.0


def test_gauge_holds_last_set_value():
    registry = MetricsRegistry()
    gauge = registry.gauge("queue_depth")

    gauge.set(3.0)
    gauge.set(7.0)

    assert gauge.value == 7.0


def test_histogram_mean_and_percentile():
    registry = MetricsRegistry()
    hist = registry.histogram("latency_ms")

    for value in [100, 200, 300, 400, 500]:
        hist.observe(value)

    assert hist.mean() == 300.0
    assert hist.percentile(0) == 100
    assert hist.percentile(100) == 500


def test_histogram_percentile_rejects_out_of_range():
    hist = MetricsRegistry().histogram("x")
    with pytest.raises(ValueError):
        hist.percentile(101)


def test_empty_histogram_returns_zero():
    hist = MetricsRegistry().histogram("empty")
    assert hist.mean() == 0.0
    assert hist.percentile(50) == 0.0


def test_registry_returns_same_instance_for_same_name():
    registry = MetricsRegistry()
    assert registry.counter("x") is registry.counter("x")


def test_counter_and_gauge_can_share_a_name():
    registry = MetricsRegistry()
    counter = registry.counter("shared")
    gauge = registry.gauge("shared")

    counter.inc()
    gauge.set(10.0)

    assert counter.value == 1.0
    assert gauge.value == 10.0
