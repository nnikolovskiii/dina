from typing import List, Dict

from app.container import container
from app.llms.models import ChatLLM
from app.pipelines.pipeline import ChatPipeline


class HistoryCondenser(ChatPipeline):
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


async def get_chat_history(history: List[Dict[str,str]]) -> str:
    chat_service = container.chat_service()
    chat_model = await chat_service.get_model(model_name="gpt-4o-mini", class_type=ChatLLM)

    history_pipeline = HistoryCondenser(chat_llm=chat_model)
    history_summary = await history_pipeline.execute(conversation=history)

    return history_summary