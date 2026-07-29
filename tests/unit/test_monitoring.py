"""Tests for the observability Monitor."""

from neuravo.observability.monitoring import Monitor, get_monitor


def test_record_request_tracks_success_and_failure_counts():
    monitor = Monitor()

    monitor.record_request(duration_ms=100.0, success=True)
    monitor.record_request(duration_ms=200.0, success=False, error_type="Timeout")

    snapshot = monitor.get_snapshot()
    assert snapshot.requests_total == 2
    assert snapshot.requests_succeeded == 1
    assert snapshot.requests_failed == 1
    assert snapshot.errors_by_type == {"Timeout": 1}


def test_record_request_tracks_average_latency():
    monitor = Monitor()

    monitor.record_request(duration_ms=100.0, success=True)
    monitor.record_request(duration_ms=300.0, success=True)

    assert monitor.get_snapshot().avg_latency_ms == 200.0


def test_record_request_groups_errors_by_type():
    monitor = Monitor()

    monitor.record_request(duration_ms=1.0, success=False, error_type="Timeout")
    monitor.record_request(duration_ms=1.0, success=False, error_type="Timeout")
    monitor.record_request(duration_ms=1.0, success=False, error_type="ProviderError")

    errors = monitor.get_snapshot().errors_by_type
    assert errors == {"Timeout": 2, "ProviderError": 1}


def test_get_snapshot_returns_independent_copy():
    monitor = Monitor()
    monitor.record_request(duration_ms=1.0, success=False, error_type="Timeout")

    snapshot = monitor.get_snapshot()
    snapshot.errors_by_type["Timeout"] = 999
    snapshot.requests_total = 999

    fresh = monitor.get_snapshot()
    assert fresh.errors_by_type == {"Timeout": 1}
    assert fresh.requests_total == 1


def test_reset_clears_all_metrics():
    monitor = Monitor()
    monitor.record_request(duration_ms=100.0, success=True)

    monitor.reset()

    snapshot = monitor.get_snapshot()
    assert snapshot.requests_total == 0
    assert snapshot.requests_succeeded == 0
    assert snapshot.avg_latency_ms == 0.0
    assert snapshot.errors_by_type == {}


def test_get_monitor_returns_singleton():
    assert get_monitor() is get_monitor()
