"""Tests for security policy checks and output redaction."""

import pytest

from neuravo.core.exceptions import SecurityError
from neuravo.security import SecurityPolicy


def test_check_prompt_allows_clean_input():
    policy = SecurityPolicy()
    policy.check_prompt("What's the weather like today?")  # should not raise


def test_check_prompt_blocks_ssn_like_pattern():
    policy = SecurityPolicy()
    with pytest.raises(SecurityError):
        policy.check_prompt("My SSN is 123-45-6789")


def test_check_prompt_blocks_credit_card_like_pattern():
    policy = SecurityPolicy()
    with pytest.raises(SecurityError):
        policy.check_prompt("Card number: 4111 1111 1111 1111")


def test_custom_banned_patterns_override_defaults():
    policy = SecurityPolicy(banned_patterns=[r"forbidden-word"])
    policy.check_prompt("My SSN is 123-45-6789")  # allowed - not in custom list

    with pytest.raises(SecurityError):
        policy.check_prompt("this contains forbidden-word")


def test_sanitize_output_redacts_sensitive_data():
    policy = SecurityPolicy()
    sanitized = policy.sanitize_output("api_key=sk-abc123xyz")
    assert "sk-abc123xyz" not in sanitized
    assert "[REDACTED]" in sanitized
