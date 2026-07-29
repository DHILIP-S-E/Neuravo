"""Exception hierarchy for Neuravo SDK.

All exceptions in Neuravo inherit from NeurevoError and include:
- Error code for programmatic handling
- User-friendly message for display
- Optional debug details for troubleshooting
- Traceback for error context

Exception Hierarchy:
    NeurevoError (base)
    ├── ProviderError (provider-specific failures)
    │   ├── BedrockError
    │   ├── OpenAIError
    │   ├── ProviderNotFoundError
    │   └── ProviderConfigError
    ├── ConfigError (configuration issues)
    │   ├── MissingConfigError
    │   └── InvalidConfigError
    ├── TimeoutError (timeout exceeded)
    ├── RetryExhaustedError (max retries exceeded)
    ├── ValidationError (input validation)
    ├── SecurityError (blocked by a security policy)
    ├── WorkflowError (a workflow step raised)
    └── StreamingError (streaming operation failed)
"""

from typing import Any, Dict, List, Optional


class NeurevoError(Exception):
    """Base exception for all Neuravo SDK errors.

    Attributes:
        error_code: Unique error code for programmatic handling
        message: User-friendly error message
        debug_details: Optional debug information
    """

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize NeurevoError.

        Args:
            message: Human-readable error message
            error_code: Unique error identifier
            debug_details: Optional debugging information
        """
        self.error_code = error_code
        self.message = message
        self.debug_details = debug_details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return formatted error string."""
        return f"[{self.error_code}] {self.message}"

    def __repr__(self) -> str:
        """Return detailed error representation."""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, error_code={self.error_code!r})"
        )


class ProviderError(NeurevoError):
    """Provider-specific error.

    Raised when a provider operation fails (authentication, API calls, etc.).
    """

    def __init__(
        self,
        message: str,
        error_code: str = "PROVIDER_ERROR",
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ProviderError."""
        super().__init__(message, error_code, debug_details)


class BedrockError(ProviderError):
    """AWS Bedrock-specific error."""

    def __init__(
        self,
        message: str,
        error_code: str = "BEDROCK_ERROR",
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize BedrockError."""
        super().__init__(message, error_code, debug_details)


class OpenAIError(ProviderError):
    """OpenAI-specific error."""

    def __init__(
        self,
        message: str,
        error_code: str = "OPENAI_ERROR",
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize OpenAIError."""
        super().__init__(message, error_code, debug_details)


class ProviderNotFoundError(ProviderError):
    """Requested provider is not available."""

    def __init__(
        self,
        provider_name: str,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ProviderNotFoundError."""
        message = f"Provider '{provider_name}' not found. Check spelling and ensure it's installed."
        super().__init__(
            message,
            "PROVIDER_NOT_FOUND",
            debug_details,
        )


class ProviderConfigError(ProviderError):
    """Provider configuration is invalid."""

    def __init__(
        self,
        message: str,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ProviderConfigError."""
        super().__init__(
            message,
            "PROVIDER_CONFIG_ERROR",
            debug_details,
        )


class ConfigError(NeurevoError):
    """Configuration validation error.

    Raised when configuration is invalid or missing required fields.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "CONFIG_ERROR",
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ConfigError."""
        super().__init__(message, error_code, debug_details)


class MissingConfigError(ConfigError):
    """Required configuration field is missing."""

    def __init__(
        self,
        missing_fields: List[str],
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize MissingConfigError."""
        fields_str = ", ".join(missing_fields)
        message = f"Missing required configuration fields: {fields_str}"
        super().__init__(
            message,
            "MISSING_CONFIG",
            debug_details,
        )


class InvalidConfigError(ConfigError):
    """Configuration value is invalid."""

    def __init__(
        self,
        message: str,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize InvalidConfigError."""
        super().__init__(
            message,
            "INVALID_CONFIG",
            debug_details,
        )


class TimeoutError(NeurevoError):
    """Operation timeout exceeded.

    Raised when an operation exceeds its timeout limit.
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: float = 0.0,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize TimeoutError."""
        self.timeout_seconds = timeout_seconds
        super().__init__(
            message,
            "TIMEOUT_ERROR",
            debug_details,
        )


class RetryExhaustedError(NeurevoError):
    """Maximum retry attempts exceeded.

    Raised when an operation fails after all retry attempts are exhausted.
    """

    def __init__(
        self,
        message: str,
        attempts: int = 0,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize RetryExhaustedError."""
        self.attempts = attempts
        super().__init__(
            message,
            "RETRY_EXHAUSTED",
            debug_details,
        )


class ValidationError(NeurevoError):
    """Input validation error.

    Raised when user input fails validation checks.
    """

    def __init__(
        self,
        message: str,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ValidationError."""
        super().__init__(
            message,
            "VALIDATION_ERROR",
            debug_details,
        )


class WorkflowError(NeurevoError):
    """A workflow step raised while running.

    Attributes:
        step_name: Name of the step that failed
    """

    def __init__(
        self,
        step_name: str,
        message: str,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize WorkflowError."""
        self.step_name = step_name
        super().__init__(message, "WORKFLOW_ERROR", debug_details)


class SecurityError(NeurevoError):
    """Security policy violation.

    Raised when a prompt is blocked by a SecurityPolicy check.
    """

    def __init__(
        self,
        message: str,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize SecurityError."""
        super().__init__(
            message,
            "SECURITY_ERROR",
            debug_details,
        )


class StreamingError(NeurevoError):
    """Streaming operation error.

    Raised when a streaming response fails mid-transfer.
    """

    def __init__(
        self,
        message: str,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize StreamingError."""
        super().__init__(
            message,
            "STREAMING_ERROR",
            debug_details,
        )
