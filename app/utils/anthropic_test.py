import asyncio
import logging
import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from anthropic import AsyncAnthropic  # Use Anthropic's async client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate(
        message: str,
        system_message: Optional[str] = "You are a helpful AI assistant.",
        history: List[Dict[str, str]] = None
) -> str:
    load_dotenv()
    api_key = os.getenv("CLAUDE")

    # Initialize Anthropic client
    client = AsyncAnthropic(api_key=api_key)

    # Prepare messages list (without system message)
    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        # Create completion with separate system message
        response = await client.messages.create(
            model="claude-3-haiku-20240307",
            system=system_message,
            messages=messages,
            max_tokens=1024
        )

        logger.info("Successfully received response from Claude API")
        print(response.content[0].text)
        return response.content[0].text

    except Exception as e:
        logger.error(f"Claude API request failed: {str(e)}")
        raise Exception(f"API Error: {str(e)}")


# Test the function
asyncio.run(generate("Hello, how are you?"))