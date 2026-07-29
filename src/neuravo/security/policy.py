"""Prompt-level security policy checks.

A minimal, extensible block-list mechanism - not a compliance/PII-detection
system. Callers with real compliance requirements should supply their own
patterns rather than rely on the illustrative defaults here.
"""

import re
from typing import List, Optional

from neuravo.core.exceptions import SecurityError
from neuravo.security.redaction import redact_sensitive_data

# Illustrative defaults only - not an exhaustive PII detector.
DEFAULT_BANNED_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN-like: 123-45-6789
    r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",  # credit-card-like
]


class SecurityPolicy:
    """Blocks prompts matching configured patterns and redacts output text.

    Examples:
        Reject a prompt containing an SSN-like pattern::

            policy = SecurityPolicy()
            policy.check_prompt("My SSN is 123-45-6789")  # raises SecurityError
    """

    def __init__(self, banned_patterns: Optional[List[str]] = None) -> None:
        """Initialize the policy.

        Args:
            banned_patterns: Regex patterns that block a prompt if matched
                (defaults to DEFAULT_BANNED_PATTERNS)
        """
        self.banned_patterns = banned_patterns or list(DEFAULT_BANNED_PATTERNS)

    def check_prompt(self, prompt: str) -> None:
        """Raise if the prompt matches any banned pattern.

        Args:
            prompt: Prompt text to check

        Raises:
            SecurityError: If a banned pattern is found in the prompt
        """
        for pattern in self.banned_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                raise SecurityError(
                    "Prompt blocked by security policy",
                    debug_details={"matched_pattern": pattern},
                )

    def sanitize_output(self, text: str) -> str:
        """Redact sensitive-looking data from response text.

        Args:
            text: Text to sanitize

        Returns:
            Text with sensitive-looking substrings replaced by [REDACTED]
        """
        return redact_sensitive_data(text)
