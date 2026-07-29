"""Prompt templates with named placeholders."""

import string
from typing import Any, List

from neuravo.core.exceptions import ValidationError


class PromptTemplate:
    """A prompt string with `{variable}` placeholders.

    Examples:
        Render a template::

            template = PromptTemplate("Summarize this {doc_type} in {n} sentences: {text}")
            prompt = template.render(doc_type="article", n=3, text="...")
    """

    def __init__(self, template: str) -> None:
        """Initialize the template.

        Args:
            template: A string containing `{variable}`-style placeholders
        """
        self.template = template

    @property
    def variables(self) -> List[str]:
        """Names of every placeholder in the template, in order of first appearance.

        Returns:
            List of variable names (duplicates removed, order preserved)
        """
        seen: List[str] = []
        for _, field_name, _, _ in string.Formatter().parse(self.template):
            if field_name and field_name not in seen:
                seen.append(field_name)
        return seen

    def render(self, **values: Any) -> str:
        """Fill in the template's placeholders.

        Args:
            **values: Value for each placeholder in the template

        Returns:
            The rendered prompt string

        Raises:
            ValidationError: If any placeholder is missing a value
        """
        missing = [v for v in self.variables if v not in values]
        if missing:
            raise ValidationError(f"Missing values for template variable(s): {', '.join(missing)}")
        return self.template.format(**values)
