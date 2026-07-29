"""Configuration management for Neuravo SDK.

This module provides the Config class for managing SDK settings with:
- Pydantic-based validation
- Environment variable support
- Clear error messages for misconfiguration
- Immutability after creation
"""

import os
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """Main configuration class for Neuravo clients.

    Supports both code-based and environment variable configuration.
    Environment variables take precedence over code defaults.

    Attributes:
        provider: AI provider to use (e.g., "bedrock", "openai")
        region: AWS region for Bedrock provider
        model: Model identifier (e.g., "anthropic.claude-3-sonnet")
        timeout: Request timeout in seconds (default: 30.0)
        max_retries: Maximum retry attempts (default: 3)
        backoff_factor: Exponential backoff multiplier (default: 2.0)
        debug: Enable debug logging (default: False)

    Examples:
        Basic configuration::

            config = Config(provider="bedrock", region="us-east-1")

        With environment variables::

            # Set in environment: AWS_REGION=us-west-2
            config = Config(provider="bedrock")
            # region will be "us-west-2"

    Raises:
        ValueError: If configuration is invalid or missing required fields
    """

    provider: str = Field(
        default="bedrock",
        description="AI provider name (bedrock, openai, anthropic, etc.)",
    )
    region: Optional[str] = Field(
        default=None,
        description="AWS region for Bedrock (e.g., us-east-1)",
    )
    model: Optional[str] = Field(
        default=None,
        description="Model identifier (provider-specific)",
    )
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=3600.0,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )
    backoff_factor: float = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="Exponential backoff multiplier",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug logging",
    )

    class Config:
        """Pydantic configuration."""

        frozen = True  # Make config immutable
        validate_assignment = False

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider name.

        Args:
            v: Provider name

        Returns:
            Validated provider name

        Raises:
            ValueError: If provider name is invalid
        """
        if not v or not isinstance(v, str):
            raise ValueError("Provider must be a non-empty string")
        if len(v) > 50:
            raise ValueError("Provider name too long (max 50 chars)")
        return v.lower()

    @field_validator("region", mode="before")
    @classmethod
    def populate_region(cls, v: Optional[str]) -> Optional[str]:
        """Populate region from environment if not provided.

        Args:
            v: Provided region or None

        Returns:
            Region string or None
        """
        if v is None:
            return os.environ.get("AWS_REGION")
        return v

    def __init__(self, **data):
        """Initialize Config with validation.

        Args:
            **data: Configuration parameters

        Raises:
            ValueError: If configuration is invalid
        """
        super().__init__(**data)

    def to_dict(self) -> dict:
        """Convert config to dictionary.

        Returns:
            Dictionary representation of config
        """
        return {
            "provider": self.provider,
            "region": self.region,
            "model": self.model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "backoff_factor": self.backoff_factor,
            "debug": self.debug,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create Config from dictionary.

        Args:
            data: Dictionary with configuration

        Returns:
            Config instance

        Raises:
            ValueError: If configuration is invalid
        """
        return cls(**data)
