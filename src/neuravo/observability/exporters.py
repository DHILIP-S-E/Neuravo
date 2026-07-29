"""Metric exporters for Neuravo SDK.

Ships local metrics snapshots to an external system. CloudWatch is the
only exporter for now since boto3 is already a core dependency; other
destinations (Datadog, Prometheus push gateway, ...) are future additions
that would each need their own optional dependency.
"""

from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from neuravo.core.exceptions import ProviderError
from neuravo.observability.monitoring import MetricsSnapshot


class CloudWatchExporter:
    """Exports MetricsSnapshots to AWS CloudWatch as custom metrics.

    Never called automatically - a caller decides when (and how often) to
    export, since every export is a real (billed) AWS API call.
    """

    def __init__(self, namespace: str = "Neuravo", region: Optional[str] = None) -> None:
        """Initialize the exporter.

        Args:
            namespace: CloudWatch namespace to publish metrics under
            region: AWS region for the CloudWatch client (uses the default
                credential chain's region if not given)
        """
        self.namespace = namespace
        client_kwargs: Dict[str, Any] = {}
        if region:
            client_kwargs["region_name"] = region
        self.client = boto3.client("cloudwatch", **client_kwargs)

    def export_snapshot(self, snapshot: MetricsSnapshot) -> None:
        """Publish a metrics snapshot to CloudWatch.

        Args:
            snapshot: Snapshot to export (see Monitor.get_snapshot)

        Raises:
            ProviderError: If the CloudWatch API call fails
        """
        metric_data: List[Dict[str, Any]] = [
            {"MetricName": "RequestsTotal", "Value": snapshot.requests_total, "Unit": "Count"},
            {
                "MetricName": "RequestsSucceeded",
                "Value": snapshot.requests_succeeded,
                "Unit": "Count",
            },
            {"MetricName": "RequestsFailed", "Value": snapshot.requests_failed, "Unit": "Count"},
            {
                "MetricName": "AverageLatency",
                "Value": snapshot.avg_latency_ms,
                "Unit": "Milliseconds",
            },
        ]
        for error_type, count in snapshot.errors_by_type.items():
            metric_data.append(
                {
                    "MetricName": "ErrorsByType",
                    "Value": count,
                    "Unit": "Count",
                    "Dimensions": [{"Name": "ErrorType", "Value": error_type}],
                }
            )

        try:
            self.client.put_metric_data(Namespace=self.namespace, MetricData=metric_data)
        except (BotoCoreError, ClientError) as exc:
            raise ProviderError(f"Failed to export metrics to CloudWatch: {exc}") from exc
