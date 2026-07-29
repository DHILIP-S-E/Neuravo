"""Named, versioned storage for prompt templates."""

from typing import Dict, List, Optional

from neuravo.core.exceptions import NeurevoError
from neuravo.prompts.template import PromptTemplate


class PromptNotFoundError(NeurevoError):
    """Raised when a requested prompt name or version isn't registered."""

    def __init__(self, message: str) -> None:
        """Initialize PromptNotFoundError."""
        super().__init__(message, "PROMPT_NOT_FOUND")


class PromptRegistry:
    """Stores prompt templates by name, with optional versioning.

    Examples:
        Register and fetch a template::

            registry = PromptRegistry()
            registry.register("summarize", PromptTemplate("Summarize: {text}"))
            template = registry.get("summarize")
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._templates: Dict[str, Dict[str, PromptTemplate]] = {}
        self._latest_version: Dict[str, str] = {}

    def register(self, name: str, template: PromptTemplate, version: str = "1") -> None:
        """Register a template under a name and version.

        Registering a new version under an existing name does not remove
        older versions - use `get(name, version=...)` to fetch a specific
        one, or `get(name)` for the most recently registered version.

        Args:
            name: Prompt name
            template: The template to store
            version: Version label for this template (default "1")
        """
        self._templates.setdefault(name, {})[version] = template
        self._latest_version[name] = version

    def get(self, name: str, version: Optional[str] = None) -> PromptTemplate:
        """Get a registered template.

        Args:
            name: Prompt name
            version: Specific version to fetch, or None for the latest
                registered version

        Returns:
            The requested PromptTemplate

        Raises:
            PromptNotFoundError: If the name or version isn't registered
        """
        if name not in self._templates:
            raise PromptNotFoundError(f"No prompt registered under name '{name}'")

        resolved_version = version or self._latest_version[name]
        versions = self._templates[name]
        if resolved_version not in versions:
            raise PromptNotFoundError(
                f"Prompt '{name}' has no version '{resolved_version}' "
                f"(known versions: {', '.join(sorted(versions))})"
            )
        return versions[resolved_version]

    def list_versions(self, name: str) -> List[str]:
        """List all registered versions of a prompt name.

        Args:
            name: Prompt name

        Returns:
            Sorted list of version labels

        Raises:
            PromptNotFoundError: If the name isn't registered
        """
        if name not in self._templates:
            raise PromptNotFoundError(f"No prompt registered under name '{name}'")
        return sorted(self._templates[name])

    def list_names(self) -> List[str]:
        """List all registered prompt names.

        Returns:
            Sorted list of prompt names
        """
        return sorted(self._templates)
