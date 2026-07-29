"""Security capability for Neuravo SDK.

Prompt-level policy checks (block-list patterns) and output redaction.
Not a compliance or PII-detection system - see security/policy.py.

Examples:
    Check a prompt before sending it::

        from neuravo.security import SecurityPolicy

        policy = SecurityPolicy()
        policy.check_prompt(user_input)  # raises SecurityError if blocked
"""

from neuravo.security.policy import DEFAULT_BANNED_PATTERNS, SecurityPolicy
from neuravo.security.redaction import redact_sensitive_data

__all__ = [
    "SecurityPolicy",
    "DEFAULT_BANNED_PATTERNS",
    "redact_sensitive_data",
]
