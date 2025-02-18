from typing import List, Dict, AsyncGenerator

from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline


class PerformPayment(ChatPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(self, conversation:  List[Dict[str, str]]) -> str:
        response =  f"""Given the below conversation make a quick summary.

# Conversation:\n"""
        for message in conversation:
            #   {"role": "system", "content": system_message},
            response += message["role"] + ":\n"
            response += message["content"] + "\n"


        response += """\nQuick summary:"""

        return response


async def perform_payment() -> AsyncGenerator[str, None]:
    yield "Payment is performed."

async def irrelevant_info_response(question: str) -> AsyncGenerator[str, None]:
    yield "There is no such information."