"""Streaming chat response handling.

Provides utilities for streaming chat responses from providers.
"""

from typing import AsyncIterator

from neuravo.core.types import ChatResponse


class StreamingChat:
    """Handles streaming chat interactions.

    Provides utilities for streaming responses and progressive output.
    """

    @staticmethod
    async def stream_response(
        response_iterator: AsyncIterator[ChatResponse],
    ) -> AsyncIterator[str]:
        """Stream response content progressively.

        Args:
            response_iterator: Iterator of response chunks

        Yields:
            Response content chunks
        """
        async for response in response_iterator:
            if response.content:
                yield response.content
