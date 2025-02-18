from typing import List, Optional, Dict, AsyncGenerator

from bson import ObjectId

from app.container import container
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import StreamChatLLM, ChatLLM
from app.pipelines.pipeline import ChatPipeline, StreamPipeline


class AboutDina(StreamPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(
            self,
            question: str,
    ) -> str:
        return f"""Answer the below question. Write your answer in Macedonian. 

# Information about yourself:
- To answer and perform task on administrative institutions strictly in Macedonia.
- Help retrieve information about administrative institutions.
- Perform actions like filling out forms, making payments, etc.

# Question: {question}

Response in Macedonian:"""


async def generate_general_response(
        question: str,
        system_message: str,
        history: List[Dict[str, str]]
) -> AsyncGenerator[str, None]:
    chat_service = container.chat_service()
    streaming_model = await chat_service.get_model(model_name="gpt-4o", class_type=StreamChatLLM)
    retriever_pipeline = AboutDina(streaming_model)

    async for response_chunk in retriever_pipeline.execute(
            question=question,
            system_message=system_message,
            history=history,
    ):
        yield response_chunk