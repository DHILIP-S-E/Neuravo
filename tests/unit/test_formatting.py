"""Tests for data formatting utilities."""

from neuravo.utils.formatting import (
    format_error_message,
    format_response,
    truncate_string,
)


def test_format_error_message_without_details():
    assert format_error_message("E001", "Something broke") == "[E001] Something broke"


def test_format_error_message_with_details():
    result = format_error_message("E001", "Something broke", {"field": "region"})
    assert result == "[E001] Something broke (field=region)"


def test_format_response_delegates_to_truncate():
    assert format_response("short text", max_length=100) == "short text"
    assert format_response("x" * 600, max_length=500).endswith("...")


def test_truncate_string_returns_unchanged_when_within_limit():
    assert truncate_string("hello", max_length=100) == "hello"


def test_truncate_string_truncates_and_adds_suffix():
    result = truncate_string("hello world", max_length=8, suffix="...")
    assert result == "hello..."
    assert len(result) == 8


def test_truncate_string_handles_max_length_smaller_than_suffix():
    result = truncate_string("hello world", max_length=2, suffix="...")
    assert result == ".."
