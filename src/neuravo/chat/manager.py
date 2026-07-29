"""Chat manager for orchestrating chat interactions.

The ChatManager handles conversation management, message validation,
and coordination between the client and provider layers.
"""

from typing import AsyncIterator, List

from neuravo.core.client import BaseClient
from neuravo.core.types import ChatResponse, Message
from neuravo.utils.validators import validate_prompt


class ChatManager:
    """Orchestrates chat interactions with AI models.

    A thin conversation-history layer over a `BaseClient`: every call
    delegates the actual request to the wrapped client and records the
    resulting turn locally.

    Attributes:
        client: The underlying AI client
        history: Conversation history

    Examples:
        Basic chat::

            chat_mgr = ChatManager(client)
            response = await chat_mgr.chat("Hello!")
            print(response.content)

        With history::

            history = chat_mgr.get_history()
            for msg in history:
                print(f"{msg.role}: {msg.content}")
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize chat manager.

        Args:
            client: AI client instance
        """
        self.client = client
        self.history: List[Message] = []

    async def chat(self, prompt: str) -> ChatResponse:
        """Send chat message and get response.

        Args:
            prompt: User input message

        Returns:
            ChatResponse from the model

        Raises:
            ValidationError: If prompt is empty or invalid
            ProviderError: If provider call fails
            TimeoutError: If request exceeds timeout
        """
        validate_prompt(prompt)
        self.history.append(Message(role="user", content=prompt))
        response = await self.client.chat(prompt)
        self.history.append(Message(role="assistant", content=response.content))
        return response

    async def stream(self, prompt: str) -> AsyncIterator[ChatResponse]:
        """Stream chat response progressively.

        Args:
            prompt: User input message

        Yields:
            ChatResponse chunks as they arrive

        Raises:
            ValidationError: If prompt is empty or invalid
            ProviderError: If provider call fails
            StreamingError: If streaming fails
        """
        validate_prompt(prompt)
        self.history.append(Message(role="user", content=prompt))

        accumulated = ""
        async for chunk in self.client.stream(prompt):
            accumulated += chunk.content
            yield chunk

        self.history.append(Message(role="assistant", content=accumulated))

    def get_history(self) -> List[Message]:
        """Get conversation history.

        Returns:
            List of messages in chronological order
        """
        return list(self.history)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history = []
