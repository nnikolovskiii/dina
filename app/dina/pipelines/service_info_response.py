from typing import List, Optional, Dict, AsyncGenerator

from bson import ObjectId

from app.container import container
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import StreamChatLLM, ChatLLM
from app.pipelines.pipeline import ChatPipeline, StreamPipeline


class ServiceResponse(StreamPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(
            self,
            question: str,
            service_info: str,
            conversation: str,
    ) -> str:
        return f"""Given the below question answer it based only on the information provided in the context. Answer in Macedonian.

{service_info}

# Previous conversation:
{conversation}

# Question: {question}

Write it in a clear format.
Response in Macedonian:"""


async def generate_service_info_response(
        question: str,
        history_summary: str,
        service_info: str,
        system_message: str,
        history: List[Dict[str, str]]
) -> AsyncGenerator[str, None]:
    chat_service = container.chat_service()
    streaming_model = await chat_service.get_model(model_name="gpt-4o", class_type=StreamChatLLM)
    retriever_pipeline = ServiceResponse(streaming_model)

    async for response_chunk in retriever_pipeline.execute(
            question=question,
            conversation=history_summary,
            service_info=service_info,
            system_message=system_message,
            history=history,
    ):
        yield response_chunk