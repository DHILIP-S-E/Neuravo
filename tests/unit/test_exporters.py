"""Tests for the CloudWatch metrics exporter, against a stubbed boto3 client."""

import pytest
from botocore.stub import Stubber

from neuravo.core.exceptions import ProviderError
from neuravo.observability.exporters import CloudWatchExporter
from neuravo.observability.monitoring import MetricsSnapshot


def test_export_snapshot_sends_expected_metric_data():
    exporter = CloudWatchExporter(namespace="NeuravoTest", region="us-east-1")
    stubber = Stubber(exporter.client)
    snapshot = MetricsSnapshot(
        requests_total=10,
        requests_succeeded=8,
        requests_failed=2,
        avg_latency_ms=123.4,
        errors_by_type={"Timeout": 2},
    )

    stubber.add_response(
        "put_metric_data",
        {},
        {
            "Namespace": "NeuravoTest",
            "MetricData": [
                {"MetricName": "RequestsTotal", "Value": 10, "Unit": "Count"},
                {"MetricName": "RequestsSucceeded", "Value": 8, "Unit": "Count"},
                {"MetricName": "RequestsFailed", "Value": 2, "Unit": "Count"},
                {"MetricName": "AverageLatency", "Value": 123.4, "Unit": "Milliseconds"},
                {
                    "MetricName": "ErrorsByType",
                    "Value": 2,
                    "Unit": "Count",
                    "Dimensions": [{"Name": "ErrorType", "Value": "Timeout"}],
                },
            ],
        },
    )
    stubber.activate()

    exporter.export_snapshot(snapshot)

    stubber.deactivate()
    stubber.assert_no_pending_responses()


def test_export_snapshot_wraps_client_errors():
    exporter = CloudWatchExporter(namespace="NeuravoTest", region="us-east-1")
    stubber = Stubber(exporter.client)
    stubber.add_client_error("put_metric_data", service_error_code="Throttling")
    stubber.activate()

    with pytest.raises(ProviderError):
        exporter.export_snapshot(MetricsSnapshot())

    stubber.deactivate()
