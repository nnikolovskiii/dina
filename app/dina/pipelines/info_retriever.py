from typing import List

from app.dina.models.service_procedure import ServiceProcedure, ServiceType
from app.llms.models import StreamChatLLM
from app.pipelines.pipeline import ChatPipeline, StreamPipeline


class InfoRetriever(StreamPipeline):
    @property
    def response_type(self) -> str:
        return "str"

    def template(self, question: str, services: List[ServiceProcedure], service_types: List[ServiceType]) -> str:
        return f"""Given the below question answer it based only on the information provided in the context. Answer in Macedonian.

# Service Types:
{"\n".join([str(service_type) for service_type in service_types])}

# Services:
{"\n".join([str(service) for service in services])}

# Question: {question}

Response in Macedonian:"""


