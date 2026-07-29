"""Core abstractions and interfaces for Neuravo SDK.

This module provides fundamental abstractions that all components depend on:
- Exception hierarchy for error handling
- Type definitions shared across SDK
- Configuration structures and validation
- Logging infrastructure
- Base client interface

The core layer has no provider-specific imports and defines all abstractions
that other layers depend on.
"""

from neuravo.core.client import BaseClient
from neuravo.core.config import Config
from neuravo.core.exceptions import (
    ConfigError,
    NeurevoError,
    ProviderError,
    RetryExhaustedError,
    StreamingError,
    TimeoutError,
    ValidationError,
)
from neuravo.core.types import ChatResponse, HealthStatus, Message, TokenUsage

__all__ = [
    "NeurevoError",
    "ProviderError",
    "ConfigError",
    "TimeoutError",
    "RetryExhaustedError",
    "ValidationError",
    "StreamingError",
    "Message",
    "ChatResponse",
    "TokenUsage",
    "HealthStatus",
    "Config",
    "BaseClient",
]
