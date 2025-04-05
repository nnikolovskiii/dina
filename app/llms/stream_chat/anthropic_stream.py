from typing import Optional, List, Dict

from anthropic import AsyncAnthropic

from app.llms.models import StreamChatLLM
from app.llms.utils import _get_messages_template


class AnthropicStreamChat(StreamChatLLM):
    async def generate(
            self,
            message: str,
            system_message: Optional[str] = "You are helpful AI assistant.",
            history: List[Dict[str, str]] = None
    ):
        client = AsyncAnthropic(api_key=self.chat_api.api_key)

        messages = _get_messages_template(message, history)

        try:
            stream = await client.messages.create(
                model=self.chat_model_config.name,
                system=system_message,
                messages=messages,
                max_tokens=40000,
                stream=True
            )

            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text

        except Exception as e:
            error_msg = f"Anthropic streaming error: {str(e)}"
            raise RuntimeError(error_msg)
