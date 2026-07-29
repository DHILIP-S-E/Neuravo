"""Message data structures for chat feature.

Extends core Message with chat-specific functionality.
"""

from neuravo.core.types import Message as CoreMessage

# Re-export core Message for convenience
Message = CoreMessage

__all__ = [
    "Message",
]
