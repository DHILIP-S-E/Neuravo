"""Input validation utilities.

Provides validators for common input types and constraints.
"""

from neuravo.core.exceptions import ValidationError


def validate_prompt(prompt: str) -> bool:
    """Validate chat prompt.

    Args:
        prompt: Prompt text to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If prompt is invalid
    """
    if not prompt or not isinstance(prompt, str):
        raise ValidationError("Prompt must be a non-empty string")

    if not prompt.strip():
        raise ValidationError("Prompt cannot be only whitespace")

    if len(prompt) > 100000:
        raise ValidationError("Prompt exceeds maximum length (100,000 chars)")

    return True


def validate_model_id(model_id: str) -> bool:
    """Validate model identifier.

    Args:
        model_id: Model ID to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If model ID is invalid
    """
    if not model_id or not isinstance(model_id, str):
        raise ValidationError("Model ID must be a non-empty string")

    return True


def validate_region(region: str) -> bool:
    """Validate AWS region.

    Args:
        region: Region string to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If region is invalid
    """
    if not region or not isinstance(region, str):
        raise ValidationError("Region must be a non-empty string")

    return True
