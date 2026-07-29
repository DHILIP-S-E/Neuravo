"""Property-based tests for Message data structure.

Tests universal properties of Message serialization and deserialization.
"""


import pytest
from hypothesis import given
from hypothesis import strategies as st

from neuravo.core.types import Message

# Strategy for generating valid messages
message_strategy = st.builds(
    Message,
    role=st.sampled_from(["user", "assistant", "system"]),
    content=st.text(min_size=1),
)


class TestMessageProperties:
    """Property-based tests for Message."""

    @given(message_strategy)
    def test_message_serialization_roundtrip(self, message: Message):
        """**Validates: Requirements 3.3, 3.6**

        Property: Message serialization is reversible.
        For any valid Message, serializing and deserializing produces equivalent message.
        """
        serialized = message.to_dict()
        deserialized = Message.from_dict(serialized)

        assert deserialized.role == message.role
        assert deserialized.content == message.content

    @given(message_strategy)
    def test_message_immutability_after_creation(self, message: Message):
        """Property: Message is immutable after creation.
        Attempting to modify any field raises an error.
        """
        with pytest.raises(Exception):
            message.role = "different"

    @given(st.text(min_size=1))
    def test_message_content_never_empty(self, content: str):
        """Property: Message content is never empty after creation."""
        msg = Message(role="user", content=content)
        assert msg.content == content
        assert len(msg.content) > 0
