"""Conversation history management for chat feature.

Manages storage and retrieval of conversation history.
"""

from typing import List, Optional

from neuravo.core.types import Message


class ConversationHistory:
    """Manages conversation history.

    Stores and retrieves chat messages with support for filtering,
    truncation, and serialization.

    Attributes:
        messages: List of messages in conversation
        max_history: Maximum number of messages to retain
    """

    def __init__(self, max_history: Optional[int] = None) -> None:
        """Initialize conversation history.

        Args:
            max_history: Maximum messages to retain (None = unlimited)
        """
        self.messages: List[Message] = []
        self.max_history = max_history

    def add(self, message: Message) -> None:
        """Add message to history.

        Args:
            message: Message to add
        """
        self.messages.append(message)
        if self.max_history is not None and len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]

    def get_all(self) -> List[Message]:
        """Get all messages.

        Returns:
            List of all messages
        """
        return list(self.messages)

    def clear(self) -> None:
        """Clear all messages."""
        self.messages = []

    def truncate(self, n: int) -> List[Message]:
        """Get last n messages.

        Args:
            n: Number of messages to retrieve

        Returns:
            Last n messages
        """
        if n <= 0:
            return []
        return self.messages[-n:]
