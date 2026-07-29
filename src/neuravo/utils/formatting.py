"""Data formatting utilities.

Provides utilities for formatting output and error messages.
"""

from typing import Any, Dict, Optional


def format_error_message(
    error_code: str, message: str, details: Optional[Dict[str, Any]] = None
) -> str:
    """Format error message for display.

    Args:
        error_code: Error code
        message: Error message
        details: Optional error details

    Returns:
        Formatted error message
    """
    if not details:
        return f"[{error_code}] {message}"
    detail_str = ", ".join(f"{key}={value}" for key, value in details.items())
    return f"[{error_code}] {message} ({detail_str})"


def format_response(content: str, max_length: int = 500) -> str:
    """Format response for display.

    Args:
        content: Response content
        max_length: Maximum display length

    Returns:
        Formatted response
    """
    return truncate_string(content, max_length)


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    if max_length <= len(suffix):
        return suffix[:max_length]
    return text[: max_length - len(suffix)] + suffix
