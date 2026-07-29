"""Logging infrastructure for Neuravo SDK.

Provides centralized logging setup with:
- Structured logging format
- Sensitive data redaction
- Multiple output levels
- Module-specific loggers
"""

import logging
import re
import sys
from typing import Any, Optional

# Patterns for sensitive data that should be redacted
SENSITIVE_PATTERNS = [
    r"api[_-]?key\s*[:=]\s*[^\s,}\"']+",
    r"api[_-]?secret\s*[:=]\s*[^\s,}\"']+",
    r"aws[_-]?access[_-]?key([_-]?id)?\s*[:=]\s*[^\s,}\"']+",
    r"aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*[^\s,}\"']+",
    r"password\s*[:=]\s*[^\s,}\"']+",
    r"token\s*[:=]\s*[^\s,}\"']+",
    r"bearer\s+[^\s]+",
    r"authorization\s*[:=]\s*[^\s,}\"']+",
]


def redact_sensitive_data(text: Any) -> str:
    """Remove sensitive data from text before logging.

    Replaces API keys, passwords, tokens, and other sensitive information
    with '[REDACTED]' markers.

    Args:
        text: Text potentially containing sensitive data

    Returns:
        Text with sensitive data redacted

    Examples:
        Redaction in action::

            >>> redact_sensitive_data("api_key=abc123xyz")
            "api_key=[REDACTED]"
    """
    if not isinstance(text, str):
        return str(text)

    result: str = text
    for pattern in SENSITIVE_PATTERNS:
        result = re.sub(pattern, "[REDACTED]", result, flags=re.IGNORECASE)

    return result


class SensitiveDataFilter(logging.Filter):
    """Logging filter that redacts sensitive data from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to redact sensitive data.

        Args:
            record: Log record to filter

        Returns:
            True to allow the record to be logged
        """
        record.msg = redact_sensitive_data(str(record.msg))
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: redact_sensitive_data(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(redact_sensitive_data(str(arg)) for arg in record.args)
        return True


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Configure logging for all Neuravo modules.

    Sets up structured logging with the specified level and optional file output.
    Automatically redacts sensitive data from all log messages.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging (default: stderr only)

    Examples:
        Enable debug logging::

            setup_logging("DEBUG")

        Log to file::

            setup_logging("INFO", log_file="neuravo.log")

    Raises:
        ValueError: If level is invalid
    """
    # Validate level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid logging level: {level}")

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger for neuravo
    root_logger = logging.getLogger("neuravo")
    root_logger.setLevel(numeric_level)
    root_logger.propagate = False

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add stderr handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(numeric_level)
    stderr_handler.setFormatter(formatter)
    stderr_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(stderr_handler)

    # Add file handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(SensitiveDataFilter())
            root_logger.addHandler(file_handler)
        except IOError as e:
            root_logger.warning(f"Failed to create log file {log_file}: {e}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module.

    Returns a logger with the given name under the neuravo namespace.

    Args:
        name: Module name (e.g., "core", "providers.bedrock")

    Returns:
        Configured logger instance

    Examples:
        Get logger for a module::

            logger = get_logger("providers.bedrock")
            logger.info("Initializing Bedrock provider")
    """
    full_name = f"neuravo.{name}" if not name.startswith("neuravo.") else name
    logger = logging.getLogger(full_name)
    return logger
