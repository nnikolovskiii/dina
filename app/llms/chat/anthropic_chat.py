import logging
from typing import List, Dict, Optional

from anthropic import AsyncAnthropic
from app.llms.models import ChatLLM
from app.llms.utils import _get_messages_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnthropicChat(ChatLLM):
    async def generate(
            self,
            message: str,
            system_message: Optional[str] = "You are helpful AI assistant.",
            history: List[Dict[str, str]] = None
    ) -> str:

        client = AsyncAnthropic(api_key=self.chat_api.api_key)

        messages = _get_messages_template(message, history)

        try:
            response = await client.messages.create(
                model=self.chat_model_config.name,
                system=system_message,
                messages=messages,
                max_tokens=40000,
            )

            logger.info("Successfully received response from Claude API")
            print(response.content[0].text)
            return response.content[0].text

        except Exception as e:
            logger.error(f"Claude API request failed: {str(e)}")
            raise Exception(f"API Error: {str(e)}")
