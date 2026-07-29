"""Scoring functions for evaluation cases.

A scorer takes the model's actual response text and the case's expected
value, and returns True if the response passes. Kept as plain functions
(not a class hierarchy) so a user's own scorer is just any callable with
this signature - no base class to inherit from.
"""

import re
from typing import Optional


def exact_match(actual: str, expected: Optional[str]) -> bool:
    """Pass only if the response equals expected exactly.

    Args:
        actual: The model's response text
        expected: The expected text to match

    Returns:
        True if actual == expected
    """
    return actual == expected


def contains(actual: str, expected: Optional[str]) -> bool:
    """Pass if expected appears anywhere in the response, case-insensitive.

    Args:
        actual: The model's response text
        expected: The substring that must appear in the response

    Returns:
        True if expected is a substring of actual (case-insensitive)
    """
    if expected is None:
        return False
    return expected.lower() in actual.lower()


def regex_match(actual: str, expected: Optional[str]) -> bool:
    """Pass if the response matches the given regex pattern anywhere in it.

    Args:
        actual: The model's response text
        expected: A regex pattern to search for in the response

    Returns:
        True if the pattern matches somewhere in actual

    Raises:
        re.error: If expected is not a valid regex pattern
    """
    if expected is None:
        return False
    return re.search(expected, actual) is not None
