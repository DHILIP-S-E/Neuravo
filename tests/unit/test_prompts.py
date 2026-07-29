"""Tests for prompt templates and the prompt registry."""

import pytest

from neuravo.core.exceptions import ValidationError
from neuravo.prompts import PromptNotFoundError, PromptRegistry, PromptTemplate


def test_render_fills_in_placeholders():
    template = PromptTemplate("Summarize this {doc_type} in {n} sentences: {text}")
    result = template.render(doc_type="article", n=3, text="Once upon a time...")
    assert result == "Summarize this article in 3 sentences: Once upon a time..."


def test_variables_lists_placeholder_names_in_order_without_duplicates():
    template = PromptTemplate("{a} and {b} and {a} again")
    assert template.variables == ["a", "b"]


def test_render_raises_on_missing_variable():
    template = PromptTemplate("Hello {name}")
    with pytest.raises(ValidationError):
        template.render()


def test_template_with_no_placeholders_renders_unchanged():
    template = PromptTemplate("Just plain text.")
    assert template.render() == "Just plain text."


def test_registry_get_returns_latest_registered_version_by_default():
    registry = PromptRegistry()
    registry.register("greet", PromptTemplate("Hi {name}"), version="1")
    registry.register("greet", PromptTemplate("Hello {name}!"), version="2")

    assert registry.get("greet").render(name="Ada") == "Hello Ada!"


def test_registry_get_specific_version():
    registry = PromptRegistry()
    registry.register("greet", PromptTemplate("Hi {name}"), version="1")
    registry.register("greet", PromptTemplate("Hello {name}!"), version="2")

    assert registry.get("greet", version="1").render(name="Ada") == "Hi Ada"


def test_registry_list_versions_and_names():
    registry = PromptRegistry()
    registry.register("greet", PromptTemplate("Hi {name}"), version="1")
    registry.register("greet", PromptTemplate("Hello {name}!"), version="2")
    registry.register("farewell", PromptTemplate("Bye {name}"))

    assert registry.list_versions("greet") == ["1", "2"]
    assert registry.list_names() == ["farewell", "greet"]


def test_registry_get_unknown_name_raises():
    registry = PromptRegistry()
    with pytest.raises(PromptNotFoundError):
        registry.get("unknown")


def test_registry_get_unknown_version_raises():
    registry = PromptRegistry()
    registry.register("greet", PromptTemplate("Hi {name}"), version="1")
    with pytest.raises(PromptNotFoundError):
        registry.get("greet", version="99")
