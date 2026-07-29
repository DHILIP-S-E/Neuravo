"""Common decorators used throughout SDK.

Provides reusable decorators for logging, error handling, and other cross-cutting concerns.
"""

import asyncio
from functools import wraps
from typing import Any, Callable


def log_execution(func: Callable) -> Callable:
    """Decorator to log function execution.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        """Async wrapper."""
        pass

    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        """Sync wrapper."""
        pass

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def handle_errors(func: Callable) -> Callable:
    """Decorator for consistent error handling.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        """Error handling wrapper."""
        pass

    return wrapper
