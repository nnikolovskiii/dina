import asyncio
import os
from typing import List, Dict, Optional, AsyncGenerator
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from app.llms.models import StreamChatLLM
from app.llms.utils import _get_messages_template


async def generate(
                   message: str,
                   system_message: Optional[str] = "You are a helpful AI assistant.",
                   history: List[Dict[str, str]] = None) -> AsyncGenerator[str, None]:
    load_dotenv()
    api_key = os.getenv("CLAUDE")
    client = AsyncAnthropic(api_key=api_key)

    # Prepare messages (Anthropic requires separate system message)
    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        # Create streaming response
        stream = await client.messages.create(
            model="claude-3-7-sonnet-20250219",
            system=system_message,
            messages=messages,
            max_tokens=1024,
            stream=True
        )

        # Stream response chunks
        async for chunk in stream:
            if chunk.type == "content_block_delta":
                yield chunk.delta.text

    except Exception as e:
        error_msg = f"Anthropic streaming error: {str(e)}"
        # logger.error(error_msg)
        raise RuntimeError(error_msg)


# Usage example with same message
async def main():
    async for chunk in generate("What is docker explain in detail?"):
        print(chunk, end="", flush=True)


asyncio.run(main())