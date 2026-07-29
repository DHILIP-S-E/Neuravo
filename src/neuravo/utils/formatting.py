"""Data formatting utilities.

Provides utilities for formatting output and error messages.
"""

from typing import Any, Dict


def format_error_message(error_code: str, message: str, details: Dict[str, Any] = None) -> str:
    """Format error message for display.

    Args:
        error_code: Error code
        message: Error message
        details: Optional error details

    Returns:
        Formatted error message
    """
    pass


def format_response(content: str, max_length: int = 500) -> str:
    """Format response for display.

    Args:
        content: Response content
        max_length: Maximum display length

    Returns:
        Formatted response
    """
    pass


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    pass
