from typing import List, Optional, Dict, AsyncGenerator

from bson import ObjectId

from app.container import container
from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.dina.pipelines.info_retriever import InfoRetriever, ServiceIds
from app.llms.models import StreamChatLLM, ChatLLM
from app.pipelines.pipeline import ChatPipeline, StreamPipeline


class FinalResponse(StreamPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(
            self,
            task: str,
            info: str
    ) -> str:
        return f"""You are an AI assistant for institutions in Macedonia. Your job is to:
- To answer and perform task on administrative institutions strictly in Macedonia.
- Help retrieve information about administrative institutions.
- Perform actions like filling out forms, making payments, etc.

Given the task and the provided information give an answer in Macedonian. If there is no answer just say it. Only stick to the given information.

# Task: {task}

# Info: {info}

Response in Macedonian:"""

