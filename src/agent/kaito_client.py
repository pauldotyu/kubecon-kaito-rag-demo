"""
Custom OpenAI Chat Client for KAITO RAG Engine compatibility.
"""

from collections.abc import Sequence
from typing import Any
from agent_framework._types import ChatMessage, Contents, TextContent
from agent_framework.openai import OpenAIChatClient


class KAITOChatClient(OpenAIChatClient):
    """Custom OpenAI Chat Client optimized for KAITO RAG Engine compatibility."""

    def _openai_content_parser(self, content: Contents) -> dict[str, Any] | str:
        """Parse contents into the open ai format."""
        if isinstance(content, TextContent):
            return content.text
            # return {"type": "text", "text": content.text}

        return super()._openai_content_parser(content)

    def _prepare_chat_history_for_request(
        self,
        chat_messages: Sequence[ChatMessage],
        role_key: str = "role",
        content_key: str = "content",
    ) -> list[dict[str, Any]]:
        """Override to ensure compatibility with KAITO RAG Engine."""
        messages = super()._prepare_chat_history_for_request(
            chat_messages, role_key, content_key
        )

        for msg in messages:
            if "content" in msg and isinstance(msg["content"], list):
                if len(msg["content"]) == 1 and isinstance(msg["content"][0], str):
                    msg["content"] = msg["content"][0]

        return messages
