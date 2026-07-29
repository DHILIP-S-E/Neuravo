"""Chat capability for Neuravo SDK.

Provides high-level chat interface with conversation history management,
streaming support, and message validation. Kept separate from
``providers/`` by design: this module knows how to expose a chat API,
not how any particular vendor's wire protocol works.

Examples:
    Basic chat::

        from neuravo import Client, Config
        from neuravo.chat import ChatManager

        config = Config(provider="bedrock", region="us-east-1")
        client = Client(config)
        chat_mgr = ChatManager(client)
        response = await chat_mgr.chat("What is AI?")

    Streaming chat::

        async for chunk in chat_mgr.stream("Tell me a story"):
            print(chunk.content, end="", flush=True)
"""

from neuravo.chat.manager import ChatManager
from neuravo.chat.message import Message

__all__ = [
    "ChatManager",
    "Message",
]
