"""Common decorators used throughout SDK.

Provides reusable decorators for logging, error handling, and other cross-cutting concerns.
"""

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, TypeVar

from neuravo.core.exceptions import NeurevoError

F = TypeVar("F", bound=Callable[..., Any])


def log_execution(func: F) -> F:
    """Decorator to log function execution.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    logger = logging.getLogger(func.__module__)

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        """Async wrapper."""
        logger.debug("Executing %s", func.__qualname__)
        result = await func(*args, **kwargs)
        logger.debug("Completed %s", func.__qualname__)
        return result

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        """Sync wrapper."""
        logger.debug("Executing %s", func.__qualname__)
        result = func(*args, **kwargs)
        logger.debug("Completed %s", func.__qualname__)
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper  # type: ignore[return-value]
    return sync_wrapper  # type: ignore[return-value]


def handle_errors(func: F) -> F:
    """Decorator for consistent error handling.

    Wraps any exception that isn't already a NeurevoError so callers only
    ever need to catch the SDK's own exception hierarchy.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Error handling wrapper."""
        try:
            return await func(*args, **kwargs)
        except NeurevoError:
            raise
        except Exception as exc:
            raise NeurevoError(str(exc), "UNHANDLED_ERROR") from exc

    return wrapper  # type: ignore[return-value]
