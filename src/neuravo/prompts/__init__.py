"""Prompt management capability for Neuravo SDK.

Templated prompts with named placeholders, and a registry for storing
and versioning them by name.

Examples:
    Register and render a versioned prompt::

        from neuravo.prompts import PromptRegistry, PromptTemplate

        registry = PromptRegistry()
        registry.register("summarize", PromptTemplate("Summarize: {text}"), version="1")
        prompt = registry.get("summarize").render(text="...")
"""

from neuravo.prompts.registry import PromptNotFoundError, PromptRegistry
from neuravo.prompts.template import PromptTemplate

__all__ = [
    "PromptTemplate",
    "PromptRegistry",
    "PromptNotFoundError",
]
